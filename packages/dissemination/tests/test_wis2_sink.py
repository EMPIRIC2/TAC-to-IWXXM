"""WIS2 sink adapter unit tests with mocked MQTT/HTTP (T3.1 / TC-F17-001 / E14-09).

Exercises preflight + publish orchestration without a live broker or wis2box.
Real Compose harness coverage lands in T3.3-T3.4.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from dissemination.allowlist import EgressDenied, parse_allowlist
from dissemination.wis2 import (
    Wis2Params,
    Wis2PublishResult,
    build_wis2_notification,
    wis2_preflight,
    wis2_publish,
)


@pytest.fixture(autouse=True)
def _public_dns_for_example_hosts():
    """Allowlist checks resolve hosts; map test FQDNs to a public address."""
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield


def _params(**overrides: Any) -> Wis2Params:
    base = dict(
        mqtt_host="broker.example.test",
        mqtt_port=8883,
        mqtt_topic="origin/a/wis2/test-centre/data/core/weather/aviation/metar",
        dataset_url="https://data.example.test/wis2/metar/sample.xml",
        centre_id="test-centre",
        mqtt_username="publisher",
        mqtt_password="secret-token",
        use_tls=True,
    )
    base.update(overrides)
    return Wis2Params(**base)


def _allowlist(*hosts: str):
    return parse_allowlist(",".join(hosts))


@pytest.fixture
def mqtt() -> AsyncMock:
    client = AsyncMock()
    client.connect = AsyncMock()
    client.publish = AsyncMock()
    client.disconnect = AsyncMock()
    return client


@pytest.fixture
def http() -> AsyncMock:
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.put_dataset = AsyncMock(return_value=201)
    client.get_dataset = AsyncMock(return_value=b"<iwxxm/>")
    return client


@pytest.mark.asyncio
async def test_wis2_preflight_ok_with_mocks(mqtt: AsyncMock, http: AsyncMock) -> None:
    params = _params()
    result = await wis2_preflight(
        params,
        allowlist=_allowlist("broker.example.test", "data.example.test"),
        mqtt=mqtt,
        http=http,
    )
    assert result.ok is True
    assert result.connectivity_ok is True
    assert result.diffs == []
    mqtt.connect.assert_awaited_once()
    mqtt.disconnect.assert_awaited_once()
    http.ping.assert_awaited_once_with(params.dataset_url)


@pytest.mark.asyncio
async def test_wis2_preflight_denies_mqtt_host_not_allowlisted(mqtt: AsyncMock, http: AsyncMock) -> None:
    with pytest.raises(EgressDenied):
        await wis2_preflight(
            _params(),
            allowlist=_allowlist("data.example.test"),
            mqtt=mqtt,
            http=http,
        )
    mqtt.connect.assert_not_awaited()


@pytest.mark.asyncio
async def test_wis2_preflight_denies_dataset_host_not_allowlisted(mqtt: AsyncMock, http: AsyncMock) -> None:
    with pytest.raises(EgressDenied):
        await wis2_preflight(
            _params(),
            allowlist=_allowlist("broker.example.test"),
            mqtt=mqtt,
            http=http,
        )


@pytest.mark.asyncio
async def test_wis2_publish_puts_dataset_then_mqtt_notify(mqtt: AsyncMock, http: AsyncMock) -> None:
    params = _params()
    xml = b'<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://example"/>'
    result = await wis2_publish(
        params,
        iwxxm_xml=xml,
        allowlist=_allowlist("broker.example.test", "data.example.test"),
        mqtt=mqtt,
        http=http,
    )
    assert isinstance(result, Wis2PublishResult)
    assert result.ok is True
    assert result.dataset_url == params.dataset_url
    assert result.mqtt_topic == params.mqtt_topic
    http.put_dataset.assert_awaited_once_with(
        params.dataset_url,
        xml,
        "application/xml",
    )
    mqtt.connect.assert_awaited_once()
    mqtt.publish.assert_awaited_once()
    topic, payload = mqtt.publish.await_args.args
    assert topic == params.mqtt_topic
    message = json.loads(payload.decode("utf-8"))
    assert message["type"] == "Feature"
    assert any(
        link.get("rel") == "canonical" and link.get("href") == params.dataset_url for link in message.get("links", [])
    )
    # Secrets must not appear in the notification payload
    dumped = json.dumps(message)
    assert "secret-token" not in dumped
    mqtt.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_wis2_publish_redacts_secret_in_transport_errors(mqtt: AsyncMock, http: AsyncMock) -> None:
    http.put_dataset = AsyncMock(side_effect=RuntimeError("auth failed secret-token"))
    with pytest.raises(ValueError, match="REDACTED") as excinfo:
        await wis2_publish(
            _params(),
            iwxxm_xml=b"<x/>",
            allowlist=_allowlist("broker.example.test", "data.example.test"),
            mqtt=mqtt,
            http=http,
        )
    assert "secret-token" not in str(excinfo.value)


@pytest.mark.asyncio
async def test_wis2_publish_redacts_without_mqtt_credentials(mqtt: AsyncMock, http: AsyncMock) -> None:
    """``_redact_exc`` false branches when username/password are unset (EV-080 M2a)."""
    http.put_dataset = AsyncMock(side_effect=RuntimeError("transport boom"))
    with pytest.raises(ValueError, match="transport boom"):
        await wis2_publish(
            _params(mqtt_username=None, mqtt_password=None),
            iwxxm_xml=b"<x/>",
            allowlist=_allowlist("broker.example.test", "data.example.test"),
            mqtt=mqtt,
            http=http,
        )


@pytest.mark.asyncio
async def test_wis2_publish_reraises_egress_denied(mqtt: AsyncMock, http: AsyncMock) -> None:
    http.put_dataset = AsyncMock(side_effect=EgressDenied("blocked mid-publish"))
    with pytest.raises(EgressDenied, match="blocked mid-publish"):
        await wis2_publish(
            _params(),
            iwxxm_xml=b"<x/>",
            allowlist=_allowlist("broker.example.test", "data.example.test"),
            mqtt=mqtt,
            http=http,
        )


def test_build_wis2_notification_canonical_link() -> None:
    params = _params()
    note = build_wis2_notification(params, content_type="application/xml")
    assert note["properties"]["data_id"].startswith("wis2/")
    hrefs = [link["href"] for link in note["links"] if link.get("rel") == "canonical"]
    assert hrefs == [params.dataset_url]


def test_build_wis2_notification_unknown_centre_when_missing() -> None:
    params = _params(centre_id=None)
    note = build_wis2_notification(params)
    assert note["properties"]["data_id"].startswith("wis2/unknown/")


def test_dataset_url_requires_hostname() -> None:
    from dissemination.wis2 import _dataset_hostname

    with pytest.raises(ValueError, match="hostname"):
        _dataset_hostname("not-a-url")


@pytest.mark.asyncio
async def test_wis2_preflight_dataset_ping_false(mqtt: AsyncMock, http: AsyncMock) -> None:
    http.ping = AsyncMock(return_value=False)
    result = await wis2_preflight(
        _params(),
        allowlist=_allowlist("broker.example.test", "data.example.test"),
        mqtt=mqtt,
        http=http,
    )
    assert result.ok is False
    assert result.connectivity_ok is False
    assert result.detail == "dataset HTTP ping failed"


@pytest.mark.asyncio
async def test_wis2_preflight_transport_error_redacted(mqtt: AsyncMock, http: AsyncMock) -> None:
    mqtt.connect = AsyncMock(side_effect=RuntimeError("password=secret-token boom"))
    with pytest.raises(ValueError, match=r".*") as excinfo:
        await wis2_preflight(
            _params(),
            allowlist=_allowlist("broker.example.test", "data.example.test"),
            mqtt=mqtt,
            http=http,
        )
    assert "secret-token" not in str(excinfo.value)


@pytest.mark.asyncio
async def test_wis2_publish_http_status_error(mqtt: AsyncMock, http: AsyncMock) -> None:
    http.put_dataset = AsyncMock(return_value=503)
    with pytest.raises(ValueError, match="dataset PUT failed"):
        await wis2_publish(
            _params(),
            iwxxm_xml="<x/>",
            allowlist=_allowlist("broker.example.test", "data.example.test"),
            mqtt=mqtt,
            http=http,
        )
    mqtt.connect.assert_not_awaited()


@pytest.mark.asyncio
async def test_wis2_publish_accepts_str_xml(mqtt: AsyncMock, http: AsyncMock) -> None:
    result = await wis2_publish(
        _params(),
        iwxxm_xml="<iwxxm/>",
        allowlist=_allowlist("broker.example.test", "data.example.test"),
        mqtt=mqtt,
        http=http,
    )
    assert result.ok is True
    body = http.put_dataset.await_args.args[1]
    assert body == b"<iwxxm/>"
