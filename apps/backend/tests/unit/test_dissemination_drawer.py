"""Success / failure / validation tests for non-DB drawer dispatch."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from dissemination.allowlist import EgressDenied, parse_allowlist
from src.services.dissemination_drawer import (
    assert_known_sink,
    edis_params_from_request,
    f19_params_from_request,
    is_db_sink,
    is_non_db_sink,
    run_non_db_preflight,
    run_non_db_send,
    wis2_params_from_request,
)


@pytest.fixture(autouse=True)
def _dns_to_loopback():
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("127.0.0.1", 0))],
    ):
        yield


def test_sink_classification_success() -> None:
    assert is_db_sink("sqlite") is True
    assert is_non_db_sink("wis2") is True
    assert assert_known_sink("edis") == "edis"


def test_assert_known_sink_validation_missing() -> None:
    with pytest.raises(ValueError, match="missing"):
        assert_known_sink(None)


def test_assert_known_sink_failure_unknown() -> None:
    with pytest.raises(ValueError, match="unknown"):
        assert_known_sink("ftp")


def test_wis2_params_validation_missing_fields() -> None:
    with pytest.raises(ValueError, match="mqtt_host"):
        wis2_params_from_request({"mqtt_topic": "t", "dataset_url": "http://x"})


def test_wis2_params_success_aliases() -> None:
    params = wis2_params_from_request({"broker": "wis2box", "topic": "origin/a", "dataset": "http://127.0.0.1/ds"})
    assert params.mqtt_host == "wis2box"
    assert params.mqtt_topic == "origin/a"
    assert params.dataset_url == "http://127.0.0.1/ds"


def test_edis_params_validation_missing() -> None:
    with pytest.raises(ValueError, match="missing required"):
        edis_params_from_request({"smtp_host": "h"})


def test_f19_params_success() -> None:
    params = f19_params_from_request("amhs", {"host": "amhs.example", "port": 102})
    assert params.host == "amhs.example"
    assert params.port == 102


@pytest.mark.asyncio
async def test_wis2_preflight_success_mocked() -> None:
    mqtt = AsyncMock()
    mqtt.connect = AsyncMock()
    mqtt.disconnect = AsyncMock()
    http = AsyncMock()
    http.ping = AsyncMock(return_value=True)
    allow = parse_allowlist("wis2box,127.0.0.1,localhost")
    result = await run_non_db_preflight(
        "wis2",
        {
            "mqtt_host": "wis2box",
            "mqtt_topic": "origin/a/wis2",
            "dataset_url": "http://127.0.0.1/datasets/x.xml",
            "use_tls": False,
        },
        allowlist=allow,
        mqtt=mqtt,
        http=http,
    )
    assert result.ok is True
    assert result.connectivity_ok is True


@pytest.mark.asyncio
async def test_wis2_preflight_failure_egress() -> None:
    allow = parse_allowlist("")  # fail-closed
    with pytest.raises(EgressDenied):
        await run_non_db_preflight(
            "wis2",
            {
                "mqtt_host": "evil.example",
                "mqtt_topic": "t",
                "dataset_url": "http://evil.example/ds",
            },
            allowlist=allow,
            mqtt=AsyncMock(),
            http=AsyncMock(),
        )


@pytest.mark.asyncio
async def test_wis2_send_success_mocked() -> None:
    mqtt = AsyncMock()
    mqtt.connect = AsyncMock()
    mqtt.publish = AsyncMock()
    mqtt.disconnect = AsyncMock()
    http = AsyncMock()
    http.put_dataset = AsyncMock(return_value=201)
    allow = parse_allowlist("wis2box,127.0.0.1,localhost")
    sent = await run_non_db_send(
        "wis2",
        {
            "mqtt_host": "wis2box",
            "mqtt_topic": "origin/a/wis2",
            "dataset_url": "http://127.0.0.1/datasets/x.xml",
            "use_tls": False,
        },
        iwxxm_xml="<METAR/>",
        allowlist=allow,
        mqtt=mqtt,
        http=http,
    )
    assert sent.ok is True
    assert "wis2" in (sent.detail or "").lower()


@pytest.mark.asyncio
async def test_f19_preflight_success() -> None:
    allow = parse_allowlist("amhs.example,127.0.0.0/8")
    result = await run_non_db_preflight(
        "amhs",
        {"host": "amhs.example"},
        allowlist=allow,
    )
    assert result.ok is True
