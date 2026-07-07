"""Orchestrate parse + merge on manual push; persist MergedJob snapshot."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.storage import Storage
from app.models.enums import JobStatus
from app.models.job import Job
from app.schemas.merge import MergePhotoInput, MergedJob
from app.services.merge.merge import merge
from app.services.survey_parse import parse_job_surveys


def push_job_merge(db: Session, storage: Storage, job: Job) -> MergedJob:
    """Parse all survey files, merge with photos, persist snapshot, advance status."""
    parsed = parse_job_surveys(db, storage, job)
    surveys = [p.survey for p in parsed if p.survey is not None]
    photo_inputs = [
        MergePhotoInput(
            photo_id=photo.id,
            ap_name=photo.ap_name,
            shot_type=photo.shot_type,
            original_filename=photo.original_filename,
        )
        for photo in job.photos
    ]
    merged = merge(surveys, photo_inputs)
    job.merged_snapshot = merged.model_dump(mode="json")
    job.status = JobStatus.FLAGS_RESOLVED if not merged.flags else JobStatus.MERGED
    db.commit()
    db.refresh(job)
    return merged


def merged_job_from_snapshot(job: Job) -> MergedJob | None:
    if job.merged_snapshot is None:
        return None
    return MergedJob.model_validate(job.merged_snapshot)
