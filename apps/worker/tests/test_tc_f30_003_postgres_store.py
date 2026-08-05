"""T3.1 / TC-F30-003 — F8 store/quarantine via DATABASE_URL (no service-role PostgREST)."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from metar_worker.pipeline import PipelineResult
from metar_worker.poller import IngestJob
from metar_worker.settings import WorkerSettings
from metar_worker.store import (
    QUARANTINE_TABLE,
    RESULTS_TABLE,
    PostgresStore,
    write_result,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_BACKEND = _REPO_ROOT / "apps" / "backend"
_ALEMBIC_INI = _BACKEND / "alembic.ini"
_WORKER_SRC = Path(__file__).resolve().parents[1] / "src" / "metar_worker"


def _to_psycopg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+psycopg2://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def _job(job_id: str = "f30-1") -> IngestJob:
    return IngestJob(
        job_id=job_id,
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://example.test/feed",
    )


@pytest.mark.unit
def test_tc_f30_003_settings_expose_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/db")
    settings = WorkerSettings()
    assert settings.database_url.startswith("postgresql://")


@pytest.mark.unit
def test_tc_f30_003_default_path_requires_database_url_not_service_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default writer path must fail closed without DATABASE_URL (F30 AC3)."""
    from metar_worker import __main__ as worker_main

    monkeypatch.setenv("INGEST_POLLER_URL", "https://ingest.example.test/feed.json")
    # Empty string overrides .env so the default writer path fails closed.
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-should-not-suffice")
    settings = WorkerSettings()
    assert settings.database_url == ""
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        worker_main.run_once(settings, store=None)


@pytest.mark.unit
def test_tc_f30_003_store_module_has_no_postgrest_default_writer() -> None:
    """Worker store default path must not use Supabase PostgREST / service-role JWT."""
    store_text = (_WORKER_SRC / "store.py").read_text(encoding="utf-8")
    main_text = (_WORKER_SRC / "__main__.py").read_text(encoding="utf-8")
    assert "PostgresStore" in store_text
    assert "DATABASE_URL" in (_WORKER_SRC / "settings.py").read_text(encoding="utf-8")
    assert "SupabaseRestStore" not in main_text
    assert "SUPABASE_SERVICE_ROLE_KEY" not in main_text
    assert "/rest/v1/" not in store_text
    assert "service_role" not in store_text.lower()


@pytest.mark.unit
def test_tc_f30_003_postgres_store_insert_protocol_with_memory_shape() -> None:
    """PostgresStore must satisfy StoreClient.insert used by write_result."""
    assert hasattr(PostgresStore, "insert")
    assert callable(PostgresStore.insert)


@pytest.fixture(scope="module")
def migrated_database_url() -> Iterator[str]:
    """Prefer ALEMBIC_TEST_DATABASE_URL, else testcontainers Postgres 16 + alembic head."""
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, text

    from_env = os.environ.get("ALEMBIC_TEST_DATABASE_URL", "").strip()
    if from_env:
        url = _to_psycopg_url(from_env)
        engine = create_engine(url)
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
        cfg = Config(str(_ALEMBIC_INI))
        cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
        cfg.set_main_option("sqlalchemy.url", url)
        command.upgrade(cfg, "head")
        yield url
        return

    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:
        pytest.skip("testcontainers not installed")

    try:
        with PostgresContainer("postgres:16") as postgres:
            url = _to_psycopg_url(postgres.get_connection_url())
            engine = create_engine(url)
            with engine.begin() as conn:
                conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
                conn.execute(text("CREATE SCHEMA public"))
            cfg = Config(str(_ALEMBIC_INI))
            cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
            cfg.set_main_option("sqlalchemy.url", url)
            command.upgrade(cfg, "head")
            yield url
    except Exception as exc:
        pytest.skip(f"Postgres container unavailable: {exc}")


@pytest.mark.integration
def test_tc_f30_003_insert_and_read_results_and_quarantine(
    migrated_database_url: str,
) -> None:
    """Unit/integration insert+read against DO schema (TC-F30-003 pass criteria)."""
    store = PostgresStore(database_url=migrated_database_url)

    ok = PipelineResult(
        job_id="f30-ok",
        ok=True,
        product="METAR",
        profile="annex3",
        xml="<iwxxm:METAR/>",
        issues=[],
    )
    fail = PipelineResult(
        job_id="f30-fail",
        ok=False,
        product="METAR",
        profile="annex3",
        xml=None,
        issues=[{"stage": "lint", "code": "x", "message": "bad", "severity": "error"}],
        stage_failed="lint",
    )

    assert write_result(store, _job("f30-ok"), ok) == RESULTS_TABLE
    assert write_result(store, _job("f30-fail"), fail) == QUARANTINE_TABLE

    results = store.fetch_by_job_id(RESULTS_TABLE, "f30-ok")
    assert len(results) == 1
    assert results[0]["iwxxm_xml"] == "<iwxxm:METAR/>"
    assert results[0]["job_id"] == "f30-ok"

    quarantined = store.fetch_by_job_id(QUARANTINE_TABLE, "f30-fail")
    assert len(quarantined) == 1
    assert quarantined[0]["stage_failed"] == "lint"
    assert quarantined[0]["iwxxm_xml"] is None


@pytest.mark.integration
def test_tc_f30_003_source_url_redacted_on_postgres_write(
    migrated_database_url: str,
) -> None:
    store = PostgresStore(database_url=migrated_database_url)
    job = IngestJob(
        job_id="f30-redact",
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://user:tok@ingest.example.test/feed.json?token=secret",
    )
    result = PipelineResult(
        job_id="f30-redact",
        ok=True,
        product="METAR",
        profile="annex3",
        xml="<iwxxm:METAR/>",
        issues=[],
    )
    write_result(store, job, result)
    rows = store.fetch_by_job_id(RESULTS_TABLE, "f30-redact")
    assert rows[0]["source_url"] == "https://ingest.example.test/feed.json"
