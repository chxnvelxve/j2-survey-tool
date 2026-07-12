"""Storage abstraction. LocalStorage default; NextcloudStorage via WebDAV.

NEVER call open()/build paths outside this module. All file IO goes through Storage.
"""
from __future__ import annotations

import shutil
import tempfile
from collections.abc import Generator
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Protocol
from urllib.parse import quote

import httpx

from app.core.config import settings

_MISSING_CREDS_MSG = (
    "STORAGE_BACKEND=nextcloud requires NEXTCLOUD_URL, NEXTCLOUD_USERNAME, "
    "and NEXTCLOUD_PASSWORD. Set those env vars, or use STORAGE_BACKEND=local. "
    "Do not fall back silently — a misconfigured production deploy must fail loudly. "
    "Live activation waits on Nextcloud access from Josh (docs/DECISIONS.md #12)."
)


class StorageNotConfiguredError(Exception):
    """Storage backend selected but not configured or not yet implemented."""


class Storage(Protocol):
    def save(self, rel_path: str, fileobj: BinaryIO) -> str: ...
    def open(self, rel_path: str) -> BinaryIO: ...
    def url_for(self, rel_path: str) -> str: ...
    def delete(self, rel_path: str) -> None: ...
    def filesystem_path(self, rel_path: str) -> Path: ...


def validate_rel_path(rel_path: str) -> str:
    """Normalize and reject empty, absolute, dot-segment, and parent-traversal paths.

    Returns a cleaned relative path using forward slashes.
    Splits manually (does not use Path normalization) so ``.`` / ``..`` are caught.
    """
    if rel_path is None or not str(rel_path).strip():
        raise ValueError("rel_path must not be empty")

    raw = str(rel_path).replace("\\", "/").strip()
    if raw.startswith("/") or raw.startswith("~"):
        raise ValueError(f"rel_path must be relative, not absolute: {rel_path!r}")
    # Windows drive / UNC
    if len(raw) >= 2 and raw[1] == ":":
        raise ValueError(f"rel_path must be relative, not absolute: {rel_path!r}")
    if raw.startswith("//"):
        raise ValueError(f"rel_path must be relative, not absolute: {rel_path!r}")

    parts = raw.split("/")
    if not parts or all(p == "" for p in parts):
        raise ValueError("rel_path must not be empty")
    cleaned: list[str] = []
    for part in parts:
        if part == "":
            # Collapse duplicate slashes; do not treat as a segment.
            continue
        if part in (".", ".."):
            raise ValueError(
                f"rel_path must not contain '.' or '..' segments: {rel_path!r}",
            )
        cleaned.append(part)

    if not cleaned:
        raise ValueError("rel_path must not be empty")
    return "/".join(cleaned)


class LocalStorage:
    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root or settings.STORAGE_LOCAL_ROOT)

    def save(self, rel_path: str, fileobj: BinaryIO) -> str:
        rel_path = validate_rel_path(rel_path)
        dest = self.root / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as out:
            shutil.copyfileobj(fileobj, out)
        return rel_path

    def open(self, rel_path: str) -> BinaryIO:
        rel_path = validate_rel_path(rel_path)
        return (self.root / rel_path).open("rb")

    def url_for(self, rel_path: str) -> str:
        rel_path = validate_rel_path(rel_path)
        return f"/files/{rel_path}"

    def delete(self, rel_path: str) -> None:
        rel_path = validate_rel_path(rel_path)
        path = self.root / rel_path
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def filesystem_path(self, rel_path: str) -> Path:
        rel_path = validate_rel_path(rel_path)
        return self.root / rel_path


class NextcloudStorage:
    """WebDAV-backed storage against a Nextcloud instance.

    Shell is buildable now; live creds activation is blocked on Josh (#12).
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        webdav_root: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        url = (base_url if base_url is not None else settings.NEXTCLOUD_URL).strip()
        user = (username if username is not None else settings.NEXTCLOUD_USERNAME).strip()
        pwd = (password if password is not None else settings.NEXTCLOUD_PASSWORD).strip()
        root = (
            webdav_root
            if webdav_root is not None
            else settings.NEXTCLOUD_WEBDAV_ROOT
        ).strip().strip("/")

        if not url or not user or not pwd:
            raise StorageNotConfiguredError(_MISSING_CREDS_MSG)

        self._base_url = url.rstrip("/")
        self._username = user
        self._password = pwd
        self._webdav_root = root
        self._owns_client = client is None
        self._client = client or httpx.Client(
            auth=(user, pwd),
            timeout=60.0,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> NextcloudStorage:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _dav_prefix(self) -> str:
        user_seg = quote(self._username, safe="")
        prefix = f"{self._base_url}/remote.php/dav/files/{user_seg}"
        if self._webdav_root:
            root_segs = "/".join(
                quote(part, safe="") for part in PurePosixPath(self._webdav_root).parts
            )
            return f"{prefix}/{root_segs}"
        return prefix

    def _object_url(self, rel_path: str) -> str:
        cleaned = validate_rel_path(rel_path)
        segs = "/".join(quote(part, safe="") for part in PurePosixPath(cleaned).parts)
        return f"{self._dav_prefix()}/{segs}"

    def url_for(self, rel_path: str) -> str:
        return self._object_url(rel_path)

    def _ensure_parent_collections(self, rel_path: str) -> None:
        cleaned = validate_rel_path(rel_path)
        parent = PurePosixPath(cleaned).parent
        if str(parent) in (".", ""):
            return
        cumulative: list[str] = []
        for part in parent.parts:
            cumulative.append(part)
            col_path = "/".join(cumulative)
            url = self._object_url(col_path)
            response = self._client.request("MKCOL", url)
            # 201 created; 405 already exists; 409 parent missing (shouldn't if ordered)
            if response.status_code in (201, 405, 301, 302):
                continue
            if response.status_code == 409:
                continue
            response.raise_for_status()

    def save(self, rel_path: str, fileobj: BinaryIO) -> str:
        rel_path = validate_rel_path(rel_path)
        self._ensure_parent_collections(rel_path)
        data = fileobj.read()
        response = self._client.put(self._object_url(rel_path), content=data)
        response.raise_for_status()
        return rel_path

    def open(self, rel_path: str) -> BinaryIO:
        rel_path = validate_rel_path(rel_path)
        response = self._client.get(self._object_url(rel_path))
        if response.status_code == 404:
            raise FileNotFoundError(f"Nextcloud object not found: {rel_path}")
        response.raise_for_status()
        return BytesIO(response.content)

    def delete(self, rel_path: str) -> None:
        rel_path = validate_rel_path(rel_path)
        response = self._client.delete(self._object_url(rel_path))
        if response.status_code == 404:
            return
        response.raise_for_status()

    def filesystem_path(self, rel_path: str) -> Path:
        rel_path = validate_rel_path(rel_path)
        with self.open(rel_path) as handle:
            data = handle.read()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(rel_path).suffix)
        try:
            tmp.write(data)
            tmp.flush()
        finally:
            tmp.close()
        return Path(tmp.name)


def get_storage() -> Generator[Storage, None, None]:
    """Request-scoped storage. Closes owned Nextcloud httpx clients after the request."""
    if settings.STORAGE_BACKEND == "nextcloud":
        storage: Storage = NextcloudStorage()
    else:
        storage = LocalStorage()
    try:
        yield storage
    finally:
        if isinstance(storage, NextcloudStorage):
            storage.close()
