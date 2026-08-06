"""Unit tests for live write-assert helpers (EV-039 / T2.3 / AC2).

[Corpus: product §F16] [Corpus: tests] TC-F16-LIVE [Corpus: adr/ADR-030]
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from dissemination.live_write_assert import assert_live_write, count_iwxxm_rows, main
from dissemination.writer_contract import CONTRACT_TABLE, apply_writer_contract


@pytest.mark.asyncio
async def test_assert_live_write_sqlite_tmp(tmp_path: Path) -> None:
    db = tmp_path / "live-assert.db"
    uri = f"sqlite+aiosqlite:///{db}"
    engine = create_async_engine(uri)
    upload_key = f"kv_{uuid.uuid4().hex}"
    try:
        await apply_writer_contract(engine, dialect="sqlite")
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"INSERT INTO {CONTRACT_TABLE} "
                    "(id, product, icao, observation_time, iwxxm_version, iwxxm_xml, "
                    "tac_text, upload_key) "
                    "VALUES (:id, :product, NULL, NULL, :ver, :xml, :tac, :upload_key)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "product": "metar",
                    "ver": "2025-2",
                    "xml": "<iwxxm:METAR/>",
                    "tac": "METAR KJFK=",
                    "upload_key": upload_key,
                },
            )
        count = await count_iwxxm_rows(engine, upload_key=upload_key)
        assert count == 1
    finally:
        await engine.dispose()

    got = await assert_live_write(
        sink_type="sqlite",
        uri=uri,
        upload_key=upload_key,
        min_rows=1,
    )
    assert got == 1


@pytest.mark.asyncio
async def test_assert_live_write_fails_when_empty(tmp_path: Path) -> None:
    db = tmp_path / "empty.db"
    uri = f"sqlite+aiosqlite:///{db}"
    engine = create_async_engine(uri)
    try:
        await apply_writer_contract(engine, dialect="sqlite")
    finally:
        await engine.dispose()

    with pytest.raises(AssertionError, match="expected ≥1"):
        await assert_live_write(sink_type="sqlite", uri=uri, min_rows=1)


def test_cli_main_ok_and_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    db = tmp_path / "cli.db"
    uri = f"sqlite+aiosqlite:///{db}"

    async def _seed() -> None:
        engine = create_async_engine(uri)
        try:
            await apply_writer_contract(engine, dialect="sqlite")
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        f"INSERT INTO {CONTRACT_TABLE} "
                        "(id, product, icao, observation_time, iwxxm_version, iwxxm_xml, "
                        "tac_text, upload_key) "
                        "VALUES (:id, 'metar', NULL, NULL, '2025-2', '<x/>', NULL, 'kv_cli')"
                    ),
                    {"id": str(uuid.uuid4())},
                )
        finally:
            await engine.dispose()

    import asyncio

    asyncio.run(_seed())

    assert main(["--sink-type", "sqlite", "--uri", uri, "--upload-key", "kv_cli"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True
    assert out["count"] == 1

    empty = tmp_path / "cli-empty.db"
    empty_uri = f"sqlite+aiosqlite:///{empty}"

    async def _empty() -> None:
        engine = create_async_engine(empty_uri)
        try:
            await apply_writer_contract(engine, dialect="sqlite")
        finally:
            await engine.dispose()

    asyncio.run(_empty())
    assert main(["--sink-type", "sqlite", "--uri", empty_uri]) == 1
    err = json.loads(capsys.readouterr().err)
    assert err["ok"] is False
