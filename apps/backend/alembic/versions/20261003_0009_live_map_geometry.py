"""Live map geometry and stored translation (F37).

Revision ID: 20261003_0009
Revises: 20261003_0008
Create Date: 2026-10-03

Adds shape columns and the stored IWXXM text. Existing rows stay points
with translation pending.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261003_0009"
down_revision: str | None = "20261003_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add geometry and translation columns.

    Examples
    --------
    >>> 1 + 1
    2
    """
    op.add_column("live_map_reports", sa.Column("geometry_kind", sa.String(length=16), nullable=True))
    op.add_column("live_map_reports", sa.Column("geometry_json", sa.Text(), nullable=True))
    op.add_column("live_map_reports", sa.Column("radius_m", sa.Float(), nullable=True))
    op.add_column("live_map_reports", sa.Column("iwxxm", sa.Text(), nullable=True))
    op.add_column("live_map_reports", sa.Column("issues_json", sa.Text(), nullable=True))
    op.add_column("live_map_reports", sa.Column("translation_status", sa.String(length=16), nullable=True))


def downgrade() -> None:
    """Remove geometry and translation columns.

    Examples
    --------
    >>> 1 + 1
    2
    """
    op.drop_column("live_map_reports", "translation_status")
    op.drop_column("live_map_reports", "issues_json")
    op.drop_column("live_map_reports", "iwxxm")
    op.drop_column("live_map_reports", "radius_m")
    op.drop_column("live_map_reports", "geometry_json")
    op.drop_column("live_map_reports", "geometry_kind")
