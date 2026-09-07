"""Compose/Testcontainers multi-DB writer-contract (T2.5 / TC-F16-003 / E14-09).

Happy path: apply DDL then empty schema diff.
Mismatch path: missing table / missing column reported per engine.
Postgres + MySQL use Testcontainers when Docker is available; SQLite is in-process.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager

import pytest
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


requires_docker = pytest.mark.skipif(
    not _docker_available(),
    reason="Docker required for Postgres/MySQL Testcontainers (T2.5 / E14-09)",
)


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql+psycopg2://")
    if url.startswith("postgresql+psycopg://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql+psycopg://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


def _to_aiomysql_url(url: str) -> str:
    if url.startswith("mysql+aiomysql://"):
        return url
    if url.startswith("mysql+pymysql://"):
        return "mysql+aiomysql://" + url.removeprefix("mysql+pymysql://")
    if url.startswith("mysql://"):
        return "mysql+aiomysql://" + url.removeprefix("mysql://")
    return url


@contextmanager
def _postgres_async_url() -> Iterator[str]:
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine", driver=None) as pg:
        yield _to_asyncpg_url(pg.get_connection_url())


@contextmanager
def _mysql_async_url() -> Iterator[str]:
    from testcontainers.mysql import MySqlContainer

    with MySqlContainer("mysql:8.4") as mysql:
        yield _to_aiomysql_url(mysql.get_connection_url())


@pytest.fixture
async def sqlite_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def postgres_engine() -> AsyncIterator[AsyncEngine]:
    with _postgres_async_url() as url:
        engine = create_async_engine(url)
        try:
            yield engine
        finally:
            await engine.dispose()


@pytest.fixture
async def mysql_engine() -> AsyncIterator[AsyncEngine]:
    with _mysql_async_url() as url:
        engine = create_async_engine(url)
        try:
            yield engine
        finally:
            await engine.dispose()


@pytest.mark.asyncio
async def test_sqlite_happy_apply_then_empty_diff(sqlite_engine: AsyncEngine) -> None:
    await apply_writer_contract(sqlite_engine, dialect="sqlite")
    assert await diff_writer_contract(sqlite_engine, dialect="sqlite") == []


@pytest.mark.asyncio
async def test_sqlite_mismatch_missing_table(sqlite_engine: AsyncEngine) -> None:
    diffs = await diff_writer_contract(sqlite_engine, dialect="sqlite")
    assert any(d.kind == DiffKind.MISSING_TABLE for d in diffs)


@pytest.mark.asyncio
async def test_sqlite_mismatch_missing_column(sqlite_engine: AsyncEngine) -> None:
    await apply_writer_contract(sqlite_engine, dialect="sqlite")
    async with sqlite_engine.begin() as conn:
        await conn.execute(text("ALTER TABLE iwxxm_reports DROP COLUMN upload_key"))
    diffs = await diff_writer_contract(sqlite_engine, dialect="sqlite")
    assert any(d.kind == DiffKind.MISSING_COLUMN and d.column == "upload_key" for d in diffs)


@requires_docker
@pytest.mark.asyncio
async def test_postgres_happy_apply_then_empty_diff(postgres_engine: AsyncEngine) -> None:
    await apply_writer_contract(postgres_engine, dialect="postgresql")
    assert await diff_writer_contract(postgres_engine, dialect="postgresql") == []


@requires_docker
@pytest.mark.asyncio
async def test_postgres_mismatch_missing_table(postgres_engine: AsyncEngine) -> None:
    diffs = await diff_writer_contract(postgres_engine, dialect="postgresql")
    assert any(d.kind == DiffKind.MISSING_TABLE for d in diffs)


@requires_docker
@pytest.mark.asyncio
async def test_postgres_mismatch_missing_column(postgres_engine: AsyncEngine) -> None:
    await apply_writer_contract(postgres_engine, dialect="postgresql")
    async with postgres_engine.begin() as conn:
        await conn.execute(text("ALTER TABLE iwxxm_reports DROP COLUMN upload_key"))
    diffs = await diff_writer_contract(postgres_engine, dialect="postgresql")
    assert any(d.kind == DiffKind.MISSING_COLUMN and d.column == "upload_key" for d in diffs)


@requires_docker
@pytest.mark.asyncio
async def test_mysql_happy_apply_then_empty_diff(mysql_engine: AsyncEngine) -> None:
    await apply_writer_contract(mysql_engine, dialect="mysql")
    assert await diff_writer_contract(mysql_engine, dialect="mysql") == []


@requires_docker
@pytest.mark.asyncio
async def test_mysql_mismatch_missing_table(mysql_engine: AsyncEngine) -> None:
    diffs = await diff_writer_contract(mysql_engine, dialect="mysql")
    assert any(d.kind == DiffKind.MISSING_TABLE for d in diffs)


@requires_docker
@pytest.mark.asyncio
async def test_mysql_mismatch_missing_column(mysql_engine: AsyncEngine) -> None:
    await apply_writer_contract(mysql_engine, dialect="mysql")
    async with mysql_engine.begin() as conn:
        await conn.execute(text("ALTER TABLE iwxxm_reports DROP COLUMN upload_key"))
    diffs = await diff_writer_contract(mysql_engine, dialect="mysql")
    assert any(d.kind == DiffKind.MISSING_COLUMN and d.column == "upload_key" for d in diffs)
