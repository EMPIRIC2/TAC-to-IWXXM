"""Dissemination ops tables (EV-936 / ADR-041 / ADR-040).

Revision ID: 20260903_0001
Revises: 20260803_0001
Create Date: 2026-09-03

Plans, redacted delivery audit, and MappingConfig rows on product Postgres.
No BYOC secrets or connection URIs in any column.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260903_0001"
down_revision: str | None = "20260803_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create dissemination ops tables."""
    op.create_table(
        "tac_dissemination_plans",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("validity_policy", sa.Text(), nullable=False, server_default="valid-only"),
        sa.Column(
            "destination_refs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "transforms",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "retry",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
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
        sa.UniqueConstraint("user_id", "slug", name="uq_tac_dissemination_plans_user_slug"),
    )
    op.create_index(
        "ix_tac_dissemination_plans_user_id",
        "tac_dissemination_plans",
        ["user_id"],
    )

    op.create_table(
        "tac_dissemination_audit",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", sa.Text(), nullable=True),
        sa.Column("station", sa.Text(), nullable=True),
        sa.Column("profile", sa.Text(), nullable=True),
        sa.Column("iwxxm_version", sa.Text(), nullable=True),
        sa.Column("product", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("gateway", sa.Text(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column(
            "destinations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_tac_dissemination_audit_user_id",
        "tac_dissemination_audit",
        ["user_id"],
    )
    op.create_index(
        "ix_tac_dissemination_audit_status",
        "tac_dissemination_audit",
        ["status"],
    )

    op.create_table(
        "tac_mapping_configs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=False),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.UniqueConstraint("user_id", "name", name="uq_tac_mapping_configs_user_name"),
        sa.CheckConstraint("mode IN ('source', 'sink')", name="ck_tac_mapping_configs_mode"),
    )
    op.create_index(
        "ix_tac_mapping_configs_user_id",
        "tac_mapping_configs",
        ["user_id"],
    )


def downgrade() -> None:
    """Drop dissemination ops tables."""
    op.drop_table("tac_mapping_configs")
    op.drop_table("tac_dissemination_audit")
    op.drop_table("tac_dissemination_plans")
