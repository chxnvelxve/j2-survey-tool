"""SQLAlchemy declarative base. Domain models land in Phase 1."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
