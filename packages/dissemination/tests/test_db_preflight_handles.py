"""Handle store + db_preflight unit tests (coverage for T2.3/T2.4 helpers)."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

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
    with pytest.raises(ValueError):
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
    h = store.create(
        user_id="a", sink_type="sqlite", uri="sqlite:///:memory:", now=1000.0
    )
    assert store.get(h, user_id="a", now=1005.0) is not None
    assert store.get(h, user_id="a", now=1020.0) is None
    store.create(user_id="a", sink_type="sqlite", uri="x", now=2000.0)
    store.clear()
    assert store.pop("missing", user_id="a") is None


def test_normalize_mysql_and_sqlite_prefixes() -> None:
    assert normalize_sqlalchemy_uri("mysql://h/db", "mysql").startswith("mysql+aiomysql://")
    assert normalize_sqlalchemy_uri("sqlite:///tmp/x.db", "sqlite").startswith(
        "sqlite+aiosqlite://"
    )


@pytest.mark.asyncio
async def test_run_db_preflight_requires_uri() -> None:
    with pytest.raises(ValueError, match="uri is required"):
        await run_db_preflight(PreflightRequest(sink_type="sqlite", uri=None))
