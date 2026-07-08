"""Typed inputs for the generator stage."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrandingConfig:
    company_name: str
    logo_path: Path | None
    primary_color: str


@dataclass(frozen=True)
class AttachmentInput:
    attachment_id: int
    filename: str
    path: Path
    content_type: str | None

    @property
    def is_image(self) -> bool:
        if self.content_type and self.content_type.startswith("image/"):
            return True
        suffix = self.path.suffix.lower()
        return suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
