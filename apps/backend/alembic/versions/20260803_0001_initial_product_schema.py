"""Initial product schema on DO Postgres (F30/F31 / ADR-033).

Revision ID: 20260803_0001
Revises:
Create Date: 2026-08-03

Creates ``tac_work_sessions`` (ADR-020 wire shapes + swxa) and F8 ingest store /
quarantine tables. No Supabase Auth user FK — Auth remains on Supabase; product DB is DO.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260803_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PRODUCTS = (
    "airmet",
    "metar",
    "sigmet",
    "speci",
    "taf",
    "vaa",
    "tca",
    "swxa",
)
_STATUSES = ("draft", "wip", "finished", "failed")


def upgrade() -> None:
    """Create product tables for sessions + F8 ingest."""
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))

    op.create_table(
        "tac_work_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("manual_tac", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "pending_files",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "converted_results",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "errors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "issues",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "conversion_params",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("kv_upload_key", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "product IN (" + ", ".join(f"'{p}'" for p in _PRODUCTS) + ")",
            name="tac_work_sessions_product_check",
        ),
        sa.CheckConstraint(
            "status IN (" + ", ".join(f"'{s}'" for s in _STATUSES) + ")",
            name="tac_work_sessions_status_check",
        ),
    )

    op.execute(
        sa.text(
            """
            CREATE INDEX idx_tac_work_sessions_user_updated
              ON tac_work_sessions (user_id, updated_at DESC)
              WHERE deleted_at IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE INDEX idx_tac_work_sessions_user_product
              ON tac_work_sessions (user_id, product)
              WHERE deleted_at IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX tac_work_sessions_one_wip_per_user
              ON tac_work_sessions (user_id)
              WHERE status = 'wip' AND deleted_at IS NULL
            """
        )
    )

    op.create_table(
        "iwxxm_ingest_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("job_id", sa.Text(), nullable=False),
        sa.Column("product", sa.Text(), nullable=False),
        sa.Column("profile", sa.Text(), nullable=False, server_default="annex3"),
        sa.Column("source_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("tac_input", sa.Text(), nullable=False, server_default=""),
        sa.Column("iwxxm_xml", sa.Text(), nullable=False),
        sa.Column(
            "issues",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("stage_failed", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.execute(
        sa.text(
            """
            CREATE INDEX idx_iwxxm_ingest_results_job_created
              ON iwxxm_ingest_results (job_id, created_at DESC)
            """
        )
    )

    op.create_table(
        "iwxxm_ingest_quarantine",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("job_id", sa.Text(), nullable=False),
        sa.Column("product", sa.Text(), nullable=False),
        sa.Column("profile", sa.Text(), nullable=False, server_default="annex3"),
        sa.Column("source_url", sa.Text(), nullable=False, server_default=""),
        sa.Column("tac_input", sa.Text(), nullable=False, server_default=""),
        sa.Column("iwxxm_xml", sa.Text(), nullable=True),
        sa.Column(
            "issues",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("stage_failed", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.execute(
        sa.text(
            """
            CREATE INDEX idx_iwxxm_ingest_quarantine_job_created
              ON iwxxm_ingest_quarantine (job_id, created_at DESC)
            """
        )
    )


def downgrade() -> None:
    """Drop product tables."""
    op.execute(sa.text("DROP INDEX IF EXISTS idx_iwxxm_ingest_quarantine_job_created"))
    op.drop_table("iwxxm_ingest_quarantine")
    op.execute(sa.text("DROP INDEX IF EXISTS idx_iwxxm_ingest_results_job_created"))
    op.drop_table("iwxxm_ingest_results")
    op.execute(sa.text("DROP INDEX IF EXISTS tac_work_sessions_one_wip_per_user"))
    op.execute(sa.text("DROP INDEX IF EXISTS idx_tac_work_sessions_user_product"))
    op.execute(sa.text("DROP INDEX IF EXISTS idx_tac_work_sessions_user_updated"))
    op.drop_table("tac_work_sessions")
