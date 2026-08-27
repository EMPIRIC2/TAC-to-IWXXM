"""Versioned IWXXM writer-contract DDL and schema-diff (F16 / ADR-030).

Contract version ``1`` targets table ``iwxxm_reports`` used by multi-DB upload sinks.
"""

from __future__ import annotations

from enum import StrEnum

import msgspec
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

CONTRACT_VERSION = "1"
CONTRACT_TABLE = "iwxxm_reports"

# Logical column names required by contract v1 (types mapped per dialect).
REQUIRED_COLUMNS: tuple[str, ...] = (
    "id",
    "product",
    "icao",
    "observation_time",
    "iwxxm_version",
    "iwxxm_xml",
    "tac_text",
    "upload_key",
    "created_at",
)


class DiffKind(StrEnum):
    MISSING_TABLE = "missing_table"
    MISSING_COLUMN = "missing_column"
    TYPE_MISMATCH = "type_mismatch"


class SchemaDiff(msgspec.Struct, frozen=True):
    """One actionable preflight schema difference."""

    kind: DiffKind
    table: str
    detail: str
    column: str | None = None


def writer_contract_ddl(dialect: str) -> str:
    """
    Return CREATE TABLE DDL for the writer contract on ``dialect``.

    Parameters
    ----------
    dialect :
        ``postgresql``, ``mysql``, ``sqlite``, or ``mssql`` / ``sqlserver`` (aioodbc).

    Returns
    -------
    str
        Dialect-specific DDL statement(s).
    """
    d = dialect.lower()
    if d in {"postgresql", "postgres"}:
        return _ddl_postgres()
    if d in {"mysql", "mariadb"}:
        return _ddl_mysql()
    if d == "sqlite":
        return _ddl_sqlite()
    if d in {"mssql", "sqlserver"}:
        return _ddl_mssql()
    raise ValueError(f"unsupported writer-contract dialect: {dialect}")


async def diff_writer_contract(
    engine: AsyncEngine,
    *,
    dialect: str | None = None,
) -> list[SchemaDiff]:
    """
    Compare the live database to writer-contract v1.

    Parameters
    ----------
    engine :
        SQLAlchemy async engine.
    dialect :
        Optional override; defaults to ``engine.dialect.name``.

    Returns
    -------
    list[SchemaDiff]
        Empty when the schema matches the contract.
    """
    name = (dialect or engine.dialect.name).lower()
    if name == "postgres":
        name = "postgresql"

    async with engine.connect() as conn:
        return await _diff_on_connection(conn, dialect=name)


async def apply_writer_contract(
    engine: AsyncEngine,
    *,
    dialect: str | None = None,
) -> None:
    """Create the writer-contract table if missing (create-if-missing path)."""
    name = (dialect or engine.dialect.name).lower()
    if name == "postgres":
        name = "postgresql"
    ddl = writer_contract_ddl(name)
    async with engine.begin() as conn:
        for stmt in _split_statements(ddl):
            await conn.execute(text(stmt))


async def _diff_on_connection(conn: AsyncConnection, *, dialect: str) -> list[SchemaDiff]:
    def _inspect(sync_conn: object) -> list[SchemaDiff]:
        insp = inspect(sync_conn)
        if not insp.has_table(CONTRACT_TABLE):
            return [
                SchemaDiff(
                    kind=DiffKind.MISSING_TABLE,
                    table=CONTRACT_TABLE,
                    detail=f"table {CONTRACT_TABLE!r} missing (contract v{CONTRACT_VERSION})",
                )
            ]
        cols = {c["name"].lower() for c in insp.get_columns(CONTRACT_TABLE)}
        out: list[SchemaDiff] = []
        out.extend(
            SchemaDiff(
                kind=DiffKind.MISSING_COLUMN,
                table=CONTRACT_TABLE,
                column=required,
                detail=f"column {required!r} missing on {CONTRACT_TABLE}",
            )
            for required in REQUIRED_COLUMNS
            if required not in cols
        )
        return out

    return await conn.run_sync(_inspect)


def _split_statements(ddl: str) -> list[str]:
    parts = [p.strip() for p in ddl.split(";")]
    return [p for p in parts if p]


def _ddl_sqlite() -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {CONTRACT_TABLE} (
  id TEXT PRIMARY KEY,
  product TEXT NOT NULL,
  icao TEXT,
  observation_time TEXT,
  iwxxm_version TEXT NOT NULL,
  iwxxm_xml TEXT NOT NULL,
  tac_text TEXT,
  upload_key TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
""".strip()


def _ddl_postgres() -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {CONTRACT_TABLE} (
  id UUID PRIMARY KEY,
  product TEXT NOT NULL,
  icao TEXT,
  observation_time TIMESTAMPTZ,
  iwxxm_version TEXT NOT NULL,
  iwxxm_xml TEXT NOT NULL,
  tac_text TEXT,
  upload_key TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""".strip()


def _ddl_mysql() -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {CONTRACT_TABLE} (
  id CHAR(36) PRIMARY KEY,
  product VARCHAR(32) NOT NULL,
  icao VARCHAR(8) NULL,
  observation_time DATETIME(6) NULL,
  iwxxm_version VARCHAR(32) NOT NULL,
  iwxxm_xml LONGTEXT NOT NULL,
  tac_text MEDIUMTEXT NULL,
  upload_key VARCHAR(128) NULL,
  created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
);
""".strip()


def _ddl_mssql() -> str:
    return f"""
IF OBJECT_ID(N'{CONTRACT_TABLE}', N'U') IS NULL
CREATE TABLE {CONTRACT_TABLE} (
  id UNIQUEIDENTIFIER PRIMARY KEY,
  product NVARCHAR(32) NOT NULL,
  icao NVARCHAR(8) NULL,
  observation_time DATETIMEOFFSET NULL,
  iwxxm_version NVARCHAR(32) NOT NULL,
  iwxxm_xml NVARCHAR(MAX) NOT NULL,
  tac_text NVARCHAR(MAX) NULL,
  upload_key NVARCHAR(128) NULL,
  created_at DATETIMEOFFSET NOT NULL DEFAULT SYSDATETIMEOFFSET()
);
""".strip()
