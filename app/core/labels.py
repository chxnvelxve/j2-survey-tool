"""Display labels for Job status, readiness gates, and block reasons.

Stable keys map to human-readable strings. When terminology is confirmed,
edit values here only — no enum or migration changes.
"""
from __future__ import annotations

from app.models.enums import JobStatus

JOB_STATUS_LABELS: dict[JobStatus, str] = {
    JobStatus.AWAITING_INPUTS: "Awaiting inputs",
    JobStatus.INPUTS_UPLOADED: "Inputs uploaded",
    JobStatus.MERGED: "Merged",
    JobStatus.FLAGS_RESOLVED: "Flags resolved",
    JobStatus.DRAFT_IN_REVIEW: "Draft in review",
    JobStatus.APPROVED: "Approved",
}

GENERATION_GATE_LABELS: dict[str, str] = {
    "merge_snapshot": "Merge snapshot present",
    "flags_resolved": "All flags resolved or overridden",
    "attachments_present": "At least one attachment uploaded",
    "status_allows_generation": "Job status allows generation",
    "template_ready": "Report template available",
}

APPROVAL_GATE_LABELS: dict[str, str] = {
    "generation_gates": "Generation gates pass (merge, flags, attachments)",
    "status_draft_in_review": "Status is draft in review",
    "deliverable_generated": "Deliverable generated",
    "deliverable_on_storage": "Deliverable file on storage",
}

READINESS_BLOCK_REASONS: dict[str, str] = {
    "no_merge_snapshot": "Push merge before generating a report.",
    "unresolved_flags": "Resolve or override all merge flags before generating.",
    "wrong_status_merged": "Resolve all merge flags before generating.",
    "wrong_status_other": (
        "Job status must be flags resolved or draft in review (current: {status})."
    ),
    "no_access_points": "No access points in merge snapshot.",
    "no_attachments": "Upload at least one attachment (IDF, LLD, etc.) before generating.",
    "template_missing": "Report template not found: {path}",
    "already_approved": "Job is already approved.",
    "not_draft_in_review": (
        "Generate a report before approving (status must be draft in review)."
    ),
    "no_deliverable_path": "No deliverable — generate a report first.",
    "no_generated_at": "No generation timestamp — regenerate the report.",
    "deliverable_missing_on_storage": (
        "Deliverable file not found on storage — regenerate the report."
    ),
    "generation_not_allowed": "Report generation is not allowed.",
    "approval_not_allowed": "Approval is not allowed.",
}


def job_status_label(status: JobStatus | str) -> str:
    if isinstance(status, str):
        status = JobStatus(status)
    return JOB_STATUS_LABELS.get(status, status.value)


def generation_gate_label(key: str) -> str:
    return GENERATION_GATE_LABELS.get(key, key)


def approval_gate_label(key: str) -> str:
    return APPROVAL_GATE_LABELS.get(key, key)


def readiness_block_reason(key: str | None, **kwargs: object) -> str | None:
    if key is None:
        return None
    template = READINESS_BLOCK_REASONS.get(key, key)
    if kwargs:
        return template.format(**kwargs)
    return template
