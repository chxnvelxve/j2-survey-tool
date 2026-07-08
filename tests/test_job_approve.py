"""Unit tests for approval readiness, approve_job, and post-approve lock."""
from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.storage import LocalStorage
from app.models.enums import JobStatus
from app.schemas.merge import Flag, FlagType, MergedAP, MergedAPStatus, MergedJob, MergedPhotoSlots
from app.schemas.survey import SurveyAP
from app.services.job_approve import ApproveNotAllowedError, approval_readiness, approve_job
from app.services.job_flag_resolution import resolve_job_flags
from app.services.job_generate import generate_job_report
from app.services.job_merge import push_job_merge
from app.services.jobs import JobLockedError, upload_photo

TEMPLATE = Path(__file__).resolve().parent.parent / "templates_docx" / "survey_report.docx"


def _job(
    *,
    status: JobStatus = JobStatus.DRAFT_IN_REVIEW,
    attachment_count: int = 1,
    deliverable_path: str | None = "jobs/1/output/report.docx",
    generated_at: datetime | None | object = ...,
) -> MagicMock:
    job = MagicMock()
    job.status = status
    job.attachments = [MagicMock()] * attachment_count
    job.deliverable_path = deliverable_path
    if generated_at is ...:
        job.generated_at = datetime.now(UTC)
    else:
        job.generated_at = generated_at
    job.merged_snapshot = {}
    job.id = 1
    return job


def _merged(*, flags: list[Flag] | None = None, ap_count: int = 1) -> MergedJob:
    aps = [
        MergedAP(
            ap_name=f"AP-{i:02d}",
            survey_data=SurveyAP(name=f"AP-{i:02d}"),
            photos=MergedPhotoSlots(),
            status=MergedAPStatus.MATCHED,
        )
        for i in range(ap_count)
    ]
    return MergedJob(aps=aps, flags=flags or [])


class _MockStorage:
    def __init__(self, *, exists: bool = True) -> None:
        self._exists = exists

    def open(self, rel_path: str) -> BytesIO:
        if not self._exists:
            raise OSError("not found")
        return BytesIO(b"docx")


def test_approval_readiness_happy_path(tmp_path: Path) -> None:
    storage = LocalStorage(root=str(tmp_path))
    rel = "jobs/1/output/report.docx"
    dest = tmp_path / rel
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"docx")

    ready, reason = approval_readiness(
        _job(),
        _merged(),
        storage=storage,
        template_path=TEMPLATE,
    )
    assert ready is True
    assert reason is None


def test_approval_readiness_not_draft_in_review() -> None:
    ready, reason = approval_readiness(
        _job(status=JobStatus.FLAGS_RESOLVED),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert reason is not None
    assert "draft in review" in reason.lower()


def test_approval_readiness_no_deliverable() -> None:
    ready, reason = approval_readiness(
        _job(deliverable_path=None),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert "deliverable" in reason.lower()


def test_approval_readiness_no_generated_at() -> None:
    ready, reason = approval_readiness(
        _job(generated_at=None),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert "generation" in reason.lower()


def test_approval_readiness_unresolved_flags() -> None:
    merged = _merged(
        flags=[
            Flag(ap_name="AP-01", type=FlagType.MISSING_PHOTO, detail="Missing far"),
        ],
    )
    ready, reason = approval_readiness(
        _job(status=JobStatus.MERGED),
        merged,
        template_path=TEMPLATE,
    )
    assert ready is False
    assert reason is not None


def test_approval_readiness_already_approved() -> None:
    ready, reason = approval_readiness(
        _job(status=JobStatus.APPROVED),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert "already approved" in reason.lower()


def test_approval_readiness_missing_storage_file() -> None:
    storage = _MockStorage(exists=False)
    ready, reason = approval_readiness(
        _job(),
        _merged(),
        storage=storage,
        template_path=TEMPLATE,
    )
    assert ready is False
    assert "storage" in reason.lower()


def test_approve_job_sets_fields() -> None:
    job = _job()
    merged = _merged()
    db = MagicMock()
    storage = _MockStorage()

    with patch("app.services.job_approve.merged_job_from_snapshot", return_value=merged):
        with patch("app.services.job_approve.approval_readiness", return_value=(True, None)):
            result = approve_job(db, job, approved_by="  Josh  ", storage=storage)

    assert result.status == JobStatus.APPROVED
    assert result.approved_by == "Josh"
    assert result.approved_at is not None
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(job)


def test_approve_job_not_allowed() -> None:
    job = _job()
    merged = _merged()
    db = MagicMock()

    with patch("app.services.job_approve.merged_job_from_snapshot", return_value=merged):
        with patch(
            "app.services.job_approve.approval_readiness",
            return_value=(False, "Not ready"),
        ):
            with pytest.raises(ApproveNotAllowedError, match="Not ready"):
                approve_job(db, job, storage=_MockStorage())


def test_approve_job_already_approved() -> None:
    job = _job(status=JobStatus.APPROVED)
    db = MagicMock()

    with pytest.raises(JobLockedError, match="already approved"):
        approve_job(db, job, storage=_MockStorage())


def test_upload_photo_locked() -> None:
    job = MagicMock()
    job.status = JobStatus.APPROVED

    with pytest.raises(JobLockedError):
        upload_photo(MagicMock(), MagicMock(), job, MagicMock(), "AP-01", MagicMock())


def test_push_merge_locked() -> None:
    job = MagicMock()
    job.status = JobStatus.APPROVED

    with pytest.raises(JobLockedError):
        push_job_merge(MagicMock(), MagicMock(), job)


def test_resolve_flags_locked() -> None:
    job = MagicMock()
    job.status = JobStatus.APPROVED
    job.merged_snapshot = _merged().model_dump(mode="json")

    with pytest.raises(JobLockedError):
        resolve_job_flags(MagicMock(), job, [0], "reason")


def test_generate_locked() -> None:
    job = MagicMock()
    job.status = JobStatus.APPROVED

    with pytest.raises(JobLockedError):
        generate_job_report(MagicMock(), MagicMock(), job)
