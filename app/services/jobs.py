"""Job CRUD and file upload business logic."""
from __future__ import annotations

import os
import zipfile
from io import BytesIO
from typing import BinaryIO

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.storage import Storage
from app.models.attachment import Attachment
from app.models.enums import JobStatus, PhotoShotType
from app.models.job import Job
from app.models.photo import Photo
from app.models.survey_file import SurveyFile
from app.schemas.job import JobSettingsUpdate


class InvalidSurveyFileError(Exception):
    """Raised when an uploaded file is not a valid .esx ZIP archive."""


class JobNotFoundError(Exception):
    pass


class JobFileNotFoundError(Exception):
    """Raised when a survey file, photo, or attachment id is not on this job."""


class JobLockedError(Exception):
    """Job is approved; mutating operations are not allowed."""


class InvalidPhotoApNameError(Exception):
    """Raised when a photo upload has a blank or whitespace-only AP name."""


def job_is_locked(job: Job) -> bool:
    return job.status == JobStatus.APPROVED


def _ensure_not_locked(job: Job) -> None:
    if job_is_locked(job):
        raise JobLockedError("This job is approved and cannot be modified.")


def create_job(db: Session, name: str) -> Job:
    job = Job(name=name.strip())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> list[Job]:
    stmt = select(Job).order_by(Job.created_at.desc())
    return list(db.scalars(stmt).all())


def get_job(db: Session, job_id: int) -> Job | None:
    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .options(
            selectinload(Job.survey_files),
            selectinload(Job.photos),
            selectinload(Job.attachments),
        )
    )
    return db.scalars(stmt).first()


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def update_job_settings(db: Session, job: Job, settings: JobSettingsUpdate) -> Job:
    """Persist capture-time job settings. Does not change status or readiness."""
    _ensure_not_locked(job)
    job.survey_type = _blank_to_none(settings.survey_type)
    job.location_vertical = _blank_to_none(settings.location_vertical)
    job.band_plan = _blank_to_none(settings.band_plan)
    job.site_metadata = _blank_to_none(settings.site_metadata)
    db.commit()
    db.refresh(job)
    return job


def _file_size(fileobj: BinaryIO) -> int | None:
    try:
        fileobj.seek(0, os.SEEK_END)
        size = fileobj.tell()
        fileobj.seek(0)
        return size
    except OSError:
        return None


def _save_file(
    storage: Storage,
    job_id: int,
    subdir: str,
    filename: str,
    fileobj: BinaryIO,
) -> str:
    safe_name = filename.replace("\\", "_").replace("/", "_")
    rel_path = f"jobs/{job_id}/{subdir}/{safe_name}"
    return storage.save(rel_path, fileobj)


def _maybe_bump_status(db: Session, job: Job) -> None:
    if job.status != JobStatus.AWAITING_INPUTS:
        return
    if job.survey_files or job.photos or job.attachments:
        job.status = JobStatus.INPUTS_UPLOADED
        db.commit()


def _invalidate_merge(job: Job) -> None:
    """Clear stale merge snapshot when job inputs change."""
    job.merged_snapshot = None
    job.deliverable_path = None
    job.generated_at = None
    if job.status in (
        JobStatus.MERGED,
        JobStatus.FLAGS_RESOLVED,
        JobStatus.DRAFT_IN_REVIEW,
    ):
        job.status = JobStatus.INPUTS_UPLOADED


def upload_survey_file(
    db: Session,
    storage: Storage,
    job: Job,
    upload: UploadFile,
) -> SurveyFile:
    _ensure_not_locked(job)
    filename = upload.filename or "unknown.esx"
    upload.file.seek(0)
    data = upload.file.read()
    upload.file.seek(0)
    if not data:
        raise InvalidSurveyFileError(f"{filename}: Empty file")
    if not zipfile.is_zipfile(BytesIO(data)):
        raise InvalidSurveyFileError(
            f"{filename}: Not a valid Ekahau .esx (expected ZIP archive). "
            "Use tests/fixtures/sample_survey.esx from this repo for testing.",
        )

    size_bytes = len(data)
    rel_path = _save_file(storage, job.id, "esx", filename, upload.file)
    record = SurveyFile(
        job_id=job.id,
        storage_path=rel_path,
        original_filename=filename,
        content_type=upload.content_type,
        size_bytes=size_bytes,
    )
    db.add(record)
    _invalidate_merge(job)
    db.commit()
    db.refresh(record)
    job.survey_files.append(record)
    _maybe_bump_status(db, job)
    return record


def upload_photo(
    db: Session,
    storage: Storage,
    job: Job,
    upload: UploadFile,
    ap_name: str,
    shot_type: PhotoShotType,
) -> Photo:
    _ensure_not_locked(job)
    if not ap_name or not ap_name.strip():
        raise InvalidPhotoApNameError(
            "AP name is required — pick from the list or type the exact survey name.",
        )
    filename = upload.filename or "photo.jpg"
    size_bytes = _file_size(upload.file)
    subdir_name = f"photos/{ap_name.strip()}_{shot_type.value}"
    rel_path = _save_file(storage, job.id, subdir_name, filename, upload.file)

    existing = db.scalars(
        select(Photo).where(
            Photo.job_id == job.id,
            Photo.ap_name == ap_name,
            Photo.shot_type == shot_type,
        ),
    ).first()

    if existing is not None:
        existing.storage_path = rel_path
        existing.original_filename = filename
        existing.content_type = upload.content_type
        existing.size_bytes = size_bytes
        _invalidate_merge(job)
        db.commit()
        db.refresh(existing)
        return existing

    record = Photo(
        job_id=job.id,
        storage_path=rel_path,
        original_filename=filename,
        content_type=upload.content_type,
        size_bytes=size_bytes,
        ap_name=ap_name,
        shot_type=shot_type,
    )
    db.add(record)
    _invalidate_merge(job)
    db.commit()
    db.refresh(record)
    job.photos.append(record)
    _maybe_bump_status(db, job)
    return record


def upload_attachment(
    db: Session,
    storage: Storage,
    job: Job,
    upload: UploadFile,
) -> Attachment:
    _ensure_not_locked(job)
    filename = upload.filename or "attachment"
    size_bytes = _file_size(upload.file)
    rel_path = _save_file(storage, job.id, "attachments", filename, upload.file)
    record = Attachment(
        job_id=job.id,
        storage_path=rel_path,
        original_filename=filename,
        content_type=upload.content_type,
        size_bytes=size_bytes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    job.attachments.append(record)
    _maybe_bump_status(db, job)
    return record


def delete_survey_file(
    db: Session,
    storage: Storage,
    job: Job,
    survey_file_id: int,
) -> None:
    _ensure_not_locked(job)
    record = db.scalars(
        select(SurveyFile).where(
            SurveyFile.id == survey_file_id,
            SurveyFile.job_id == job.id,
        ),
    ).first()
    if record is None:
        raise JobFileNotFoundError(f"Survey file {survey_file_id} not found on job {job.id}")
    storage.delete(record.storage_path)
    db.delete(record)
    job.survey_files = [f for f in job.survey_files if f.id != survey_file_id]
    _invalidate_merge(job)
    db.commit()


def delete_photo(
    db: Session,
    storage: Storage,
    job: Job,
    photo_id: int,
) -> None:
    _ensure_not_locked(job)
    record = db.scalars(
        select(Photo).where(
            Photo.id == photo_id,
            Photo.job_id == job.id,
        ),
    ).first()
    if record is None:
        raise JobFileNotFoundError(f"Photo {photo_id} not found on job {job.id}")
    storage.delete(record.storage_path)
    db.delete(record)
    job.photos = [p for p in job.photos if p.id != photo_id]
    _invalidate_merge(job)
    db.commit()


def delete_attachment(
    db: Session,
    storage: Storage,
    job: Job,
    attachment_id: int,
) -> None:
    _ensure_not_locked(job)
    record = db.scalars(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.job_id == job.id,
        ),
    ).first()
    if record is None:
        raise JobFileNotFoundError(f"Attachment {attachment_id} not found on job {job.id}")
    storage.delete(record.storage_path)
    db.delete(record)
    job.attachments = [a for a in job.attachments if a.id != attachment_id]
    db.commit()
