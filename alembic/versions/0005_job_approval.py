"""Add approved_at and approved_by to jobs.

Revision ID: 0005_job_approval
Revises: 0004_job_deliverable
Create Date: 2026-07-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_job_approval"
down_revision: Union[str, None] = "0004_job_deliverable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("approved_by", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("jobs", "approved_by")
    op.drop_column("jobs", "approved_at")
