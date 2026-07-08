"""Bulk flag resolution — read/write override_reason on job.merged_snapshot."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import JobStatus
from app.models.job import Job
from app.schemas.merge import FLAG_TYPE_LABELS, Flag, MergedJob
from app.services.jobs import _ensure_not_locked


class NoMergeSnapshotError(Exception):
    """Resolve called when job has no merged snapshot."""


class FlagResolutionError(Exception):
    """Invalid indices, empty reason, or flag already resolved."""


def flag_is_resolved(flag: Flag) -> bool:
    return bool(flag.override_reason and flag.override_reason.strip())


def all_flags_resolved(merged: MergedJob) -> bool:
    if not merged.flags:
        return True
    return all(flag_is_resolved(flag) for flag in merged.flags)


def status_after_resolution(merged: MergedJob) -> JobStatus:
    if all_flags_resolved(merged):
        return JobStatus.FLAGS_RESOLVED
    return JobStatus.MERGED


def reasons_from_snapshots(snapshots: list[dict | None], *, limit: int = 100) -> list[str]:
    """Collect distinct override reasons from snapshot dicts (testable without DB)."""
    seen: set[str] = set()
    for snapshot in snapshots:
        if snapshot is None:
            continue
        merged = MergedJob.model_validate(snapshot)
        for flag in merged.flags:
            if flag.override_reason:
                stripped = flag.override_reason.strip()
                if stripped:
                    seen.add(stripped)
    return sorted(seen)[:limit]


def list_past_override_reasons(db: Session, *, limit: int = 100) -> list[str]:
    stmt = select(Job.merged_snapshot).where(Job.merged_snapshot.isnot(None))
    snapshots = list(db.scalars(stmt).all())
    return reasons_from_snapshots(snapshots, limit=limit)


def list_overridden_flags(merged: MergedJob) -> list[dict[str, str]]:
    """Return read-only audit rows for flags with override reasons."""
    rows: list[dict[str, str]] = []
    for flag in sorted(merged.flags, key=lambda row: row.ap_name):
        if not flag.override_reason or not flag.override_reason.strip():
            continue
        rows.append(
            {
                "ap_name": flag.ap_name,
                "type_label": FLAG_TYPE_LABELS.get(flag.type, flag.type.value),
                "detail": flag.detail,
                "reason": flag.override_reason.strip(),
            },
        )
    return rows


def apply_override_reasons(
    merged: MergedJob,
    indices: list[int],
    reason: str,
) -> MergedJob:
    """Return a copy of merged with override_reason set on selected flags."""
    stripped = reason.strip()
    if not stripped:
        raise FlagResolutionError("Override reason is required.")

    if not indices:
        raise FlagResolutionError("Select at least one flag.")

    unique_indices = sorted(set(indices))
    flag_count = len(merged.flags)

    for index in unique_indices:
        if index < 0 or index >= flag_count:
            raise FlagResolutionError(f"Invalid flag index: {index}.")
        if flag_is_resolved(merged.flags[index]):
            raise FlagResolutionError(
                f"Flag at index {index} is already resolved.",
            )

    updated_flags = list(merged.flags)
    for index in unique_indices:
        flag = updated_flags[index]
        updated_flags[index] = flag.model_copy(update={"override_reason": stripped})

    return merged.model_copy(update={"flags": updated_flags})


def resolve_job_flags(
    db: Session,
    job: Job,
    flag_indices: list[int],
    override_reason: str,
) -> MergedJob:
    """Apply override reasons to selected flags and persist snapshot + status."""
    _ensure_not_locked(job)
    if job.merged_snapshot is None:
        raise NoMergeSnapshotError(
            "No merge snapshot on this job. Push merge before resolving flags.",
        )

    merged = MergedJob.model_validate(job.merged_snapshot)
    updated = apply_override_reasons(merged, flag_indices, override_reason)
    job.merged_snapshot = updated.model_dump(mode="json")
    job.status = status_after_resolution(updated)
    db.commit()
    db.refresh(job)
    return updated
