"""Photo — field AP image matched to survey APs by exact ap_name."""
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import PhotoShotType
from app.models.mixins import FileRecordMixin

if TYPE_CHECKING:
    from app.models.job import Job


class Photo(FileRecordMixin, Base):
    __tablename__ = "photos"
    __table_args__ = (
        UniqueConstraint("job_id", "ap_name", "shot_type", name="uq_photos_job_ap_shot"),
    )

    ap_name: Mapped[str] = mapped_column(String(255), nullable=False)
    shot_type: Mapped[PhotoShotType] = mapped_column(
        Enum(PhotoShotType, native_enum=False),
        nullable=False,
    )

    job: Mapped["Job"] = relationship(back_populates="photos")
