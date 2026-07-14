"""Build docxtpl Jinja context from MergedJob and resolved assets.

Frozen context contract — see docs/template_map.md. Contract test fails if
documented keys disappear.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage

from app.schemas.merge import FLAG_TYPE_LABELS, MergedJob, MergedPhotoRef
from app.schemas.survey import SurveyRadio
from app.services.generator.errors import MissingPhotoFileError
from app.services.generator.profiles import SuccessCriteria, resolve_profile
from app.services.generator.types import AttachmentInput, BrandingConfig

logger = logging.getLogger(__name__)

PHOTO_WIDTH = Mm(55)
LOGO_WIDTH = Mm(40)

# 🟡 DRAFTED placeholders until Josh's sample deliverable arrives.
_EXEC_SUMMARY_PLACEHOLDER = (
    "This report documents wireless access point installation and survey results "
    "for the site named above. Detailed RF configuration and field photos follow. "
    "(Placeholder text — replace when Josh's sample deliverable arrives.)"
)
_SCOPE_METHODOLOGY_PLACEHOLDER = (
    "Survey scope and methodology will be drafted by the editor. "
    "Capture settings below are machine-fed from the job record. "
    "(Placeholder — replace when Josh's sample deliverable arrives.)"
)
_FINDINGS_PLACEHOLDER = (
    "Findings narrative will be drafted by the editor after reviewing survey "
    "data and field photos. Summary counts below are machine-fed. "
    "(Placeholder — RF pass/fail math is not computed in v1 shell.)"
)


def _resolve_logo(tpl: DocxTemplate, logo_path: Path | None) -> InlineImage | None:
    """Resolve the branded logo, warning (not silently dropping) on a bad path.

    A None path means no logo was configured — that is fine and silent. A
    configured path that does not resolve is a misconfiguration worth surfacing,
    so the report renders unbranded instead of failing, but logs a warning.
    """
    if logo_path is None:
        return None
    if logo_path.is_file():
        return InlineImage(tpl, str(logo_path), width=LOGO_WIDTH)
    logger.warning(
        "Configured brand logo path %s does not resolve; rendering report without logo.",
        logo_path,
    )
    return None


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


def _blank(value: str | None) -> str:
    if value is None or not str(value).strip():
        return "—"
    return str(value).strip()


def _prose_or_placeholder(value: str | None, placeholder: str) -> str:
    if value is not None and str(value).strip():
        return str(value).strip()
    return placeholder


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
    location_vertical: str | None = None,
    success_criteria_override: dict[str, Any] | None = None,
    survey_type: str | None = None,
    band_plan: str | None = None,
    site_metadata: str | None = None,
    exec_summary: str | None = None,
    scope_methodology: str | None = None,
    findings: str | None = None,
) -> dict[str, object]:
    logo = _resolve_logo(tpl, branding.logo_path)

    criteria: SuccessCriteria = resolve_profile(
        location_vertical,
        success_criteria_override,
    )

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

    ap_count = len(aps)
    override_count = len(overrides)

    return {
        "company_name": branding.company_name,
        "primary_color": branding.primary_color,
        "logo": logo,
        "job_name": job_name,
        "project_name": project_name,
        "survey_type": _blank(survey_type),
        "location_vertical": _blank(location_vertical),
        "band_plan": _blank(band_plan),
        "site_metadata": _blank(site_metadata),
        "success_criteria": criteria.as_context(),
        "exec_summary": _prose_or_placeholder(exec_summary, _EXEC_SUMMARY_PLACEHOLDER),
        "scope_methodology": _prose_or_placeholder(
            scope_methodology,
            _SCOPE_METHODOLOGY_PLACEHOLDER,
        ),
        "findings": _prose_or_placeholder(findings, _FINDINGS_PLACEHOLDER),
        "ap_count": ap_count,
        "override_count": override_count,
        "aps": aps,
        "attachments": attachment_rows,
        "overrides": overrides,
        "has_overrides": bool(overrides),
    }
