"""Unit tests for centralized display labels."""
from __future__ import annotations

from app.core.labels import (
    approval_gate_label,
    generation_gate_label,
    job_status_label,
    readiness_block_reason,
)
from app.models.enums import JobStatus


def test_every_job_status_has_label() -> None:
    for status in JobStatus:
        label = job_status_label(status)
        assert label
        assert label != status.value


def test_job_status_label_accepts_string() -> None:
    assert job_status_label("draft_in_review") == job_status_label(JobStatus.DRAFT_IN_REVIEW)


def test_generation_gate_labels() -> None:
    assert generation_gate_label("merge_snapshot") == "Merge snapshot present"
    assert generation_gate_label("flags_resolved") == "All flags resolved or overridden"
    assert generation_gate_label("attachments_present") == "At least one attachment uploaded"
    assert generation_gate_label("status_allows_generation") == "Job status allows generation"


def test_approval_gate_labels() -> None:
    assert approval_gate_label("generation_gates") == (
        "Generation gates pass (merge, flags, attachments)"
    )
    assert approval_gate_label("status_draft_in_review") == "Status is draft in review"
    assert approval_gate_label("deliverable_generated") == "Deliverable generated"
    assert approval_gate_label("deliverable_on_storage") == "Deliverable file on storage"


def test_readiness_block_reason_static() -> None:
    assert readiness_block_reason("no_merge_snapshot") == (
        "Push merge before generating a report."
    )
    assert readiness_block_reason("already_approved") == "Job is already approved."


def test_readiness_block_reason_with_kwargs() -> None:
    msg = readiness_block_reason("wrong_status_other", status="inputs_uploaded")
    assert "inputs_uploaded" in msg
    msg = readiness_block_reason("template_missing", path="/app/missing.docx")
    assert "/app/missing.docx" in msg


def test_readiness_block_reason_none() -> None:
    assert readiness_block_reason(None) is None
