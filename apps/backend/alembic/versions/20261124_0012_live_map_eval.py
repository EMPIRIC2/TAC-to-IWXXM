"""Live map evaluation snapshots (FR-045).

Revision ID: 20261124_0012
Revises: 20261113_0011
Create Date: 2026-11-24

Stores cron-built aggregate eval rows for GET /api/v1/live-map/eval.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261124_0012"
down_revision: str | None = "20261113_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create live_map_eval_snapshots."""
    op.create_table(
        "live_map_eval_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_hours", sa.Integer(), nullable=False, server_default="24"),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_live_map_eval_snapshots_computed_at",
        "live_map_eval_snapshots",
        ["computed_at"],
    )


def downgrade() -> None:
    """Drop live_map_eval_snapshots."""
    op.drop_index(
        "ix_live_map_eval_snapshots_computed_at",
        table_name="live_map_eval_snapshots",
    )
    op.drop_table("live_map_eval_snapshots")
