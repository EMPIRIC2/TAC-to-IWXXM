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
    params = f19_params_from_request("amhs", {"host": "amhs.example", "port": "102"})
    assert params.host == "amhs.example"
    assert params.port == 102


def test_f19_params_validation_bad_sink() -> None:
    with pytest.raises(ValueError, match="not an F19"):
        f19_params_from_request("wis2", {"host": "x"})


def test_f19_params_validation_missing_host() -> None:
    with pytest.raises(ValueError, match="require host"):
        f19_params_from_request("swim", {"port": 1})


def test_edis_params_success() -> None:
    params = edis_params_from_request(
        {
            "smtp_host": "smtp.example",
            "mail_from": "a@b.c",
            "mail_to": "d@e.f",
            "tt": "SA",
            "aa": "XX",
            "ii": "01",
            "cccc": "KABC",
            "yygggg": "121200",
            "use_tls": "yes",
            "smtp_port": "bad",
        }
    )
    assert params.smtp_host == "smtp.example"
    assert params.use_tls is True
    assert params.smtp_port == 587


def test_wis2_params_bool_and_int_branches() -> None:
    params = wis2_params_from_request(
        {
            "mqtt_host": "wis2box",
            "mqtt_topic": "t",
            "dataset_url": "http://127.0.0.1/ds",
            "mqtt_port": "not-int",
            "use_tls": "off",
            "mqtt_username": "u",
            "mqtt_password": "p",
        }
    )
    assert params.mqtt_port == 8883
    assert params.use_tls is False
    params2 = wis2_params_from_request(
        {
            "mqtt_host": "wis2box",
            "mqtt_topic": "t",
            "dataset_url": "http://127.0.0.1/ds",
            "use_tls": True,
            "mqtt_port": 1883,
        }
    )
    assert params2.use_tls is True
    assert params2.mqtt_port == 1883


def test_wis2_params_empty_alias_falls_through_to_next_key() -> None:
    """Blank primary keys must not win over a later alias."""
    params = wis2_params_from_request(
        {
            "mqtt_host": "   ",
            "broker": "wis2box",
            "mqtt_topic": "",
            "topic": "origin/a",
            "dataset_url": "\t",
            "dataset": "http://127.0.0.1/ds",
            "use_tls": "maybe",
        }
    )
    assert params.mqtt_host == "wis2box"
    assert params.mqtt_topic == "origin/a"
    assert params.dataset_url == "http://127.0.0.1/ds"
    assert params.use_tls is True


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


@pytest.mark.asyncio
async def test_edis_preflight_and_send_success_mocked() -> None:
    from dissemination.edis import EdisSubmitResult
    from dissemination.models import PreflightResponse

    smtp = AsyncMock()
    allow = parse_allowlist("smtp.example,127.0.0.0/8")
    edis_body = {
        "smtp_host": "smtp.example",
        "mail_from": "a@b.c",
        "mail_to": "d@e.f",
        "tt": "SA",
        "aa": "XX",
        "ii": "01",
        "cccc": "KABC",
        "yygggg": "121200",
    }
    with patch(
        "src.services.dissemination_drawer.edis_preflight",
        new=AsyncMock(
            return_value=PreflightResponse(
                ok=True, connectivity_ok=True, diffs=[], detail="edis ok"
            )
        ),
    ) as preflight:
        result = await run_non_db_preflight("edis", edis_body, allowlist=allow, smtp=smtp)
    assert result.ok is True
    preflight.assert_awaited_once()

    with patch(
        "src.services.dissemination_drawer.edis_submit",
        new=AsyncMock(
            return_value=EdisSubmitResult(ok=True, ahl="SAXX01 KABC 121200", detail="edis submitted")
        ),
    ) as submit:
        sent = await run_non_db_send(
            "edis",
            edis_body,
            iwxxm_xml="<METAR/>",
            tac_text="METAR KABC 121200Z ...",
            allowlist=allow,
            smtp=smtp,
        )
    assert sent.ok is True
    assert "edis" in (sent.detail or "").lower()
    submit.assert_awaited_once()


@pytest.mark.asyncio
async def test_f19_send_success() -> None:
    allow = parse_allowlist("amhs.example,127.0.0.0/8")
    sent = await run_non_db_send(
        "amhs",
        {"host": "amhs.example"},
        iwxxm_xml="<METAR/>",
        allowlist=allow,
    )
    assert sent.ok is True


@pytest.mark.asyncio
async def test_unsupported_non_db_sink_raises() -> None:
    with pytest.raises(ValueError, match="unsupported non-DB sink"):
        await run_non_db_preflight("ftp", {})
    with pytest.raises(ValueError, match="unsupported non-DB sink"):
        await run_non_db_send("ftp", {}, iwxxm_xml="<x/>")


@pytest.mark.asyncio
async def test_default_transport_clients_constructed() -> None:
    """Cover Aiomqtt/Aiosmtp/Httpx construction when callers omit clients."""
    from dissemination.edis import EdisSubmitResult
    from dissemination.models import PreflightResponse
    from dissemination.wis2 import Wis2PublishResult

    allow = parse_allowlist("wis2box,smtp.example,127.0.0.0/8")
    mqtt = AsyncMock()
    http = AsyncMock()
    smtp = AsyncMock()
    preflight_ok = PreflightResponse(ok=True, connectivity_ok=True, diffs=[], detail="ok")
    wis2_params = {
        "mqtt_host": "wis2box",
        "mqtt_topic": "origin/a/wis2",
        "dataset_url": "http://127.0.0.1/ds",
    }
    edis_params = {
        "smtp_host": "smtp.example",
        "mail_from": "a@b.c",
        "mail_to": "d@e.f",
        "tt": "SA",
        "aa": "XX",
        "ii": "01",
        "cccc": "KABC",
        "yygggg": "121200",
    }

    with (
        patch("src.services.dissemination_drawer.AiomqttClient", return_value=mqtt) as mqtt_ctor,
        patch("src.services.dissemination_drawer.HttpxDatasetClient", return_value=http) as http_ctor,
        patch(
            "src.services.dissemination_drawer.wis2_preflight",
            new=AsyncMock(return_value=preflight_ok),
        ),
    ):
        result = await run_non_db_preflight("wis2", wis2_params, allowlist=allow)
    assert result.ok is True
    mqtt_ctor.assert_called_once()
    http_ctor.assert_called_once()

    with (
        patch("src.services.dissemination_drawer.AiosmtpClient", return_value=smtp) as smtp_ctor,
        patch(
            "src.services.dissemination_drawer.edis_preflight",
            new=AsyncMock(return_value=preflight_ok),
        ),
    ):
        edis = await run_non_db_preflight("edis", edis_params, allowlist=allow)
    assert edis.ok is True
    smtp_ctor.assert_called_once()

    with (
        patch("src.services.dissemination_drawer.AiomqttClient", return_value=mqtt),
        patch("src.services.dissemination_drawer.HttpxDatasetClient", return_value=http),
        patch("src.services.dissemination_drawer.AiosmtpClient", return_value=smtp),
        patch(
            "src.services.dissemination_drawer.wis2_publish",
            new=AsyncMock(
                return_value=Wis2PublishResult(
                    ok=True,
                    dataset_url="http://127.0.0.1/ds",
                    mqtt_topic="origin/a/wis2",
                    detail="wis2 published",
                )
            ),
        ),
        patch(
            "src.services.dissemination_drawer.edis_submit",
            new=AsyncMock(
                return_value=EdisSubmitResult(ok=True, ahl="SAXX01 KABC 121200", detail=None)
            ),
        ),
    ):
        wis2_sent = await run_non_db_send(
            "wis2", wis2_params, iwxxm_xml="<METAR/>", allowlist=allow
        )
        edis_sent = await run_non_db_send(
            "edis", edis_params, iwxxm_xml="<METAR/>", allowlist=allow
        )
    assert wis2_sent.ok is True
    assert edis_sent.ok is True
    assert edis_sent.detail == "edis submitted"
