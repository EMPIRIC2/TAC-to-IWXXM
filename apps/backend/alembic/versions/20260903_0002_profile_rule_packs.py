"""Profile rule-pack tables (EV-933 / F7.w / #933).

Revision ID: 20260903_0002
Revises: 20260903_0001
Create Date: 2026-09-03

Owner-scoped rule packs on product Postgres. No secrets or destination URIs.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_0002"
down_revision: str | None = "20260903_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tac_profile_rule_packs."""
    op.create_table(
        "tac_profile_rule_packs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("profile", sa.Text(), nullable=False),
        sa.Column("product", sa.Text(), nullable=False),
        sa.Column("stage", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("when_expr", sa.Text(), nullable=False, server_default=""),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("standard_reference", sa.Text(), nullable=False, server_default=""),
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
            name="uq_tac_profile_rule_packs_user_slug",
        ),
    )
    op.create_index(
        "ix_tac_profile_rule_packs_user_id",
        "tac_profile_rule_packs",
        ["user_id"],
    )


def downgrade() -> None:
    """Drop tac_profile_rule_packs."""
    op.drop_index("ix_tac_profile_rule_packs_user_id", table_name="tac_profile_rule_packs")
    op.drop_table("tac_profile_rule_packs")
