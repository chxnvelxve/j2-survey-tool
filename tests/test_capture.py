"""Phase 11 — field capture settings and AP-name picker helpers."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.models.enums import JobStatus
from app.schemas.job import JobSettingsUpdate
from app.schemas.survey import ParsedSurveyFile, SurveyAP, SurveyModel, SurveyProject
from app.services.jobs import JobLockedError, update_job_settings
from app.services.survey_parse import flatten_ap_names


def _parsed(
    *names: str,
    error: str | None = None,
) -> ParsedSurveyFile:
    if error is not None:
        return ParsedSurveyFile(
            survey_file_id=1,
            filename="bad.esx",
            error=error,
        )
    return ParsedSurveyFile(
        survey_file_id=1,
        filename="sample.esx",
        survey=SurveyModel(
            project=SurveyProject(name="t"),
            floors=[],
            aps=[SurveyAP(name=n) for n in names],
            source_filename="sample.esx",
        ),
    )


def test_flatten_ap_names_preserves_exact_and_order() -> None:
    names = flatten_ap_names(
        [
            _parsed("AP-01", " AP-02 "),
            _parsed("AP-01", "AP-03"),
        ],
    )
    assert names == ["AP-01", " AP-02 ", "AP-03"]


def test_flatten_ap_names_skips_errors_and_empty() -> None:
    assert flatten_ap_names([]) == []
    assert flatten_ap_names([_parsed(error="parse failed")]) == []


def test_update_job_settings_round_trip() -> None:
    job = MagicMock()
    job.status = JobStatus.INPUTS_UPLOADED
    job.survey_type = None
    job.location_vertical = None
    job.band_plan = None
    job.site_metadata = None
    db = MagicMock()

    update_job_settings(
        db,
        job,
        JobSettingsUpdate(
            survey_type="validation",
            location_vertical="warehouse",
            band_plan="5 GHz",
            site_metadata="Acme / 1 Main St",
        ),
    )

    assert job.survey_type == "validation"
    assert job.location_vertical == "warehouse"
    assert job.band_plan == "5 GHz"
    assert job.site_metadata == "Acme / 1 Main St"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(job)


def test_update_job_settings_blank_to_none() -> None:
    job = MagicMock()
    job.status = JobStatus.AWAITING_INPUTS
    db = MagicMock()

    update_job_settings(
        db,
        job,
        JobSettingsUpdate(
            survey_type="  ",
            location_vertical="",
            band_plan=None,
            site_metadata=" notes ",
        ),
    )

    assert job.survey_type is None
    assert job.location_vertical is None
    assert job.band_plan is None
    assert job.site_metadata == "notes"


def test_update_job_settings_locked() -> None:
    job = MagicMock()
    job.status = JobStatus.APPROVED
    db = MagicMock()

    with pytest.raises(JobLockedError):
        update_job_settings(
            db,
            job,
            JobSettingsUpdate(survey_type="x"),
        )
    db.commit.assert_not_called()
