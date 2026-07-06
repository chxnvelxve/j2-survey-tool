"""Storage abstraction. LocalStorage now; NextcloudStorage later — same interface.

NEVER call open()/build paths outside this module. All file IO goes through Storage.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO, Protocol

from app.core.config import settings


class Storage(Protocol):
    def save(self, rel_path: str, fileobj: BinaryIO) -> str: ...
    def open(self, rel_path: str) -> BinaryIO: ...
    def url_for(self, rel_path: str) -> str: ...


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


def get_storage() -> Storage:
    # Phase 6: branch on settings.STORAGE_BACKEND for NextcloudStorage.
    return LocalStorage()
