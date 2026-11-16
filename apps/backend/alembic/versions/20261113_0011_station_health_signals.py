"""Station health format, issue codes, retention metrics (F39).

Revision ID: 20261113_0011
Revises: 20261113_0010
Create Date: 2026-11-13

Adds file_format and issue_codes on observation rows, and seeds metric
definitions for maintenance tags, formats, issue counts, and Centennial
proxies.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261113_0011"
down_revision: str | None = "20261113_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add signal columns and seed metric definitions.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (upgrade)
    2
    """
    op.add_column(
        "station_tac_records",
        sa.Column(
            "file_format",
            sa.String(length=32),
            nullable=False,
            server_default="tac",
        ),
    )
    op.add_column(
        "station_tac_records",
        sa.Column(
            "issue_codes",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
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
                "id": "maintenance_tags",
                "label": "Maintenance tags",
                "description": "Counts of maintenance and sensor-outage tags in TAC text",
                "unit": "count",
                "higher_is_better": False,
                "enabled": True,
                "sort_order": 60,
            },
            {
                "id": "file_formats",
                "label": "File formats",
                "description": "Counts of stored payload formats per station",
                "unit": "count",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 70,
            },
            {
                "id": "issue_codes",
                "label": "Lint and validation issues",
                "description": "Counts of lint and validation issue identifiers",
                "unit": "count",
                "higher_is_better": False,
                "enabled": True,
                "sort_order": 80,
            },
            {
                "id": "centennial_continuity",
                "label": "Observing continuity",
                "description": (
                    "Availability proxy aligned with Centennial continuity "
                    "(90 percent or better when a report cadence exists)"
                ),
                "unit": "percent",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 90,
            },
            {
                "id": "centennial_metadata",
                "label": "Station metadata",
                "description": "Completeness of live station registry fields",
                "unit": "percent",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 100,
            },
            {
                "id": "centennial_quality",
                "label": "Observation quality",
                "description": "Quality proxy from solidus, missing digits, and lint severity",
                "unit": "percent",
                "higher_is_better": True,
                "enabled": True,
                "sort_order": 110,
            },
        ],
    )


def downgrade() -> None:
    """
    Drop signal columns and seeded metrics.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (downgrade)
    2
    """
    op.execute(
        sa.text(
            "DELETE FROM station_metric_definitions WHERE id IN "
            "('maintenance_tags', 'file_formats', 'issue_codes', "
            "'centennial_continuity', 'centennial_metadata', 'centennial_quality')"
        )
    )
    op.drop_column("station_tac_records", "issue_codes")
    op.drop_column("station_tac_records", "file_format")
