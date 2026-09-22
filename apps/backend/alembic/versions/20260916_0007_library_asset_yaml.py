"""Library YAML lifecycle columns (EVPYL Phase C).

Revision ID: 20260916_0007
Revises: 20260914_0006
Create Date: 2026-09-16

Adds yaml_body, status (draft|activated), and schema_version on custom
library assets. First-party builtins stay code-served.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260916_0007"
down_revision: str | None = "20260914_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add YAML document + lifecycle columns."""
    op.add_column("tac_library_assets", sa.Column("yaml_body", sa.Text(), nullable=True))
    op.add_column(
        "tac_library_assets",
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'draft'")),
    )
    op.add_column(
        "tac_library_assets",
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.create_check_constraint(
        "ck_tac_library_assets_status",
        "tac_library_assets",
        "status IN ('draft','activated')",
    )


def downgrade() -> None:
    """Drop YAML document + lifecycle columns."""
    op.drop_constraint("ck_tac_library_assets_status", "tac_library_assets", type_="check")
    op.drop_column("tac_library_assets", "schema_version")
    op.drop_column("tac_library_assets", "status")
    op.drop_column("tac_library_assets", "yaml_body")
