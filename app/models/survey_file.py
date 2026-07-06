"""SurveyFile — one uploaded .esx per row."""
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base
from app.models.mixins import FileRecordMixin

if TYPE_CHECKING:
    from app.models.job import Job


class SurveyFile(FileRecordMixin, Base):
    __tablename__ = "survey_files"

    job: Mapped["Job"] = relationship(back_populates="survey_files")
