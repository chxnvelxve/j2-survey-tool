"""Orchestrate per-file .esx parsing for a Job."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.storage import Storage
from app.models.job import Job
from app.schemas.survey import ParsedSurveyFile
from app.services.parser.errors import ParseError
from app.services.parser.parser import parse_esx


def parse_job_surveys(_db: Session, storage: Storage, job: Job) -> list[ParsedSurveyFile]:
    """Parse each SurveyFile on the Job; per-file errors do not fail the whole Job."""
    results: list[ParsedSurveyFile] = []
    for survey_file in job.survey_files:
        try:
            with storage.open(survey_file.storage_path) as fileobj:
                survey = parse_esx(fileobj, source_name=survey_file.original_filename)
        except ParseError as exc:
            results.append(
                ParsedSurveyFile(
                    survey_file_id=survey_file.id,
                    filename=survey_file.original_filename,
                    error=str(exc),
                ),
            )
        except OSError as exc:
            results.append(
                ParsedSurveyFile(
                    survey_file_id=survey_file.id,
                    filename=survey_file.original_filename,
                    error=f"{survey_file.original_filename}: Could not read file ({exc})",
                ),
            )
        else:
            results.append(
                ParsedSurveyFile(
                    survey_file_id=survey_file.id,
                    filename=survey_file.original_filename,
                    survey=survey,
                ),
            )
    return results


def flatten_ap_names(parsed_surveys: list[ParsedSurveyFile]) -> list[str]:
    """Unique AP names from parsed surveys, exact strings preserved, first-seen order."""
    seen: set[str] = set()
    names: list[str] = []
    for pf in parsed_surveys:
        if pf.survey is None:
            continue
        for ap in pf.survey.aps:
            if ap.name in seen:
                continue
            seen.add(ap.name)
            names.append(ap.name)
    return names

