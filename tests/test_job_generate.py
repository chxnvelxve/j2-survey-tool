"""Unit tests for report generation readiness."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from app.models.enums import JobStatus
from app.schemas.merge import Flag, FlagType, MergedAP, MergedAPStatus, MergedJob, MergedPhotoSlots
from app.schemas.survey import SurveyAP
from app.services.job_generate import generation_readiness

TEMPLATE = Path(__file__).resolve().parent.parent / "templates_docx" / "survey_report.docx"


def _job(
    *,
    status: JobStatus = JobStatus.FLAGS_RESOLVED,
    attachment_count: int = 1,
) -> MagicMock:
    job = MagicMock()
    job.status = status
    job.attachments = [MagicMock()] * attachment_count
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


def test_readiness_happy_path() -> None:
    ready, reason = generation_readiness(
        _job(),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is True
    assert reason is None


def test_readiness_no_snapshot() -> None:
    ready, reason = generation_readiness(_job(), None, template_path=TEMPLATE)
    assert ready is False
    assert reason is not None
    assert "merge" in reason.lower()


def test_readiness_unresolved_flags() -> None:
    merged = _merged(
        flags=[
            Flag(
                ap_name="AP-01",
                type=FlagType.MISSING_PHOTO,
                detail="Missing far",
            ),
        ],
    )
    ready, reason = generation_readiness(_job(status=JobStatus.MERGED), merged, template_path=TEMPLATE)
    assert ready is False
    assert "flag" in reason.lower()


def test_readiness_wrong_status() -> None:
    ready, reason = generation_readiness(
        _job(status=JobStatus.INPUTS_UPLOADED),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert reason is not None


def test_readiness_draft_in_review_allowed() -> None:
    ready, _reason = generation_readiness(
        _job(status=JobStatus.DRAFT_IN_REVIEW),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is True


def test_readiness_no_attachments() -> None:
    ready, reason = generation_readiness(
        _job(attachment_count=0),
        _merged(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert "attachment" in reason.lower()


def test_readiness_no_aps() -> None:
    ready, reason = generation_readiness(
        _job(),
        MergedJob(),
        template_path=TEMPLATE,
    )
    assert ready is False
    assert "access point" in reason.lower()


def test_readiness_missing_template(tmp_path: Path) -> None:
    ready, reason = generation_readiness(
        _job(),
        _merged(),
        template_path=tmp_path / "missing.docx",
    )
    assert ready is False
    assert "template" in reason.lower()
