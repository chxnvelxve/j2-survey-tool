"""Add deliverable_path and generated_at to jobs.

Revision ID: 0004_job_deliverable
Revises: 0003_job_merged_snapshot
Create Date: 2026-07-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_job_deliverable"
down_revision: Union[str, None] = "0003_job_merged_snapshot"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("deliverable_path", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("jobs", "generated_at")
    op.drop_column("jobs", "deliverable_path")
