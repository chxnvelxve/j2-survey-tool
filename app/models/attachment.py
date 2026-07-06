"""Attachment — IDF diagrams, LLDs, and other supporting files."""
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base
from app.models.mixins import FileRecordMixin

if TYPE_CHECKING:
    from app.models.job import Job


class Attachment(FileRecordMixin, Base):
    __tablename__ = "attachments"

    job: Mapped["Job"] = relationship(back_populates="attachments")
