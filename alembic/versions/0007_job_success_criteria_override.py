"""Add nullable success_criteria_override JSON column to jobs.

Revision ID: 0007_criteria_override
Revises: 0006_job_capture_settings
Create Date: 2026-07-10

Note: revision id must stay ≤32 chars (alembic_version.version_num).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_criteria_override"
down_revision: Union[str, None] = "0006_job_capture_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("success_criteria_override", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("jobs", "success_criteria_override")
