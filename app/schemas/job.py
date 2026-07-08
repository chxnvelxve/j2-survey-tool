"""Pydantic schemas for Job CRUD and file uploads."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import JobStatus, PhotoShotType

JOB_STATUS_LABELS: dict[JobStatus, str] = {
    JobStatus.AWAITING_INPUTS: "Awaiting inputs",
    JobStatus.INPUTS_UPLOADED: "Inputs uploaded",
    JobStatus.MERGED: "Merged",
    JobStatus.FLAGS_RESOLVED: "Flags resolved",
    JobStatus.DRAFT_IN_REVIEW: "Draft in review",
    JobStatus.APPROVED: "Approved",
}


def job_status_label(status: JobStatus) -> str:
    return JOB_STATUS_LABELS.get(status, status.value)


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
