"""Generator stage: MergedJob + template + branding -> .docx bytes.
See .cursor/skills/docx-generator/SKILL.md.

Phase 5. docxtpl. Branding from config, never hardcoded.
"""
from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from pathlib import Path

from docxtpl import DocxTemplate

from app.schemas.merge import MergedJob
from app.services.generator.context import build_template_context
from app.services.generator.errors import (
    EmptyMergedJobError,
    MissingTemplateError,
    NoAttachmentsError,
    UnresolvedFlagsError,
)
from app.services.generator.types import AttachmentInput, BrandingConfig
from app.services.job_flag_resolution import all_flags_resolved


def _validate_inputs(
    merged: MergedJob,
    template_path: Path,
    attachments: list[AttachmentInput],
) -> None:
    if not template_path.is_file():
        raise MissingTemplateError(f"Template not found: {template_path}")
    if not merged.aps:
        raise EmptyMergedJobError("Cannot generate a report with no access points.")
    if not all_flags_resolved(merged):
        raise UnresolvedFlagsError(
            "All merge flags must be resolved or overridden before generating.",
        )
    if not attachments:
        raise NoAttachmentsError(
            "At least one attachment (IDF, LLD, etc.) is required before generating.",
        )


def generate_docx(
    merged: MergedJob,
    *,
    template_path: Path,
    branding: BrandingConfig,
    job_name: str,
    project_name: str,
    floor_name_for: Callable[[str | None], str],
    photo_paths: dict[int, Path],
    attachments: list[AttachmentInput],
) -> bytes:
    """Validate, build context, render docxtpl, return .docx bytes."""
    _validate_inputs(merged, template_path, attachments)

    tpl = DocxTemplate(str(template_path))
    context = build_template_context(
        tpl,
        merged,
        branding=branding,
        job_name=job_name,
        project_name=project_name,
        floor_name_for=floor_name_for,
        photo_paths=photo_paths,
        attachments=attachments,
    )
    tpl.render(context)

    buffer = BytesIO()
    tpl.save(buffer)
    return buffer.getvalue()
