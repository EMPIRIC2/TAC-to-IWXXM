"""T5.3 / TC-EV031-001 — migrate dry-run / apply helpers."""

from __future__ import annotations

import pytest
from scripts.ops.run_supabase_to_do_migrate import (
    COPY_COLUMNS,
    build_insert_sql,
    urls_are_same_database,
)
from scripts.ops.verify_supabase_to_do_migrate import PRODUCT_TABLES


@pytest.mark.unit
def test_copy_columns_cover_product_tables() -> None:
    assert set(COPY_COLUMNS) == set(PRODUCT_TABLES)
    for table, cols in COPY_COLUMNS.items():
        assert cols[0] == "id", table
        assert "id" in cols


@pytest.mark.unit
def test_urls_are_same_database_ignores_password_and_dialect() -> None:
    a = "postgresql+psycopg2://u:secret1@db.example.com:5432/postgres"
    b = "postgresql://u:secret2@db.example.com:5432/postgres"
    assert urls_are_same_database(a, b) is True
    c = "postgresql://u:secret@other.example.com:5432/postgres"
    assert urls_are_same_database(a, c) is False


@pytest.mark.unit
def test_build_insert_sql_is_idempotent_on_conflict() -> None:
    sql = build_insert_sql(
        "tac_work_sessions",
        ("id", "user_id", "product"),
    )
    assert 'INSERT INTO "tac_work_sessions"' in sql
    assert "ON CONFLICT" in sql
    assert "DO NOTHING" in sql
    assert ":id" in sql and ":user_id" in sql


@pytest.mark.unit
def test_build_insert_sql_requires_id() -> None:
    with pytest.raises(ValueError, match="must include id"):
        build_insert_sql("tac_work_sessions", ("user_id", "product"))
