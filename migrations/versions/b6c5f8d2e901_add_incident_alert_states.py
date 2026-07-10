"""add incident alert states

Revision ID: b6c5f8d2e901
Revises: 7b2d9f4a1c01
Create Date: 2026-07-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b6c5f8d2e901"
down_revision: Union[str, Sequence[str], None] = "7b2d9f4a1c01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_incidents", sa.Column("confirmed_at", sa.BigInteger(), nullable=True))
    op.add_column("site_incidents", sa.Column("confirmed_status_code", sa.Integer(), nullable=True))
    op.add_column("site_incidents", sa.Column("confirmed_description", sa.Text(), nullable=True))
    op.add_column(
        "site_incidents",
        sa.Column("alert_suppressed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("site_incidents", sa.Column("alert_sent_at", sa.BigInteger(), nullable=True))
    op.add_column("site_incidents", sa.Column("recovery_sent_at", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("site_incidents", "recovery_sent_at")
    op.drop_column("site_incidents", "alert_sent_at")
    op.drop_column("site_incidents", "alert_suppressed")
    op.drop_column("site_incidents", "confirmed_description")
    op.drop_column("site_incidents", "confirmed_status_code")
    op.drop_column("site_incidents", "confirmed_at")
