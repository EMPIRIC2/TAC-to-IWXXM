"""Transport hard-fail paths for WIS2/EDIS clients (EV-stage coverage expansion).

[Corpus: tests] — mocked httpx / aiomqtt / aiosmtplib; no live egress.
"""

from __future__ import annotations

from email.message import EmailMessage
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from dissemination.transports import AiomqttClient, AiosmtpClient, HttpxDatasetClient


@pytest.mark.asyncio
async def test_httpx_ping_false_on_server_error() -> None:
    resp = MagicMock()
    resp.status_code = 503
    client = AsyncMock()
    client.head = AsyncMock(return_value=resp)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        assert await HttpxDatasetClient().ping("http://example.test/ds") is False


@pytest.mark.asyncio
async def test_httpx_ping_falls_back_on_501_then_fails_5xx() -> None:
    head = MagicMock()
    head.status_code = 501
    get = MagicMock()
    get.status_code = 502
    client = AsyncMock()
    client.head = AsyncMock(return_value=head)
    client.get = AsyncMock(return_value=get)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        assert await HttpxDatasetClient().ping("http://example.test/ds") is False
    client.get.assert_awaited()


@pytest.mark.asyncio
async def test_httpx_ping_false_on_timeout() -> None:
    client = AsyncMock()
    client.head = AsyncMock(side_effect=httpx.ReadTimeout("timed out"))
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.httpx.AsyncClient", return_value=client):
        assert await HttpxDatasetClient(timeout_s=0.1).ping("http://example.test/ds") is False


@pytest.mark.asyncio
async def test_httpx_get_dataset_raises_on_http_error() -> None:
    get_resp = MagicMock()
    get_resp.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "boom",
            request=MagicMock(),
            response=MagicMock(status_code=404),
        )
    )
    client = AsyncMock()
    client.get = AsyncMock(return_value=get_resp)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("dissemination.transports.httpx.AsyncClient", return_value=client),
        pytest.raises(httpx.HTTPStatusError),
    ):
        await HttpxDatasetClient().get_dataset("http://example.test/missing")


@pytest.mark.asyncio
async def test_aiomqtt_methods_require_connected_client() -> None:
    mqtt = AiomqttClient(host="127.0.0.1", port=1883, username="u", password="p")
    with pytest.raises(RuntimeError, match="not connected"):
        await mqtt.publish("topic", b"payload")
    with pytest.raises(RuntimeError, match="not connected"):
        await mqtt.subscribe("topic")
    with pytest.raises(RuntimeError, match="not connected"):
        await mqtt.recv(timeout_s=0.05)


@pytest.mark.asyncio
async def test_aiomqtt_recv_timeout_propagates() -> None:
    import asyncio

    inner = AsyncMock()

    async def _messages() -> Any:
        await asyncio.sleep(10)
        if False:  # pragma: no cover - keeps this an async generator
            yield None

    inner.messages = _messages()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)
    with patch("dissemination.transports.aiomqtt.Client", return_value=cm):
        mqtt = AiomqttClient(host="127.0.0.1")
        await mqtt.connect()
        with pytest.raises(TimeoutError):
            await mqtt.recv(timeout_s=0.05)
        await mqtt.disconnect()


@pytest.mark.asyncio
async def test_aiosmtp_login_and_send_require_connect() -> None:
    client = AiosmtpClient(hostname="smtp.example.test", port=587)
    with pytest.raises(RuntimeError, match="not connected"):
        await client.login("user", "secret")
    with pytest.raises(RuntimeError, match="not connected"):
        await client.send_message(EmailMessage())


@pytest.mark.asyncio
async def test_aiosmtp_quit_noop_when_never_connected() -> None:
    client = AiosmtpClient(hostname="smtp.example.test", use_tls=False)
    await client.quit()  # must not raise
