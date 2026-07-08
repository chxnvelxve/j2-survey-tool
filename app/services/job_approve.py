"""Approver sign-off — readiness gates and status transition to APPROVED."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.labels import readiness_block_reason
from app.core.storage import Storage
from app.models.enums import JobStatus
from app.models.job import Job
from app.schemas.merge import MergedJob
from app.services.job_flag_resolution import NoMergeSnapshotError
from app.services.job_generate import generation_readiness
from app.services.job_merge import merged_job_from_snapshot
from app.services.jobs import JobLockedError


class ApproveNotAllowedError(Exception):
    """Job is not in a state that allows approval."""


def approval_readiness(
    job: Job,
    merged: MergedJob | None,
    *,
    storage: Storage | None = None,
    template_path: Path | None = None,
) -> tuple[bool, str | None]:
    """Return (ready, block_reason_key). Composes generation_readiness with approval gates."""
    if job.status == JobStatus.APPROVED:
        return False, "already_approved"

    gen_ready, gen_reason = generation_readiness(job, merged, template_path=template_path)
    if not gen_ready:
        return False, gen_reason

    if job.status != JobStatus.DRAFT_IN_REVIEW:
        return False, "not_draft_in_review"

    if not job.deliverable_path:
        return False, "no_deliverable_path"

    if not job.generated_at:
        return False, "no_generated_at"

    if storage is not None:
        try:
            handle = storage.open(job.deliverable_path)
            handle.close()
        except OSError:
            return False, "deliverable_missing_on_storage"

    return True, None


def approve_job(
    db: Session,
    job: Job,
    *,
    approved_by: str | None = None,
    storage: Storage | None = None,
    template_path: Path | None = None,
) -> Job:
    """Approve a generated report. Sets status APPROVED with timestamp."""
    if job.status == JobStatus.APPROVED:
        raise JobLockedError("This job is already approved.")

    merged = merged_job_from_snapshot(job)
    if merged is None:
        raise NoMergeSnapshotError(
            "No merge snapshot on this job. Push merge before approving.",
        )

    ready, reason_key = approval_readiness(
        job,
        merged,
        storage=storage,
        template_path=template_path,
    )
    if not ready:
        msg = readiness_block_reason(reason_key)
        raise ApproveNotAllowedError(msg or readiness_block_reason("approval_not_allowed"))

    stripped_by = approved_by.strip() if approved_by else ""
    job.status = JobStatus.APPROVED
    job.approved_at = datetime.now(UTC)
    job.approved_by = stripped_by or None
    db.commit()
    db.refresh(job)
    return job
