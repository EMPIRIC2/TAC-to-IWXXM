"""Library assets table (EV-bridge five Libraries).

Revision ID: 20260914_0006
Revises: 20260914_0005
Create Date: 2026-09-14

Owner-scoped custom library assets. First-party builtins are code-served.
No destination credentials.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260914_0006"
down_revision: str | None = "20260914_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tac_library_assets."""
    op.create_table(
        "tac_library_assets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("engine_profile_id", sa.Text(), nullable=False),
        sa.Column("attached_national_line", sa.Text(), nullable=False),
        sa.Column(
            "body",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
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
        sa.UniqueConstraint("user_id", "slug", name="uq_tac_library_assets_user_slug"),
        sa.CheckConstraint(
            "kind IN ('conversion','tac_validation','iwxxm_validation','dissemination','decoding')",
            name="ck_tac_library_assets_kind",
        ),
    )
    op.create_index("ix_tac_library_assets_user_id", "tac_library_assets", ["user_id"])
    op.create_index("ix_tac_library_assets_kind", "tac_library_assets", ["kind"])


def downgrade() -> None:
    """Drop tac_library_assets."""
    op.drop_index("ix_tac_library_assets_kind", table_name="tac_library_assets")
    op.drop_index("ix_tac_library_assets_user_id", table_name="tac_library_assets")
    op.drop_table("tac_library_assets")
