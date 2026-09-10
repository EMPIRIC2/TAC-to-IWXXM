"""Profile preset and dissemination template tables (EV-1051 / F7.w / #1051).

Revision ID: 20260907_0004
Revises: 20260903_0003
Create Date: 2026-09-07

Owner-scoped semantic presets and dissemination templates with optional shared reads.
No secrets or destination URIs.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260907_0004"
down_revision: str | None = "20260903_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tac_profile_presets and tac_dissemination_templates."""
    op.create_table(
        "tac_profile_presets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("semantic_profile", sa.Text(), nullable=False),
        sa.Column("iwxxm_version", sa.Text(), nullable=False),
        sa.Column(
            "extensions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("report_variant", sa.Text(), nullable=True),
        sa.Column("overlay_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["overlay_id"],
            ["tac_profile_overlays.id"],
            name="fk_tac_profile_presets_overlay_id",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("user_id", "slug", name="uq_tac_profile_presets_user_slug"),
    )
    op.create_index(
        "ix_tac_profile_presets_user_id",
        "tac_profile_presets",
        ["user_id"],
    )
    op.create_table(
        "tac_dissemination_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("sink_type", sa.Text(), nullable=False),
        sa.Column("product", sa.Text(), nullable=True),
        sa.Column(
            "ddl",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "params",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
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
        sa.UniqueConstraint("user_id", "slug", name="uq_tac_dissemination_templates_user_slug"),
    )
    op.create_index(
        "ix_tac_dissemination_templates_user_id",
        "tac_dissemination_templates",
        ["user_id"],
    )


def downgrade() -> None:
    """Drop tac_profile_presets and tac_dissemination_templates."""
    op.drop_index("ix_tac_dissemination_templates_user_id", table_name="tac_dissemination_templates")
    op.drop_table("tac_dissemination_templates")
    op.drop_index("ix_tac_profile_presets_user_id", table_name="tac_profile_presets")
    op.drop_table("tac_profile_presets")
