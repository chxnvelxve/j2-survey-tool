"""NextcloudStorage WebDAV shell — mocked HTTP only (no live creds)."""
from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

import httpx
import pytest
import respx

from app.core.storage import (
    LocalStorage,
    NextcloudStorage,
    StorageNotConfiguredError,
    get_storage,
    validate_rel_path,
)

REJECTED_PATHS = [
    "",
    "   ",
    "/etc/passwd",
    "C:/Windows/system32",
    "jobs/1/../other.bin",
    "jobs/./secret.bin",
    "../escape.bin",
    "jobs/1/../../etc/passwd",
]

BASE = "https://nextcloud.example.com"
USER = "survey-bot"
PASSWORD = "app-password"
ROOT = "j2-survey"
DAV_PREFIX = f"{BASE}/remote.php/dav/files/{USER}/{ROOT}"


def _storage(**kwargs) -> NextcloudStorage:
    defaults = {
        "base_url": BASE,
        "username": USER,
        "password": PASSWORD,
        "webdav_root": ROOT,
    }
    defaults.update(kwargs)
    return NextcloudStorage(**defaults)


def test_missing_creds_raises() -> None:
    with pytest.raises(StorageNotConfiguredError, match="NEXTCLOUD_URL"):
        NextcloudStorage(base_url="", username=USER, password=PASSWORD)

    with pytest.raises(StorageNotConfiguredError, match="NEXTCLOUD_USERNAME"):
        NextcloudStorage(base_url=BASE, username="", password=PASSWORD)

    with pytest.raises(StorageNotConfiguredError, match="NEXTCLOUD_PASSWORD"):
        NextcloudStorage(base_url=BASE, username=USER, password="")


def test_url_for_shape() -> None:
    storage = _storage()
    assert storage.url_for("jobs/1/output/report.docx") == (
        f"{DAV_PREFIX}/jobs/1/output/report.docx"
    )


@respx.mock
def test_save_puts_and_mkcol_parents() -> None:
    mkcol_jobs = respx.route(method="MKCOL", url=f"{DAV_PREFIX}/jobs").mock(
        return_value=httpx.Response(201),
    )
    mkcol_nested = respx.route(method="MKCOL", url=f"{DAV_PREFIX}/jobs/1").mock(
        return_value=httpx.Response(201),
    )
    mkcol_output = respx.route(method="MKCOL", url=f"{DAV_PREFIX}/jobs/1/output").mock(
        return_value=httpx.Response(405),  # already exists
    )
    put = respx.put(f"{DAV_PREFIX}/jobs/1/output/report.docx").mock(
        return_value=httpx.Response(201),
    )

    storage = _storage()
    result = storage.save("jobs/1/output/report.docx", BytesIO(b"docx-bytes"))

    assert result == "jobs/1/output/report.docx"
    assert mkcol_jobs.called
    assert mkcol_nested.called
    assert mkcol_output.called
    assert put.called
    assert put.calls.last.request.content == b"docx-bytes"


@respx.mock
def test_open_returns_bytes() -> None:
    respx.get(f"{DAV_PREFIX}/jobs/1/photo.jpg").mock(
        return_value=httpx.Response(200, content=b"jpeg-data"),
    )
    storage = _storage()
    with storage.open("jobs/1/photo.jpg") as handle:
        assert handle.read() == b"jpeg-data"


@respx.mock
def test_open_missing_raises_file_not_found() -> None:
    respx.get(f"{DAV_PREFIX}/missing.bin").mock(
        return_value=httpx.Response(404),
    )
    storage = _storage()
    with pytest.raises(FileNotFoundError, match="missing.bin"):
        storage.open("missing.bin")


@respx.mock
def test_delete_tolerates_404() -> None:
    respx.delete(f"{DAV_PREFIX}/gone.bin").mock(
        return_value=httpx.Response(404),
    )
    storage = _storage()
    storage.delete("gone.bin")  # does not raise


@respx.mock
def test_delete_raises_on_server_error() -> None:
    respx.delete(f"{DAV_PREFIX}/locked.bin").mock(
        return_value=httpx.Response(500),
    )
    storage = _storage()
    with pytest.raises(httpx.HTTPStatusError):
        storage.delete("locked.bin")


@respx.mock
def test_filesystem_path_downloads_to_temp() -> None:
    respx.get(f"{DAV_PREFIX}/jobs/1/photo.jpg").mock(
        return_value=httpx.Response(200, content=b"temp-jpeg"),
    )
    storage = _storage()
    path = storage.filesystem_path("jobs/1/photo.jpg")
    try:
        assert path.exists()
        assert path.read_bytes() == b"temp-jpeg"
        assert path.suffix == ".jpg"
    finally:
        path.unlink(missing_ok=True)


def test_get_storage_local_default() -> None:
    with patch("app.core.storage.settings") as mock_settings:
        mock_settings.STORAGE_BACKEND = "local"
        mock_settings.STORAGE_LOCAL_ROOT = "/tmp/storage-test"
        storage = get_storage()
    assert isinstance(storage, LocalStorage)


def test_get_storage_nextcloud_missing_creds() -> None:
    with patch("app.core.storage.settings") as mock_settings:
        mock_settings.STORAGE_BACKEND = "nextcloud"
        mock_settings.NEXTCLOUD_URL = ""
        mock_settings.NEXTCLOUD_USERNAME = ""
        mock_settings.NEXTCLOUD_PASSWORD = ""
        mock_settings.NEXTCLOUD_WEBDAV_ROOT = ""
        with pytest.raises(StorageNotConfiguredError):
            get_storage()


@pytest.mark.parametrize("bad_path", REJECTED_PATHS)
def test_validate_rel_path_rejects(bad_path: str) -> None:
    with pytest.raises(ValueError):
        validate_rel_path(bad_path)


def test_validate_rel_path_accepts_normal() -> None:
    assert validate_rel_path("jobs/1/output/report.docx") == "jobs/1/output/report.docx"
    assert validate_rel_path(r"jobs\1\photo.jpg") == "jobs/1/photo.jpg"


@pytest.mark.parametrize("bad_path", REJECTED_PATHS)
def test_local_storage_rejects_bad_paths(tmp_path, bad_path: str) -> None:
    storage = LocalStorage(root=str(tmp_path))
    with pytest.raises(ValueError):
        storage.url_for(bad_path)
    with pytest.raises(ValueError):
        storage.filesystem_path(bad_path)
    with pytest.raises(ValueError):
        storage.open(bad_path)
    with pytest.raises(ValueError):
        storage.save(bad_path, BytesIO(b"x"))
    with pytest.raises(ValueError):
        storage.delete(bad_path)


@pytest.mark.parametrize(
    "bad_path",
    [
        "jobs/1/../other.bin",
        "/etc/passwd",
        "jobs/./secret.bin",
        "",
    ],
)
def test_nextcloud_storage_rejects_bad_paths(bad_path: str) -> None:
    storage = _storage()
    with pytest.raises(ValueError):
        storage.url_for(bad_path)
    with pytest.raises(ValueError):
        storage.open(bad_path)
    with pytest.raises(ValueError):
        storage.save(bad_path, BytesIO(b"x"))
    with pytest.raises(ValueError):
        storage.delete(bad_path)
    with pytest.raises(ValueError):
        storage.filesystem_path(bad_path)
