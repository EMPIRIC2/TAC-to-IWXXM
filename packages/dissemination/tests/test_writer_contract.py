"""Writer-contract schema diff and DDL create-if-missing tests (T2.1 / TC-F16-003)."""

from __future__ import annotations

import pytest
from dissemination.writer_contract import (
    CONTRACT_VERSION,
    DiffKind,
    SchemaDiff,
    apply_writer_contract,
    diff_writer_contract,
    writer_contract_ddl,
)
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


@pytest.fixture
async def sqlite_engine() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    yield engine
    await engine.dispose()


@pytest.mark.asyncio
async def test_diff_missing_table_on_empty_sqlite(sqlite_engine: AsyncEngine) -> None:
    diffs = await diff_writer_contract(sqlite_engine, dialect="sqlite")
    assert any(d.kind == DiffKind.MISSING_TABLE for d in diffs)
    assert CONTRACT_VERSION == "1"


@pytest.mark.asyncio
async def test_apply_then_diff_is_empty_sqlite(sqlite_engine: AsyncEngine) -> None:
    await apply_writer_contract(sqlite_engine, dialect="sqlite")
    diffs = await diff_writer_contract(sqlite_engine, dialect="sqlite")
    assert diffs == []


@pytest.mark.asyncio
async def test_postgres_dialect_alias_normalized(sqlite_engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch) -> None:
    # Alias ``postgres`` → ``postgresql`` (writer_contract lines 95/109).
    seen: list[str] = []

    async def _fake_diff(_conn: object, *, dialect: str) -> list[SchemaDiff]:
        seen.append(dialect)
        return []

    monkeypatch.setattr(
        "dissemination.writer_contract._diff_on_connection",
        _fake_diff,
    )
    assert await diff_writer_contract(sqlite_engine, dialect="postgres") == []
    assert seen == ["postgresql"]

    ddl_seen: list[str] = []

    def _fake_ddl(dialect: str) -> str:
        ddl_seen.append(dialect)
        return "SELECT 1"

    monkeypatch.setattr(
        "dissemination.writer_contract.writer_contract_ddl",
        _fake_ddl,
    )
    await apply_writer_contract(sqlite_engine, dialect="postgres")
    assert ddl_seen == ["postgresql"]


@pytest.mark.asyncio
async def test_diff_reports_missing_column_sqlite(sqlite_engine: AsyncEngine) -> None:
    await apply_writer_contract(sqlite_engine, dialect="sqlite")
    async with sqlite_engine.begin() as conn:
        await conn.exec_driver_sql("ALTER TABLE iwxxm_reports DROP COLUMN tac_text")
    diffs = await diff_writer_contract(sqlite_engine, dialect="sqlite")
    assert any(d.kind == DiffKind.MISSING_COLUMN and d.column == "tac_text" for d in diffs)


def test_writer_contract_ddl_per_engine_mentions_core_columns() -> None:
    for dialect in ("postgresql", "mysql", "sqlite", "mssql"):
        ddl = writer_contract_ddl(dialect)
        assert "iwxxm_reports" in ddl
        assert "iwxxm_xml" in ddl
        assert "upload_key" in ddl


def test_writer_contract_ddl_rejects_unknown_dialect() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        writer_contract_ddl("oracle")


@pytest.mark.asyncio
async def test_diff_uses_engine_dialect_name(sqlite_engine: AsyncEngine) -> None:
    await apply_writer_contract(sqlite_engine)
    diffs = await diff_writer_contract(sqlite_engine)
    assert diffs == []


def test_schema_diff_is_msgspec_friendly_struct() -> None:
    d = SchemaDiff(kind=DiffKind.MISSING_TABLE, table="iwxxm_reports", detail="absent")
    assert d.table == "iwxxm_reports"
    assert d.kind == DiffKind.MISSING_TABLE
