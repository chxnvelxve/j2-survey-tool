"""Orchestrate report generation: load assets, call generator, persist deliverable."""
from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.labels import readiness_block_reason
from app.core.storage import Storage
from app.models.enums import JobStatus
from app.models.job import Job
from app.schemas.merge import MergedJob
from app.schemas.survey import floor_name_for
from app.services.generator.errors import GeneratorError
from app.services.generator.generator import generate_docx
from app.services.generator.types import AttachmentInput, BrandingConfig
from app.services.job_flag_resolution import NoMergeSnapshotError, all_flags_resolved
from app.services.job_merge import merged_job_from_snapshot
from app.services.jobs import _ensure_not_locked
from app.services.survey_parse import parse_job_surveys

GENERATABLE_STATUSES = frozenset({JobStatus.FLAGS_RESOLVED, JobStatus.DRAFT_IN_REVIEW})

DELIVERABLE_FILENAME = "report.docx"


class GenerateNotAllowedError(Exception):
    """Job is not in a state that allows report generation."""


def _abs_path(storage: Storage, rel_path: str) -> Path:
    return storage.filesystem_path(rel_path)


def _project_name_from_parsed(parsed_surveys: list) -> str:
    for parsed in parsed_surveys:
        if parsed.survey is not None:
            return parsed.survey.project.name
    return "—"


def _floor_lookup(parsed_surveys: list):
    surveys = [p.survey for p in parsed_surveys if p.survey is not None]

    def floor_name_for_id(floor_id: str | None) -> str:
        if not surveys:
            return "—"
        return floor_name_for(surveys[0], floor_id)

    def merged_floor_for(ap_name: str) -> str:
        for parsed in parsed_surveys:
            if parsed.survey is None:
                continue
            for ap in parsed.survey.aps:
                if ap.name == ap_name:
                    return floor_name_for(parsed.survey, ap.floor_id)
        return "—"

    return floor_name_for_id, merged_floor_for


def generation_readiness(
    job: Job,
    merged: MergedJob | None,
    *,
    template_path: Path | None = None,
) -> tuple[bool, str | None]:
    """Return (ready, block_reason_key). Pure check for UI and orchestration."""
    template = template_path or Path(settings.DOCX_TEMPLATE_PATH)

    if merged is None:
        return False, "no_merge_snapshot"
    if job.status not in GENERATABLE_STATUSES:
        if job.status == JobStatus.MERGED:
            return False, "wrong_status_merged"
        return False, "wrong_status_other"
    if not all_flags_resolved(merged):
        return False, "unresolved_flags"
    if not merged.aps:
        return False, "no_access_points"
    if not job.attachments:
        return False, "no_attachments"
    if not template.is_file():
        return False, "template_missing"
    return True, None


def _branding_config() -> BrandingConfig:
    # Pass the configured path through as-is; the generator resolves it and warns
    # if it does not exist (rather than silently dropping the logo here).
    raw_logo_path = settings.BRAND_LOGO_PATH.strip()
    return BrandingConfig(
        company_name=settings.BRAND_COMPANY_NAME,
        logo_path=Path(raw_logo_path) if raw_logo_path else None,
        primary_color=settings.BRAND_PRIMARY_COLOR,
    )


def _photo_paths(job: Job, storage: Storage) -> dict[int, Path]:
    return {photo.id: _abs_path(storage, photo.storage_path) for photo in job.photos}


def _attachment_inputs(job: Job, storage: Storage) -> list[AttachmentInput]:
    return [
        AttachmentInput(
            attachment_id=att.id,
            filename=att.original_filename,
            path=_abs_path(storage, att.storage_path),
            content_type=att.content_type,
        )
        for att in job.attachments
    ]


def deliverable_rel_path(job_id: int) -> str:
    return f"jobs/{job_id}/output/{DELIVERABLE_FILENAME}"


def generate_job_report(db: Session, storage: Storage, job: Job) -> str:
    """Generate .docx deliverable, persist path + status, return storage rel_path."""
    _ensure_not_locked(job)
    merged = merged_job_from_snapshot(job)
    if merged is None:
        raise NoMergeSnapshotError(
            "No merge snapshot on this job. Push merge before generating.",
        )

    ready, reason_key = generation_readiness(job, merged)
    if not ready:
        template = Path(settings.DOCX_TEMPLATE_PATH)
        msg = readiness_block_reason(
            reason_key,
            status=job.status.value,
            path=template,
        )
        raise GenerateNotAllowedError(msg or readiness_block_reason("generation_not_allowed"))

    parsed_surveys = parse_job_surveys(db, storage, job)
    project_name = _project_name_from_parsed(parsed_surveys)
    floor_name_for_id, _ = _floor_lookup(parsed_surveys)

    try:
        docx_bytes = generate_docx(
            merged,
            template_path=Path(settings.DOCX_TEMPLATE_PATH),
            branding=_branding_config(),
            job_name=job.name,
            project_name=project_name,
            floor_name_for=floor_name_for_id,
            photo_paths=_photo_paths(job, storage),
            attachments=_attachment_inputs(job, storage),
            location_vertical=job.location_vertical,
            success_criteria_override=job.success_criteria_override,
            survey_type=job.survey_type,
            band_plan=job.band_plan,
            site_metadata=job.site_metadata,
            exec_summary=job.exec_summary,
            scope_methodology=job.scope_methodology,
            findings=job.findings,
        )
    except GeneratorError:
        raise

    rel_path = deliverable_rel_path(job.id)
    storage.save(rel_path, BytesIO(docx_bytes))

    job.deliverable_path = rel_path
    job.generated_at = datetime.now(UTC)
    job.status = JobStatus.DRAFT_IN_REVIEW
    db.commit()
    db.refresh(job)
    return rel_path
