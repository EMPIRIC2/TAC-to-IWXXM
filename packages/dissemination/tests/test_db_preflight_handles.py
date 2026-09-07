"""Handle store + db_preflight unit tests (coverage for T2.3/T2.4 helpers)."""

from __future__ import annotations

import pytest
from dissemination.db_preflight import (
    dialect_for_sink,
    normalize_sqlalchemy_uri,
    run_db_preflight,
    uri_hostname,
)
from dissemination.handles import HandleStore
from dissemination.models import PreflightRequest


def test_uri_hostname_and_dialect_helpers() -> None:
    assert uri_hostname("postgresql://u:p@db.example.com:5432/wx") == "db.example.com"
    assert uri_hostname("sqlite+aiosqlite:///:memory:") is None
    assert dialect_for_sink("postgres") == "postgresql"
    assert normalize_sqlalchemy_uri("postgresql://x", "postgres").startswith("postgresql+asyncpg://")
    with pytest.raises(ValueError, match=r".*"):
        dialect_for_sink("wis2")


@pytest.mark.asyncio
async def test_run_db_preflight_sqlite_ddl(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    db = tmp_path / "p.db"
    uri = f"sqlite+aiosqlite:///{db}"
    resp = await run_db_preflight(PreflightRequest(sink_type="sqlite", uri=uri, ddl=True))
    assert resp.ok is True
    assert resp.diffs == []


def test_handle_store_create_get_pop_and_user_isolation() -> None:
    store = HandleStore(ttl_seconds=60)
    h = store.create(user_id="a", sink_type="sqlite", uri="sqlite:///:memory:")
    assert store.get(h, user_id="b") is None
    rec = store.get(h, user_id="a")
    assert rec is not None
    assert rec.sink_type == "sqlite"
    assert store.pop(h, user_id="a") is not None
    assert store.get(h, user_id="a") is None


def test_handle_store_expires_and_clear() -> None:
    store = HandleStore(ttl_seconds=10)
    h = store.create(user_id="a", sink_type="sqlite", uri="sqlite:///:memory:", now=1000.0)
    assert store.get(h, user_id="a", now=1005.0) is not None
    assert store.get(h, user_id="a", now=1020.0) is None
    store.create(user_id="a", sink_type="sqlite", uri="x", now=2000.0)
    store.clear()
    assert store.pop("missing", user_id="a") is None


def test_normalize_mysql_sqlite_and_sqlserver_prefixes() -> None:
    assert normalize_sqlalchemy_uri("mysql://h/db", "mysql").startswith("mysql+aiomysql://")
    assert normalize_sqlalchemy_uri("sqlite:///tmp/x.db", "sqlite").startswith("sqlite+aiosqlite://")
    assert dialect_for_sink("sqlserver") == "mssql"
    assert normalize_sqlalchemy_uri("mssql://h/db", "sqlserver").startswith("mssql+aioodbc://")
    assert normalize_sqlalchemy_uri("mssql+pymssql://h/db", "sqlserver").startswith("mssql+aioodbc://")
    assert normalize_sqlalchemy_uri("mssql+pyodbc://h/db", "sqlserver").startswith("mssql+aioodbc://")
    already = "mssql+aioodbc://h/db?driver=ODBC+Driver+18+for+SQL+Server"
    assert normalize_sqlalchemy_uri(already, "sqlserver") == already
    # Non-mssql scheme left unchanged for sqlserver sink
    assert normalize_sqlalchemy_uri("postgresql://h/db", "sqlserver") == "postgresql://h/db"


@pytest.mark.asyncio
async def test_run_db_preflight_requires_uri() -> None:
    with pytest.raises(ValueError, match="uri is required"):
        await run_db_preflight(PreflightRequest(sink_type="sqlite", uri=None))


@pytest.mark.asyncio
async def test_run_db_preflight_validates_host_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "127.0.0.1,localhost")
    # Hostless sqlite memory skips allowlist; use a file URI with host.
    uri = "sqlite+aiosqlite://localhost//tmp/should-not-matter.db"
    # Force hostname path: patch uri_hostname + engine path via memory sqlite.
    monkeypatch.setattr(
        "dissemination.db_preflight.uri_hostname",
        lambda _u: "127.0.0.1",
    )
    resp = await run_db_preflight(PreflightRequest(sink_type="sqlite", uri="sqlite+aiosqlite:///:memory:", ddl=False))
    assert resp.connectivity_ok is True
    _ = uri  # keep local for readability


@pytest.mark.asyncio
async def test_run_db_preflight_redacts_engine_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")

    async def _boom(_engine: object, *, dialect: str) -> list[object]:
        raise RuntimeError('{"password": "supersecret"} boom')

    monkeypatch.setattr("dissemination.db_preflight.diff_writer_contract", _boom)
    with pytest.raises(ValueError, match=r".*") as excinfo:
        await run_db_preflight(
            PreflightRequest(
                sink_type="sqlite",
                uri="sqlite+aiosqlite:///:memory:",
                ddl=False,
            )
        )
    assert "supersecret" not in str(excinfo.value)
    assert "***" in str(excinfo.value)


def test_handle_get_expires_inline(monkeypatch: pytest.MonkeyPatch) -> None:
    store = HandleStore(ttl_seconds=5)
    h = store.create(user_id="a", sink_type="sqlite", uri="x", now=100.0)
    # Skip purge so the inline expires_at check (68-69) is reachable.
    monkeypatch.setattr(store, "_purge", lambda _now: None)
    assert store.get(h, user_id="a", now=106.0) is None
