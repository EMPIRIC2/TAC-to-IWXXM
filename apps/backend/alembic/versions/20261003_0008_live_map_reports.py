"""Live map report cache (F37).

Revision ID: 20261003_0008
Revises: 20260916_0007
Create Date: 2026-10-03

Last three feed reports per place. No IWXXM column: conversion runs when a
report is opened, not on the refresh.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261003_0008"
down_revision: str | None = "20260916_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the live map cache table."""
    op.create_table(
        "live_map_reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("place_key", sa.String(length=64), nullable=False),
        sa.Column("product", sa.String(length=16), nullable=False),
        sa.Column("observed_at", sa.String(length=40), nullable=False),
        sa.Column("tac", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    """Drop the live map cache table."""
    op.drop_table("live_map_reports")
