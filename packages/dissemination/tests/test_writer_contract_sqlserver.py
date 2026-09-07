"""SQL Server writer-contract via aioodbc (T2.6 / TC-F16-003 / E14-06).

Live engine tests require Docker (Testcontainers) **and** a system ODBC SQL Server
driver (e.g. Microsoft ODBC Driver 18). Without ODBC, cases skip - CI may omit ODBC.
Driver install notes: ``docs/deploy.md`` §SQL Server ODBC and this package README.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import pytest
from dissemination.db_preflight import dialect_for_sink, normalize_sqlalchemy_uri
from dissemination.odbc import (
    odbc_sqlserver_available,
    preferred_sqlserver_odbc_driver,
)
from dissemination.writer_contract import DiffKind, apply_writer_contract, diff_writer_contract
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

pytestmark = pytest.mark.integration


def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            capture_output=True,
            timeout=15,
        )
        return True
    except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired):
        return False


requires_docker_and_odbc = pytest.mark.skipif(
    not (_docker_available() and odbc_sqlserver_available()),
    reason=("Docker + SQL Server ODBC driver required for aioodbc path (T2.6 / E14-06; CI skips when ODBC absent)"),
)


def _with_odbc_driver(url: str) -> str:
    """Attach preferred ODBC driver + TrustServerCertificate for container TLS."""
    driver = preferred_sqlserver_odbc_driver()
    if driver is None:
        return url
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    q.setdefault("driver", driver)
    q.setdefault("TrustServerCertificate", "yes")
    return urlunparse(parsed._replace(query=urlencode(q)))


def _to_aioodbc_url(url: str) -> str:
    return _with_odbc_driver(normalize_sqlalchemy_uri(url, "sqlserver"))


@contextmanager
def _mssql_async_url() -> Iterator[str]:
    from testcontainers.mssql import SqlServerContainer

    with SqlServerContainer("mcr.microsoft.com/mssql/server:2022-latest") as mssql:
        yield _to_aioodbc_url(mssql.get_connection_url())


@pytest.fixture
async def mssql_engine() -> AsyncIterator[AsyncEngine]:
    with _mssql_async_url() as url:
        engine = create_async_engine(url)
        try:
            yield engine
        finally:
            await engine.dispose()


def test_normalize_sqlserver_uri_to_aioodbc() -> None:
    assert dialect_for_sink("sqlserver") == "mssql"
    assert normalize_sqlalchemy_uri("mssql://SA:x@h:1433/db", "sqlserver").startswith("mssql+aioodbc://")
    assert normalize_sqlalchemy_uri("mssql+pymssql://SA:x@h:1433/db", "sqlserver").startswith("mssql+aioodbc://")
    assert normalize_sqlalchemy_uri("mssql+pyodbc://SA:x@h:1433/db", "sqlserver").startswith("mssql+aioodbc://")
    already = "mssql+aioodbc://SA:x@h:1433/db?driver=ODBC+Driver+18+for+SQL+Server"
    assert normalize_sqlalchemy_uri(already, "sqlserver") == already


def test_odbc_probe_returns_bool() -> None:
    assert isinstance(odbc_sqlserver_available(), bool)


@requires_docker_and_odbc
@pytest.mark.asyncio
async def test_mssql_happy_apply_then_empty_diff(mssql_engine: AsyncEngine) -> None:
    await apply_writer_contract(mssql_engine, dialect="mssql")
    assert await diff_writer_contract(mssql_engine, dialect="mssql") == []


@requires_docker_and_odbc
@pytest.mark.asyncio
async def test_mssql_mismatch_missing_table(mssql_engine: AsyncEngine) -> None:
    diffs = await diff_writer_contract(mssql_engine, dialect="mssql")
    assert any(d.kind == DiffKind.MISSING_TABLE for d in diffs)


@requires_docker_and_odbc
@pytest.mark.asyncio
async def test_mssql_mismatch_missing_column(mssql_engine: AsyncEngine) -> None:
    await apply_writer_contract(mssql_engine, dialect="mssql")
    async with mssql_engine.begin() as conn:
        await conn.execute(text("ALTER TABLE iwxxm_reports DROP COLUMN upload_key"))
    diffs = await diff_writer_contract(mssql_engine, dialect="mssql")
    assert any(d.kind == DiffKind.MISSING_COLUMN and d.column == "upload_key" for d in diffs)
