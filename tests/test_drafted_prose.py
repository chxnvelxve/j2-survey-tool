"""Phase 13d — editable DRAFTED prose overrides."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from docxtpl import DocxTemplate

from app.models.enums import JobStatus
from app.schemas.job import JobProseUpdate
from app.schemas.merge import (
    MergedAP,
    MergedAPStatus,
    MergedJob,
    MergedPhotoRef,
    MergedPhotoSlots,
)
from app.schemas.survey import SurveyAP, SurveyRadio
from app.services.generator.context import (
    _EXEC_SUMMARY_PLACEHOLDER,
    _FINDINGS_PLACEHOLDER,
    _SCOPE_METHODOLOGY_PLACEHOLDER,
    build_template_context,
)
from app.services.generator.types import AttachmentInput, BrandingConfig
from app.services.jobs import JobLockedError, update_job_prose

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates_docx" / "survey_report.docx"
FIXTURES = Path(__file__).parent / "fixtures"
PHOTO_CLOSE = FIXTURES / "gen_photo_close.png"
PHOTO_FAR = FIXTURES / "gen_photo_far.png"


def _ensure_photos() -> None:
    if not PHOTO_CLOSE.exists():
        from tests.fixtures.build_gen_photos import MINIMAL_PNG

        PHOTO_CLOSE.write_bytes(MINIMAL_PNG)
        PHOTO_FAR.write_bytes(MINIMAL_PNG)


def _merged() -> MergedJob:
    return MergedJob(
        aps=[
            MergedAP(
                ap_name="AP-01-NE",
                survey_data=SurveyAP(
                    name="AP-01-NE",
                    model="C9136I",
                    vendor="Cisco",
                    floor_id="fp1",
                    x=1.0,
                    y=2.0,
                    radios=[SurveyRadio(band="5GHz", channel=36, tx_power=17.0)],
                ),
                photos=MergedPhotoSlots(
                    close=MergedPhotoRef(photo_id=1, original_filename="close.png"),
                    far=MergedPhotoRef(photo_id=2, original_filename="far.png"),
                ),
                status=MergedAPStatus.MATCHED,
            ),
        ],
        flags=[],
    )


def _attachments(tmp_path: Path) -> list[AttachmentInput]:
    from tests.fixtures.build_gen_photos import MINIMAL_PNG

    path = tmp_path / "idf.png"
    path.write_bytes(MINIMAL_PNG)
    return [
        AttachmentInput(
            attachment_id=1,
            filename="idf.png",
            path=path,
            content_type="image/png",
        ),
    ]


def _ctx(
    tmp_path: Path,
    *,
    exec_summary: str | None = None,
    scope_methodology: str | None = None,
    findings: str | None = None,
) -> dict[str, object]:
    _ensure_photos()
    tpl = DocxTemplate(str(TEMPLATE))
    return build_template_context(
        tpl,
        _merged(),
        branding=BrandingConfig(
            company_name="Test Co",
            logo_path=None,
            primary_color="#1F4E79",
        ),
        job_name="Job",
        project_name="Project",
        floor_name_for=lambda _fid: "Floor 1",
        photo_paths={1: PHOTO_CLOSE, 2: PHOTO_FAR},
        attachments=_attachments(tmp_path),
        exec_summary=exec_summary,
        scope_methodology=scope_methodology,
        findings=findings,
    )


def test_context_falls_back_to_placeholders_when_prose_empty(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path, exec_summary=None, scope_methodology="  ", findings="")
    assert ctx["exec_summary"] == _EXEC_SUMMARY_PLACEHOLDER
    assert ctx["scope_methodology"] == _SCOPE_METHODOLOGY_PLACEHOLDER
    assert ctx["findings"] == _FINDINGS_PLACEHOLDER


def test_context_prefers_job_prose_when_set(tmp_path: Path) -> None:
    ctx = _ctx(
        tmp_path,
        exec_summary="  Custom exec  ",
        scope_methodology="Custom scope",
        findings="Custom findings",
    )
    assert ctx["exec_summary"] == "Custom exec"
    assert ctx["scope_methodology"] == "Custom scope"
    assert ctx["findings"] == "Custom findings"


def test_update_job_prose_round_trip() -> None:
    job = MagicMock()
    job.status = JobStatus.FLAGS_RESOLVED
    job.exec_summary = None
    job.scope_methodology = None
    job.findings = None
    db = MagicMock()

    update_job_prose(
        db,
        job,
        JobProseUpdate(
            exec_summary="Exec",
            scope_methodology="Scope",
            findings="Findings",
        ),
    )

    assert job.exec_summary == "Exec"
    assert job.scope_methodology == "Scope"
    assert job.findings == "Findings"
    db.commit.assert_called_once()


def test_update_job_prose_blank_clears_to_none() -> None:
    job = MagicMock()
    job.status = JobStatus.DRAFT_IN_REVIEW
    db = MagicMock()

    update_job_prose(
        db,
        job,
        JobProseUpdate(exec_summary="  ", scope_methodology="", findings=None),
    )

    assert job.exec_summary is None
    assert job.scope_methodology is None
    assert job.findings is None


def test_update_job_prose_rejects_locked() -> None:
    job = MagicMock()
    job.status = JobStatus.APPROVED
    db = MagicMock()

    try:
        update_job_prose(
            db,
            job,
            JobProseUpdate(exec_summary="x", scope_methodology=None, findings=None),
        )
        raise AssertionError("expected JobLockedError")
    except JobLockedError:
        pass
    db.commit.assert_not_called()
