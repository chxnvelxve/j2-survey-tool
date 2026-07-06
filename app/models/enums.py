"""Domain enums for Job lifecycle and photo metadata."""
from enum import Enum


class JobStatus(str, Enum):
    """Job phase progression. Display labels are unconfirmed — see docs/DECISIONS.md."""

    AWAITING_INPUTS = "awaiting_inputs"
    INPUTS_UPLOADED = "inputs_uploaded"
    MERGED = "merged"
    FLAGS_RESOLVED = "flags_resolved"
    DRAFT_IN_REVIEW = "draft_in_review"
    APPROVED = "approved"


class PhotoShotType(str, Enum):
    CLOSE = "close"
    FAR = "far"
