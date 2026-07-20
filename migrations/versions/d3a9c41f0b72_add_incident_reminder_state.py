"""add incident reminder state

Revision ID: d3a9c41f0b72
Revises: b6c5f8d2e901
Create Date: 2026-07-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d3a9c41f0b72"
down_revision: Union[str, Sequence[str], None] = "b6c5f8d2e901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_incidents", sa.Column("reminder_sent_at", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("site_incidents", "reminder_sent_at")
