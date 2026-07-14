"""Add nullable DRAFTED prose columns to jobs (Phase 13d).

Revision ID: 0008_job_drafted_prose
Revises: 0007_job_success_criteria_override
Create Date: 2026-07-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_job_drafted_prose"
down_revision: Union[str, None] = "0007_job_success_criteria_override"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("exec_summary", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("scope_methodology", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("findings", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "findings")
    op.drop_column("jobs", "scope_methodology")
    op.drop_column("jobs", "exec_summary")
