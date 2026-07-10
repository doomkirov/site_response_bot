"""add incidents and daily reports

Revision ID: 7b2d9f4a1c01
Revises: cc8a0ce5970c
Create Date: 2026-07-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "7b2d9f4a1c01"
down_revision: Union[str, Sequence[str], None] = "cc8a0ce5970c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_incidents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("link_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("started_at", sa.BigInteger(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("recovered_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["link_id"], ["links.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_site_incidents_link_id", "site_incidents", ["link_id"])
    op.create_index("ix_site_incidents_started_at", "site_incidents", ["started_at"])
    op.create_index("ix_site_incidents_recovered_at", "site_incidents", ["recovered_at"])

    op.create_table(
        "daily_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("report_date", sa.String(), nullable=False),
        sa.Column("sent_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("report_date"),
    )


def downgrade() -> None:
    op.drop_table("daily_reports")
    op.drop_index("ix_site_incidents_recovered_at", table_name="site_incidents")
    op.drop_index("ix_site_incidents_started_at", table_name="site_incidents")
    op.drop_index("ix_site_incidents_link_id", table_name="site_incidents")
    op.drop_table("site_incidents")
