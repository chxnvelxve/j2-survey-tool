"""Pydantic schemas for Job CRUD and file uploads."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.labels import job_status_label
from app.models.enums import JobStatus, PhotoShotType

__all__ = [
    "AttachmentRead",
    "JobCreate",
    "JobListItem",
    "JobRead",
    "PhotoRead",
    "SurveyFileRead",
    "job_status_label",
]


class JobCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class FileRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    content_type: str | None
    size_bytes: int | None
    uploaded_at: datetime


class SurveyFileRead(FileRecordRead):
    pass


class PhotoRead(FileRecordRead):
    ap_name: str
    shot_type: PhotoShotType


class AttachmentRead(FileRecordRead):
    pass


class JobListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: JobStatus
    created_at: datetime


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    generated_at: datetime | None = None
    deliverable_path: str | None = None
    approved_at: datetime | None = None
    approved_by: str | None = None
    survey_files: list[SurveyFileRead] = Field(default_factory=list)
    photos: list[PhotoRead] = Field(default_factory=list)
    attachments: list[AttachmentRead] = Field(default_factory=list)
