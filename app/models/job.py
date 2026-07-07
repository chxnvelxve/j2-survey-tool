"""Job — central container for one survey engagement."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import JobStatus

if TYPE_CHECKING:
    from app.models.attachment import Attachment
    from app.models.photo import Photo
    from app.models.survey_file import SurveyFile


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        # VARCHAR storage — phase names unconfirmed (docs/DECISIONS.md #22).
        Enum(JobStatus, native_enum=False),
        nullable=False,
        default=JobStatus.AWAITING_INPUTS,
        server_default=JobStatus.AWAITING_INPUTS.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    merged_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    survey_files: Mapped[list["SurveyFile"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    photos: Mapped[list["Photo"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
