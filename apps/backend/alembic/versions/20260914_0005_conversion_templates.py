"""Conversion templates table (EV-080 / F7.w / #1146).

Revision ID: 20260914_0005
Revises: 20260907_0004
Create Date: 2026-09-14

Owner-scoped custom conversion templates. First-party builtins are code-served.
No destination credentials.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260914_0005"
down_revision: str | None = "20260907_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Create tac_conversion_templates.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (upgrade)
    2
    """
    op.create_table(
        "tac_conversion_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("iwxxm_block", sa.Text(), nullable=False),
        sa.Column(
            "slots",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("sample", sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("fork_of", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("user_id", "slug", name="uq_tac_conversion_templates_user_slug"),
    )
    op.create_index(
        "ix_tac_conversion_templates_user_id",
        "tac_conversion_templates",
        ["user_id"],
    )


def downgrade() -> None:
    """
    Drop tac_conversion_templates.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (downgrade)
    2
    """
    op.drop_index("ix_tac_conversion_templates_user_id", table_name="tac_conversion_templates")
    op.drop_table("tac_conversion_templates")
