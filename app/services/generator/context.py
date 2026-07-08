"""Build docxtpl Jinja context from MergedJob and resolved assets."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage

from app.schemas.merge import FLAG_TYPE_LABELS, MergedJob, MergedPhotoRef
from app.schemas.survey import SurveyRadio
from app.services.generator.errors import MissingPhotoFileError
from app.services.generator.types import AttachmentInput, BrandingConfig

PHOTO_WIDTH = Mm(55)
LOGO_WIDTH = Mm(40)


def _radio_label(radio: SurveyRadio) -> str:
    parts = [radio.band]
    if radio.channel is not None:
        parts.append(f"ch{radio.channel}")
    if radio.tx_power is not None:
        parts.append(f"@{radio.tx_power} dBm")
    return " ".join(parts)


def _resolve_photo(
    tpl: DocxTemplate,
    ref: MergedPhotoRef | None,
    photo_paths: dict[int, Path],
) -> tuple[InlineImage | None, str | None]:
    if ref is None:
        return None, None
    path = photo_paths.get(ref.photo_id)
    if path is None or not path.is_file():
        raise MissingPhotoFileError(
            f"Photo {ref.photo_id} ({ref.original_filename}) is missing or unreadable.",
        )
    return InlineImage(tpl, str(path), width=PHOTO_WIDTH), ref.original_filename


def build_template_context(
    tpl: DocxTemplate,
    merged: MergedJob,
    *,
    branding: BrandingConfig,
    job_name: str,
    project_name: str,
    floor_name_for: Callable[[str | None], str],
    photo_paths: dict[int, Path],
    attachments: list[AttachmentInput],
) -> dict[str, object]:
    logo: InlineImage | None = None
    if branding.logo_path is not None and branding.logo_path.is_file():
        logo = InlineImage(tpl, str(branding.logo_path), width=LOGO_WIDTH)

    aps: list[dict[str, object]] = []
    for ap in sorted(merged.aps, key=lambda row: row.ap_name):
        photo_close, close_label = _resolve_photo(tpl, ap.photos.close, photo_paths)
        photo_far, far_label = _resolve_photo(tpl, ap.photos.far, photo_paths)
        aps.append(
            {
                "name": ap.ap_name,
                "model": ap.survey_data.model or "—",
                "vendor": ap.survey_data.vendor or "—",
                "floor": floor_name_for(ap.survey_data.floor_id),
                "x": ap.survey_data.x,
                "y": ap.survey_data.y,
                "radios": [
                    {
                        "band": radio.band,
                        "channel": radio.channel,
                        "tx_power": radio.tx_power,
                    }
                    for radio in ap.survey_data.radios
                ],
                "radios_summary": ", ".join(
                    _radio_label(radio) for radio in ap.survey_data.radios
                )
                or "—",
                "status": ap.status.value,
                "photo_close": photo_close,
                "photo_far": photo_far,
                "photo_close_label": close_label or "Not provided",
                "photo_far_label": far_label or "Not provided",
            },
        )

    attachment_rows: list[dict[str, object]] = []
    for att in sorted(attachments, key=lambda row: row.filename):
        image: InlineImage | None = None
        if att.is_image and att.path.is_file():
            image = InlineImage(tpl, str(att.path), width=PHOTO_WIDTH)
        attachment_rows.append(
            {
                "filename": att.filename,
                "image": image,
                "is_image": att.is_image,
            },
        )

    overrides: list[dict[str, str]] = []
    for flag in sorted(merged.flags, key=lambda row: row.ap_name):
        if not flag.override_reason or not flag.override_reason.strip():
            continue
        overrides.append(
            {
                "ap_name": flag.ap_name,
                "type_label": FLAG_TYPE_LABELS.get(flag.type, flag.type.value),
                "detail": flag.detail,
                "reason": flag.override_reason.strip(),
            },
        )

    return {
        "company_name": branding.company_name,
        "primary_color": branding.primary_color,
        "logo": logo,
        "job_name": job_name,
        "project_name": project_name,
        "aps": aps,
        "attachments": attachment_rows,
        "overrides": overrides,
        "has_overrides": bool(overrides),
    }
