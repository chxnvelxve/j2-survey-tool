"""Add nullable capture settings columns to jobs.

Revision ID: 0006_job_capture_settings
Revises: 0005_job_approval
Create Date: 2026-07-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_job_capture_settings"
down_revision: Union[str, None] = "0005_job_approval"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("survey_type", sa.String(length=255), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("location_vertical", sa.String(length=255), nullable=True),
    )
    op.add_column("jobs", sa.Column("band_plan", sa.String(length=255), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("site_metadata", sa.String(length=1024), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("jobs", "site_metadata")
    op.drop_column("jobs", "band_plan")
    op.drop_column("jobs", "location_vertical")
    op.drop_column("jobs", "survey_type")
