"""Add merged_snapshot JSON column to jobs.

Revision ID: 0003_job_merged_snapshot
Revises: 0002_job_domain_models
Create Date: 2026-07-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_job_merged_snapshot"
down_revision: Union[str, None] = "0002_job_domain_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("merged_snapshot", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "merged_snapshot")
