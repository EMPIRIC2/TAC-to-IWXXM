"""Unit tests for WIS2 httpx/aiomqtt transports (T3.4 coverage)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from dissemination.transports import AiomqttClient, HttpxDatasetClient


@pytest.mark.asyncio
async def test_httpx_ping_true_on_200() -> None:
    resp = MagicMock()
    resp.status_code = 200
    client = AsyncMock()
    client.head = AsyncMock(return_value=resp)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        assert await HttpxDatasetClient().ping("http://example.test/ds") is True


@pytest.mark.asyncio
async def test_httpx_ping_falls_back_to_get_on_405() -> None:
    head = MagicMock()
    head.status_code = 405
    get = MagicMock()
    get.status_code = 404
    client = AsyncMock()
    client.head = AsyncMock(return_value=head)
    client.get = AsyncMock(return_value=get)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        assert await HttpxDatasetClient().ping("http://example.test/ds") is True
    client.get.assert_awaited()


@pytest.mark.asyncio
async def test_httpx_ping_false_on_http_error() -> None:
    client = AsyncMock()
    client.head = AsyncMock(side_effect=httpx.ConnectError("boom"))
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        assert await HttpxDatasetClient().ping("http://example.test/ds") is False


@pytest.mark.asyncio
async def test_httpx_put_and_get() -> None:
    put_resp = MagicMock()
    put_resp.status_code = 201
    get_resp = MagicMock()
    get_resp.content = b"<xml/>"
    get_resp.raise_for_status = MagicMock()
    client = AsyncMock()
    client.put = AsyncMock(return_value=put_resp)
    client.get = AsyncMock(return_value=get_resp)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        http = HttpxDatasetClient()
        assert await http.put_dataset("http://example.test/ds", b"<xml/>", "application/xml") == 201
        assert await http.get_dataset("http://example.test/ds") == b"<xml/>"


@pytest.mark.asyncio
async def test_aiomqtt_subscribe_and_recv_require_connect() -> None:
    mqtt = AiomqttClient(host="127.0.0.1", port=1883)
    with pytest.raises(RuntimeError, match="not connected"):
        await mqtt.subscribe("t")
    with pytest.raises(RuntimeError, match="not connected"):
        await mqtt.recv(timeout_s=0.1)


@pytest.mark.asyncio
async def test_aiomqtt_recv_bytearray_and_str_payloads() -> None:
    inner = AsyncMock()

    class _BA:
        payload = bytearray(b"ba")

    class _Str:
        payload = "str-payload"

    async def _messages() -> Any:
        yield _BA()
        yield _Str()

    inner.messages = _messages()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.aiomqtt.Client", return_value=cm):
        mqtt = AiomqttClient(host="127.0.0.1")
        await mqtt.connect()
        assert await mqtt.recv(timeout_s=1.0) == b"ba"
        assert await mqtt.recv(timeout_s=1.0) == b"str-payload"
        await mqtt.disconnect()


@pytest.mark.asyncio
async def test_aiomqtt_recv_memoryview_like_payload() -> None:
    inner = AsyncMock()

    class _Mem:
        payload = memoryview(b"mv")

    async def _messages() -> Any:
        yield _Mem()

    inner.messages = _messages()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.aiomqtt.Client", return_value=cm):
        mqtt = AiomqttClient(host="127.0.0.1")
        await mqtt.connect()
        assert await mqtt.recv(timeout_s=1.0) == b"mv"
        await mqtt.disconnect()


@pytest.mark.asyncio
async def test_aiomqtt_disconnect_noop_when_never_connected() -> None:
    mqtt = AiomqttClient(host="127.0.0.1")
    await mqtt.disconnect()


@pytest.mark.asyncio
async def test_aiomqtt_connect_publish_disconnect() -> None:
    inner = AsyncMock()
    inner.publish = AsyncMock()
    inner.subscribe = AsyncMock()

    class _Msg:
        payload = b'{"ok":true}'

    async def _messages() -> Any:
        yield _Msg()

    inner.messages = _messages()

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)

    with patch("dissemination.transports.aiomqtt.Client", return_value=cm) as ctor:
        mqtt = AiomqttClient(host="127.0.0.1", port=1883, username="u", password="p")
        await mqtt.connect()
        await mqtt.connect()  # idempotent
        ctor.assert_called_once()
        await mqtt.publish("topic", b"payload")
        inner.publish.assert_awaited_once_with("topic", payload=b"payload")
        await mqtt.subscribe("topic")
        got = await mqtt.recv(timeout_s=1.0)
        assert got == b'{"ok":true}'
        await mqtt.disconnect()
        cm.__aexit__.assert_awaited()


@pytest.mark.asyncio
async def test_aiomqtt_context_manager() -> None:
    inner = AsyncMock()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.aiomqtt.Client", return_value=cm):
        async with AiomqttClient(host="127.0.0.1") as mqtt:
            assert mqtt is not None
        cm.__aexit__.assert_awaited()
