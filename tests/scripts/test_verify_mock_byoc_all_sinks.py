"""EV-080 coverage fills for scripts/deploy/verify_mock_byoc_all_sinks.py."""

from __future__ import annotations

import asyncio
import json
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tests.scripts.conftest import load_script

byoc = load_script("deploy/verify_mock_byoc_all_sinks.py")


def test_record_and_with_odbc_driver(capsys: pytest.CaptureFixture[str]) -> None:
    byoc.RESULTS.clear()
    byoc._record("sqlite", "PASS", "detail")
    assert byoc.RESULTS[-1] == ("sqlite", "PASS", "detail")
    assert "[PASS] sqlite" in capsys.readouterr().out

    uri = "mssql+pyodbc://user:pass@host/db"
    with patch.object(byoc, "preferred_sqlserver_odbc_driver", return_value=None):
        assert byoc._with_odbc_driver(uri) == uri
    with patch.object(
        byoc, "preferred_sqlserver_odbc_driver", return_value="{ODBC Driver 18}"
    ):
        out = byoc._with_odbc_driver(uri)
    assert "driver=" in out
    assert "TrustServerCertificate=yes" in out


def test_verify_db_success() -> None:
    byoc.RESULTS.clear()
    pre = SimpleNamespace(ok=True, connectivity_ok=True, diffs=[])

    class FakeResult:
        def scalar_one(self) -> int:
            return 1

    conn = AsyncMock()
    conn.execute = AsyncMock(return_value=FakeResult())
    ctx = AsyncMock()
    ctx.__aenter__.return_value = conn
    ctx.__aenter__.return_value = conn
    engine = MagicMock()
    engine.begin.return_value = ctx
    engine.dispose = AsyncMock()

    async def run() -> None:
        with (
            patch.object(byoc, "run_db_preflight", AsyncMock(return_value=pre)),
            patch.object(byoc, "create_async_engine", return_value=engine),
            patch.object(byoc, "apply_writer_contract", AsyncMock()),
            patch.object(byoc, "dialect_for_sink", return_value="sqlite"),
        ):
            await byoc._verify_db(
                "postgres_sqlite_standin", uri_override="sqlite+aiosqlite:///tmp/x.db"
            )

    asyncio.run(run())
    assert any(s == "PASS" for _, s, _ in byoc.RESULTS)


async def test_verify_sqlite_without_existing_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(byoc, "ROOT", tmp_path)
    db = tmp_path / "tmp" / "mock-byoc-all-sinks.db"
    assert not db.exists()

    async def fake_verify(_key: str, *, uri_override: str | None = None) -> None:
        byoc._record("sqlite", "PASS")

    with patch.object(byoc, "_verify_db", fake_verify):
        await byoc.verify_sqlite()


def test_verify_sqlite_creates_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(byoc, "ROOT", tmp_path)
    db = tmp_path / "tmp" / "mock-byoc-all-sinks.db"
    db.parent.mkdir(parents=True)
    db.write_text("old", encoding="utf-8")

    async def fake_verify(_key: str, *, uri_override: str | None = None) -> None:
        byoc._record("sqlite", "PASS")

    with patch.object(byoc, "_verify_db", fake_verify):
        asyncio.run(byoc.verify_sqlite())
    assert not db.exists()


def test_verify_sqlserver_skip_and_run() -> None:
    byoc.RESULTS.clear()
    with patch.object(byoc, "odbc_sqlserver_available", return_value=False):
        asyncio.run(byoc.verify_sqlserver())
    assert ("sqlserver", "SKIP", "ODBC SQL Server driver not installed") in byoc.RESULTS

    byoc.RESULTS.clear()
    with (
        patch.object(byoc, "odbc_sqlserver_available", return_value=True),
        patch.object(byoc, "_with_odbc_driver", return_value="uri"),
        patch.object(byoc, "_verify_db", AsyncMock()) as verify,
    ):
        asyncio.run(byoc.verify_sqlserver())
    verify.assert_awaited_once()


def test_verify_wis2_and_edis_and_f19() -> None:
    byoc.RESULTS.clear()
    pre = SimpleNamespace(ok=True, connectivity_ok=True)
    pub = SimpleNamespace(ok=True)
    sub = SimpleNamespace(ok=True, ahl="AHL")

    async def run_wis2() -> None:
        http = AsyncMock()
        http.get_dataset = AsyncMock(return_value=b"METAR iwxxm")
        with (
            patch.object(byoc, "wis2_preflight", AsyncMock(return_value=pre)),
            patch.object(byoc, "wis2_publish", AsyncMock(return_value=pub)),
            patch.object(byoc, "AiomqttClient", MagicMock()),
            patch.object(byoc, "HttpxDatasetClient", return_value=http),
        ):
            await byoc.verify_wis2()

    asyncio.run(run_wis2())
    assert byoc.RESULTS[-1][:2] == ("wis2", "PASS")

    byoc.RESULTS.clear()

    async def run_edis() -> None:
        with (
            patch.object(byoc, "edis_preflight", AsyncMock(return_value=pre)),
            patch.object(byoc, "edis_submit", AsyncMock(return_value=sub)),
            patch.object(byoc, "AiosmtpClient", MagicMock()),
            patch.object(
                byoc,
                "urlopen",
                side_effect=[BytesIO(b'{"total": 1}'), BytesIO(b'{"total": 2}')],
            ),
        ):
            await byoc.verify_edis()

    asyncio.run(run_edis())
    assert byoc.RESULTS[-1][0] == "edis"

    byoc.RESULTS.clear()
    adapter = SimpleNamespace(
        preflight=AsyncMock(return_value=pre),
        send=AsyncMock(return_value=SimpleNamespace(ok=True, kv_upload_key="kv1")),
    )
    resp = MagicMock()
    resp.status = 201
    resp.read.return_value = json.dumps({"ok": True, "kv_upload_key": "kv2"}).encode()
    resp.__enter__.return_value = resp

    async def run_f19() -> None:
        with (
            patch.object(byoc, "get_staging_sink", return_value=adapter),
            patch.object(byoc, "urlopen", return_value=resp),
        ):
            await byoc.verify_f19("amhs")

    asyncio.run(run_f19())
    assert byoc.RESULTS[-1][0] == "amhs"


def test_verify_postgres_and_mysql() -> None:
    with patch.object(byoc, "_verify_db", AsyncMock()) as verify:
        asyncio.run(byoc.verify_postgres())
        asyncio.run(byoc.verify_mysql())
    assert verify.await_count == 2


def _record_pass(sink: str) -> AsyncMock:
    async def _go() -> None:
        byoc._record(sink, "PASS")

    return AsyncMock(side_effect=_go)


def test_main_summary_paths(capsys: pytest.CaptureFixture[str]) -> None:
    byoc.RESULTS.clear()

    async def pass_all() -> None:
        await byoc.main()

    async def record_f19(sink: str) -> None:
        byoc._record(sink, "PASS")

    with (
        patch.object(byoc, "verify_sqlite", _record_pass("sqlite")),
        patch.object(byoc, "verify_postgres", _record_pass("postgres")),
        patch.object(byoc, "verify_mysql", _record_pass("mysql")),
        patch.object(byoc, "verify_sqlserver", _record_pass("sqlserver")),
        patch.object(byoc, "verify_wis2", _record_pass("wis2")),
        patch.object(byoc, "verify_edis", _record_pass("edis")),
        patch.object(byoc, "verify_f19", record_f19),
    ):
        asyncio.run(pass_all())
    out = capsys.readouterr().out
    assert "passed=9" in out

    byoc.RESULTS.clear()

    async def fail_main() -> None:
        with pytest.raises(SystemExit) as exc:
            await byoc.main()
        assert exc.value.code == 1

    async def record_fail() -> None:
        byoc._record("sqlite", "FAIL", "boom")

    with (
        patch.object(byoc, "verify_sqlite", AsyncMock(side_effect=record_fail)),
        patch.object(byoc, "verify_postgres", AsyncMock()),
        patch.object(byoc, "verify_mysql", AsyncMock()),
        patch.object(byoc, "verify_sqlserver", AsyncMock()),
        patch.object(byoc, "verify_wis2", AsyncMock()),
        patch.object(byoc, "verify_edis", AsyncMock()),
        patch.object(byoc, "verify_f19", AsyncMock()),
    ):
        asyncio.run(fail_main())

    byoc.RESULTS.clear()

    async def missing_sink_main() -> None:
        with pytest.raises(SystemExit, match="missing sinks"):
            await byoc.main()

    with (
        patch.object(byoc, "verify_sqlite", _record_pass("sqlite")),
        patch.object(byoc, "verify_postgres", AsyncMock()),
        patch.object(byoc, "verify_mysql", AsyncMock()),
        patch.object(byoc, "verify_sqlserver", AsyncMock()),
        patch.object(byoc, "verify_wis2", AsyncMock()),
        patch.object(byoc, "verify_edis", AsyncMock()),
        patch.object(byoc, "verify_f19", AsyncMock()),
    ):
        asyncio.run(missing_sink_main())
