"""Profile overlay tables (EV-933 / F7.w / #933 M2).

Revision ID: 20260903_0003
Revises: 20260903_0002
Create Date: 2026-09-04

Owner-scoped signed overlays on product Postgres. No secrets or destination URIs.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_0003"
down_revision: str | None = "20260903_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tac_profile_overlays."""
    op.create_table(
        "tac_profile_overlays",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("base_profile_id", sa.Text(), nullable=False),
        sa.Column(
            "body",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("signature", sa.Text(), nullable=False),
        sa.Column(
            "shared",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "slug",
            name="uq_tac_profile_overlays_user_slug",
        ),
    )
    op.create_index(
        "ix_tac_profile_overlays_user_id",
        "tac_profile_overlays",
        ["user_id"],
    )


def downgrade() -> None:
    """Drop tac_profile_overlays."""
    op.drop_index("ix_tac_profile_overlays_user_id", table_name="tac_profile_overlays")
    op.drop_table("tac_profile_overlays")
