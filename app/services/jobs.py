"""Job CRUD and file upload business logic."""
from __future__ import annotations

import os
from typing import BinaryIO

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.storage import Storage
from app.models.attachment import Attachment
from app.models.enums import JobStatus, PhotoShotType
from app.models.job import Job
from app.models.photo import Photo
from app.models.survey_file import SurveyFile


class DuplicatePhotoError(Exception):
    """Raised when the same AP name + shot type is uploaded twice for one Job."""


class JobNotFoundError(Exception):
    pass


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


def upload_survey_file(
    db: Session,
    storage: Storage,
    job: Job,
    upload: UploadFile,
) -> SurveyFile:
    filename = upload.filename or "unknown.esx"
    size_bytes = _file_size(upload.file)
    rel_path = _save_file(storage, job.id, "esx", filename, upload.file)
    record = SurveyFile(
        job_id=job.id,
        storage_path=rel_path,
        original_filename=filename,
        content_type=upload.content_type,
        size_bytes=size_bytes,
    )
    db.add(record)
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
    filename = upload.filename or "photo.jpg"
    size_bytes = _file_size(upload.file)
    subdir_name = f"photos/{ap_name.strip()}_{shot_type.value}"
    rel_path = _save_file(storage, job.id, subdir_name, filename, upload.file)
    record = Photo(
        job_id=job.id,
        storage_path=rel_path,
        original_filename=filename,
        content_type=upload.content_type,
        size_bytes=size_bytes,
        ap_name=ap_name.strip(),
        shot_type=shot_type,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicatePhotoError(
            f"Photo already exists for AP {ap_name!r} ({shot_type.value})"
        ) from exc
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
