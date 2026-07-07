"""Pydantic schemas for the merge pipeline — MergedJob contract."""
from enum import Enum

from pydantic import BaseModel, Field

from app.models.enums import PhotoShotType
from app.schemas.survey import SurveyAP


class FlagType(str, Enum):
    MISSING_PHOTO = "missing_photo"
    NAME_MISMATCH = "name_mismatch"
    CROSS_FILE_DISAGREEMENT = "cross_file_disagreement"
    ORPHAN_PHOTO = "orphan_photo"


FLAG_TYPE_LABELS: dict[FlagType, str] = {
    FlagType.MISSING_PHOTO: "Missing photo",
    FlagType.NAME_MISMATCH: "Name does not match survey",
    FlagType.CROSS_FILE_DISAGREEMENT: "Survey files disagree",
    FlagType.ORPHAN_PHOTO: "No matching survey AP",
}


class MergedAPStatus(str, Enum):
    MATCHED = "matched"
    INCOMPLETE = "incomplete"
    FLAGGED = "flagged"


class MergedPhotoRef(BaseModel):
    photo_id: int
    original_filename: str


class MergedPhotoSlots(BaseModel):
    close: MergedPhotoRef | None = None
    far: MergedPhotoRef | None = None


class MergedAP(BaseModel):
    ap_name: str
    survey_data: SurveyAP
    photos: MergedPhotoSlots
    status: MergedAPStatus


class Flag(BaseModel):
    ap_name: str
    type: FlagType
    detail: str
    override_reason: str | None = None


class MergedJob(BaseModel):
    aps: list[MergedAP] = Field(default_factory=list)
    flags: list[Flag] = Field(default_factory=list)


class MergePhotoInput(BaseModel):
    photo_id: int
    ap_name: str
    shot_type: PhotoShotType
    original_filename: str
