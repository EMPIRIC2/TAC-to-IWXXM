"""T2.1 / TC-EV031-002 - empty DB → head; second ``upgrade head`` is a no-op.

Requires Docker (testcontainers) or ``DATABASE_URL`` pointing at an empty disposable
Postgres. Skips when neither is available (local without Docker).
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _REPO_ROOT / "apps" / "backend"
_ALEMBIC_INI = _BACKEND / "alembic.ini"

REQUIRED_SESSION_COLUMNS = frozenset(
    {
        "id",
        "user_id",
        "product",
        "status",
        "title",
        "manual_tac",
        "pending_files",
        "converted_results",
        "errors",
        "issues",
        "conversion_params",
        "kv_upload_key",
        "deleted_at",
        "created_at",
        "updated_at",
    }
)


def _to_psycopg_url(url: str) -> str:
    """Normalize container/env URLs to SQLAlchemy psycopg v3 dialect."""
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+psycopg2://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


@pytest.fixture(scope="module")
def alembic_database_url() -> Iterator[str]:
    """Prefer ``ALEMBIC_TEST_DATABASE_URL``, else testcontainers Postgres 16."""
    from_env = os.environ.get("ALEMBIC_TEST_DATABASE_URL", "").strip()
    if from_env:
        yield _to_psycopg_url(from_env)
        return

    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:
        pytest.skip("testcontainers not installed")

    try:
        with PostgresContainer("postgres:16") as postgres:
            yield _to_psycopg_url(postgres.get_connection_url())
    except Exception as exc:
        pytest.skip(f"Postgres container unavailable: {exc}")


def _run_upgrade_head(url: str) -> None:
    from alembic import command
    from alembic.config import Config

    assert _ALEMBIC_INI.is_file(), f"missing {_ALEMBIC_INI}"
    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")


@pytest.mark.integration
def test_alembic_upgrade_head_twice_idempotent(alembic_database_url: str) -> None:
    url = alembic_database_url
    engine = create_engine(url)

    with engine.begin() as conn:
        # Disposable: wipe public schema so first upgrade starts from empty.
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))

    _run_upgrade_head(url)
    _run_upgrade_head(url)  # second pass must be a no-op (Alembic version table)

    insp = inspect(engine)
    assert "tac_work_sessions" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("tac_work_sessions")}
    missing = REQUIRED_SESSION_COLUMNS - cols
    assert not missing, f"tac_work_sessions missing columns: {sorted(missing)}"

    assert "iwxxm_ingest_results" in insp.get_table_names()
    assert "iwxxm_ingest_quarantine" in insp.get_table_names()

    with engine.connect() as conn:
        ver = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert ver  # at head
        # Product CHECK includes swxa (F28 / ADR-020 deepen).
        check_rows = conn.execute(
            text(
                """
                SELECT pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid = 'public.tac_work_sessions'::regclass
                  AND contype = 'c'
                """
            )
        ).fetchall()
        check_sql = " ".join(row[0] for row in check_rows)
        assert "swxa" in check_sql
        assert "auth.users" not in check_sql
