"""T6.6 mock BYOC close-gate evidence (S019 / EV-014).

Operator waived live destination credentials (D-S019-EV014-Q15-mock-waive).
Exercises Postgres stand-in (SQLite), WIS2 (mocked transports), and EDIS
(mocked SMTP) with fixture-shaped params - no live egress.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from dissemination.allowlist import parse_allowlist
from dissemination.db_preflight import run_db_preflight
from dissemination.edis import EdisParams, edis_preflight, edis_submit
from dissemination.models import PreflightRequest
from dissemination.wis2 import Wis2Params, wis2_preflight, wis2_publish
from dissemination.writer_contract import apply_writer_contract, diff_writer_contract
from sqlalchemy.ext.asyncio import create_async_engine

_FIXTURES = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "sessions"
    / "S019-dissemination-upload"
    / "fixtures"
    / "mock-byoc-destinations.json"
)


@pytest.fixture(scope="module")
def mock_byoc() -> dict[str, Any]:
    return json.loads(_FIXTURES.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _dns_to_loopback():
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("127.0.0.1", 0))],
    ):
        yield


@pytest.mark.asyncio
async def test_mock_postgres_standin_sqlite_preflight_and_apply(
    mock_byoc: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SQLite stand-in for Postgres writer-contract when Testcontainers unavailable."""
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    db = tmp_path / "s019-mock-byoc.db"
    uri = f"sqlite+aiosqlite:///{db}"
    assert mock_byoc["postgres_sqlite_standin"]["sink_type"] == "sqlite"

    resp = await run_db_preflight(PreflightRequest(sink_type="sqlite", uri=uri, ddl=True))
    assert resp.ok is True
    assert resp.connectivity_ok is True
    assert resp.diffs == []

    engine = create_async_engine(uri)
    try:
        await apply_writer_contract(engine, dialect="sqlite")
        diffs = await diff_writer_contract(engine, dialect="sqlite")
        assert diffs == []
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_mock_wis2_preflight_and_publish(mock_byoc: dict[str, Any]) -> None:
    """WIS2 using fixture params + injected mock MQTT/HTTP (no Compose required)."""
    raw = mock_byoc["wis2_mock"]["params"]
    params = Wis2Params(
        mqtt_host=raw["mqtt_host"],
        mqtt_port=int(raw["mqtt_port"]),
        mqtt_topic=raw["mqtt_topic"],
        dataset_url=raw["dataset_url"],
        centre_id=raw["centre_id"],
        mqtt_username=raw["mqtt_username"],
        mqtt_password=raw["mqtt_password"],
        use_tls=bool(raw["use_tls"]),
    )
    allow = parse_allowlist("wis2box,127.0.0.1,127.0.0.0/8,localhost")
    mqtt = AsyncMock()
    mqtt.connect = AsyncMock()
    mqtt.publish = AsyncMock()
    mqtt.disconnect = AsyncMock()
    http = AsyncMock()
    http.ping = AsyncMock(return_value=True)
    http.put_dataset = AsyncMock(return_value=201)

    pre = await wis2_preflight(params, allowlist=allow, mqtt=mqtt, http=http)
    assert pre.ok is True
    assert pre.connectivity_ok is True

    pub = await wis2_publish(
        params,
        iwxxm_xml="<MeteorologicalAerodromeObservationReport/>",
        allowlist=allow,
        mqtt=mqtt,
        http=http,
    )
    assert pub.ok is True
    assert "mock-wis2-token-not-real" not in repr(pre)
    mqtt.connect.assert_awaited()
    http.put_dataset.assert_awaited()


@pytest.mark.asyncio
async def test_mock_edis_preflight_and_submit(mock_byoc: dict[str, Any]) -> None:
    """EDIS using fixture params + mocked SMTP client (no live RTH)."""
    raw = mock_byoc["edis_mock"]["params"]
    params = EdisParams(
        smtp_host=raw["smtp_host"],
        smtp_port=int(raw["smtp_port"]),
        mail_from=raw["mail_from"],
        mail_to=raw["mail_to"],
        username=raw["username"],
        password=raw["password"],
        use_tls=bool(raw["use_tls"]),
        tt=raw["tt"],
        aa=raw["aa"],
        ii=raw["ii"],
        cccc=raw["cccc"],
        yygggg=raw["yygggg"],
    )
    allow = parse_allowlist("127.0.0.1,127.0.0.0/8,localhost")
    smtp = AsyncMock()
    smtp.connect = AsyncMock()
    smtp.login = AsyncMock()
    smtp.send_message = AsyncMock()
    smtp.quit = AsyncMock()

    pre = await edis_preflight(params, allowlist=allow, smtp=smtp)
    assert pre.ok is True
    assert pre.connectivity_ok is True

    sent = await edis_submit(
        params,
        tac_body="METAR KXXX 211200Z 00000KT 10SM SKC 20/10 A2992=",
        allowlist=allow,
        smtp=smtp,
    )
    assert sent.ok is True
    assert "mock-smtp-password-not-real" not in repr(pre)
    smtp.connect.assert_awaited()
    smtp.send_message.assert_awaited()
