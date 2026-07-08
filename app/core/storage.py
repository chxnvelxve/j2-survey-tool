"""Storage abstraction. LocalStorage now; NextcloudStorage later — same interface.

NEVER call open()/build paths outside this module. All file IO goes through Storage.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO, Protocol

from app.core.config import settings


class StorageNotConfiguredError(Exception):
    """Storage backend selected but not configured or not yet implemented."""


class Storage(Protocol):
    def save(self, rel_path: str, fileobj: BinaryIO) -> str: ...
    def open(self, rel_path: str) -> BinaryIO: ...
    def url_for(self, rel_path: str) -> str: ...
    def delete(self, rel_path: str) -> None: ...
    def filesystem_path(self, rel_path: str) -> Path: ...


class LocalStorage:
    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root or settings.STORAGE_LOCAL_ROOT)

    def save(self, rel_path: str, fileobj: BinaryIO) -> str:
        dest = self.root / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as out:
            shutil.copyfileobj(fileobj, out)
        return rel_path

    def open(self, rel_path: str) -> BinaryIO:
        return (self.root / rel_path).open("rb")

    def url_for(self, rel_path: str) -> str:
        return f"/files/{rel_path}"

    def delete(self, rel_path: str) -> None:
        path = self.root / rel_path
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def filesystem_path(self, rel_path: str) -> Path:
        return self.root / rel_path


class NextcloudStorage:
    """Stub — full WebDAV impl blocked on Josh (docs/DECISIONS.md #12)."""

    def __init__(self) -> None:
        raise StorageNotConfiguredError(
            "Nextcloud storage is not configured. "
            "Waiting on Nextcloud access from Josh (docs/DECISIONS.md #12). "
            "Set STORAGE_BACKEND=local for now.",
        )


def get_storage() -> Storage:
    if settings.STORAGE_BACKEND == "nextcloud":
        return NextcloudStorage()
    return LocalStorage()
