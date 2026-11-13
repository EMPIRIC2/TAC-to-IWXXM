"""Station health tracking tables (F39).

Revision ID: 20261113_0010
Revises: 20261003_0009
Create Date: 2026-11-13

Dedicated station issuance and grade tables. Work sessions stay operator WIP.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261113_0010"
down_revision: str | None = "20261003_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Create station health tables and seed metric definitions.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (upgrade)
    2
    """
    op.create_table(
        "station_registry",
        sa.Column("icao", sa.String(length=4), primary_key=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "station_tac_records",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("icao", sa.String(length=4), nullable=False),
        sa.Column("product", sa.String(length=16), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tac_text", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("solidus_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_digit_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lint_error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lint_warning_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("convert_ok", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["icao"], ["station_registry.icao"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_station_tac_records_icao_product_observed",
        "station_tac_records",
        ["icao", "product", "observed_at"],
    )
    op.create_index(
        "ix_station_tac_records_observed",
        "station_tac_records",
        ["observed_at"],
    )
    op.create_table(
        "station_metric_definitions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("higher_is_better", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "station_health_grades",
        sa.Column("icao", sa.String(length=4), nullable=False),
        sa.Column("product", sa.String(length=16), nullable=False),
        sa.Column("window_key", sa.String(length=8), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("actual_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("availability_score", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column("solidus_rate", sa.Numeric(8, 5), nullable=False, server_default="0"),
        sa.Column("missing_digit_rate", sa.Numeric(8, 5), nullable=False, server_default="0"),
        sa.Column("lint_severity_score", sa.Numeric(6, 2), nullable=False, server_default="100"),
        sa.Column("overall_score", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column("overall_grade", sa.String(length=1), nullable=False, server_default="F"),
        sa.Column("metrics", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.PrimaryKeyConstraint("icao", "product", "window_key"),
        sa.ForeignKeyConstraint(["icao"], ["station_registry.icao"], ondelete="CASCADE"),
    )
    metrics = sa.table(
        "station_metric_definitions",
        sa.column("id", sa.String),
        sa.column("label", sa.Text),
        sa.column("description", sa.Text),
        sa.column("unit", sa.String),
        sa.column("higher_is_better", sa.Boolean),
        sa.column("enabled", sa.Boolean),
        sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(
        metrics,
        [
            {
                "id": "availability",
                "label": "Availability",
                "description": "Share of expected TAC reports received in the window",
                "unit": "percent",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 10,
            },
            {
                "id": "solidus_rate",
                "label": "Solidus rate",
                "description": "Share of solidus characters in received TAC text",
                "unit": "ratio",
                "higher_is_better": False,
                "enabled": True,
                "sort_order": 20,
            },
            {
                "id": "missing_digit_rate",
                "label": "Missing digit rate",
                "description": "Average missing-digit solidus runs per report",
                "unit": "ratio",
                "higher_is_better": False,
                "enabled": True,
                "sort_order": 30,
            },
            {
                "id": "lint_severity",
                "label": "Lint severity",
                "description": "Quality score from stored lint error and warning counts",
                "unit": "percent",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 40,
            },
            {
                "id": "overall_grade",
                "label": "Overall grade",
                "description": "Combined availability and quality letter grade",
                "unit": "letter",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 50,
            },
        ],
    )


def downgrade() -> None:
    """
    Drop station health tables.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (downgrade)
    2
    """
    op.drop_table("station_health_grades")
    op.drop_table("station_metric_definitions")
    op.drop_index("ix_station_tac_records_observed", table_name="station_tac_records")
    op.drop_index(
        "ix_station_tac_records_icao_product_observed",
        table_name="station_tac_records",
    )
    op.drop_table("station_tac_records")
    op.drop_table("station_registry")
