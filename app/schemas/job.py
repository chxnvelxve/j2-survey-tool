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
    "JobSettingsUpdate",
    "PhotoRead",
    "SurveyFileRead",
    "job_status_label",
]


class JobCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class JobSettingsUpdate(BaseModel):
    """Per-job capture settings — store only; not readiness-gated (Phase 11)."""

    survey_type: str | None = Field(default=None, max_length=255)
    location_vertical: str | None = Field(default=None, max_length=255)
    band_plan: str | None = Field(default=None, max_length=255)
    site_metadata: str | None = Field(default=None, max_length=1024)


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
    survey_type: str | None = None
    location_vertical: str | None = None
    band_plan: str | None = None
    site_metadata: str | None = None
    survey_files: list[SurveyFileRead] = Field(default_factory=list)
    photos: list[PhotoRead] = Field(default_factory=list)
    attachments: list[AttachmentRead] = Field(default_factory=list)
