"""Concrete transports for WIS2 + EDIS sinks (F17 / F18).

Implements the Protocols in ``dissemination.wis2`` / ``dissemination.edis`` using
``httpx``, ``aiomqtt``, and ``aiosmtplib``.
"""

from __future__ import annotations

import asyncio
from email.message import EmailMessage
from typing import Self

import aiomqtt
import aiosmtplib
import httpx


class HttpxDatasetClient:
    """``HttpDatasetClient`` backed by httpx (async)."""

    def __init__(self, *, timeout_s: float = 30.0) -> None:
        self._timeout = timeout_s

    async def ping(self, url: str) -> bool:
        """
        Return True when the dataset URL is reachable (2xx/3xx/404/405 accepted).

        A missing object (404) still proves HTTP reachability for preflight.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                resp = await client.head(url)
                if resp.status_code in {404, 405, 501}:
                    resp = await client.get(url)
                return resp.status_code < 500
        except httpx.HTTPError:
            return False

    async def put_dataset(self, url: str, body: bytes, content_type: str) -> int:
        """PUT dataset bytes; return HTTP status code."""
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            resp = await client.put(url, content=body, headers={"Content-Type": content_type})
            return resp.status_code

    async def get_dataset(self, url: str) -> bytes:
        """GET dataset bytes; raise on non-2xx."""
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content


class AiomqttClient:
    """``MqttClient`` (+ subscribe helper) backed by aiomqtt 2.x."""

    def __init__(
        self,
        *,
        host: str,
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client: aiomqtt.Client | None = None
        self._cm: object | None = None

    async def connect(self) -> None:
        """Open an MQTT connection to the configured broker."""
        if self._client is not None:
            return
        kwargs: dict[str, object] = {
            "hostname": self._host,
            "port": self._port,
        }
        if self._username is not None:
            kwargs["username"] = self._username
        if self._password is not None:
            kwargs["password"] = self._password
        client = aiomqtt.Client(**kwargs)  # type: ignore[arg-type]
        self._cm = client
        self._client = await client.__aenter__()

    async def publish(self, topic: str, payload: bytes) -> None:
        """Publish ``payload`` to ``topic`` (QoS 0)."""
        if self._client is None:
            raise RuntimeError("mqtt client is not connected")
        await self._client.publish(topic, payload=payload)

    async def subscribe(self, topic: str) -> None:
        """Subscribe to ``topic`` (for harness verification)."""
        if self._client is None:
            raise RuntimeError("mqtt client is not connected")
        await self._client.subscribe(topic)

    async def recv(self, *, timeout_s: float = 15.0) -> bytes:
        """
        Wait for the next subscribed message payload.

        Parameters
        ----------
        timeout_s :
            Seconds to wait before raising ``TimeoutError``.
        """
        if self._client is None:
            raise RuntimeError("mqtt client is not connected")

        async def _next() -> bytes:
            assert self._client is not None
            async for message in self._client.messages:
                payload = message.payload
                if isinstance(payload, bytes):
                    return payload
                if isinstance(payload, bytearray):
                    return bytes(payload)
                if isinstance(payload, str):
                    return payload.encode("utf-8")
                return bytes(payload)

        return await asyncio.wait_for(_next(), timeout=timeout_s)

    async def disconnect(self) -> None:
        """Close the MQTT connection if open."""
        if self._cm is None:
            self._client = None
            return
        cm = self._cm
        self._client = None
        self._cm = None
        await cm.__aexit__(None, None, None)  # type: ignore[union-attr]

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.disconnect()


class AiosmtpClient:
    """``SmtpClient`` backed by ``aiosmtplib`` (EDIS / F18).

    Prefers STARTTLS on submission ports (e.g. 587); uses implicit TLS on 465.
    """

    def __init__(
        self,
        *,
        hostname: str,
        port: int = 587,
        use_tls: bool = True,
        timeout: float = 30.0,
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._use_tls = use_tls
        self._timeout = timeout
        self._client: aiosmtplib.SMTP | None = None

    def _tls_kwargs(self) -> dict[str, bool]:
        if not self._use_tls:
            return {"use_tls": False, "start_tls": False}
        if self._port == 465:
            return {"use_tls": True, "start_tls": False}
        return {"use_tls": False, "start_tls": True}

    async def connect(self) -> None:
        """Open an SMTP connection (STARTTLS or implicit TLS per port)."""
        if self._client is not None and self._client.is_connected:
            return
        client = aiosmtplib.SMTP(
            hostname=self._hostname,
            port=self._port,
            timeout=self._timeout,
            **self._tls_kwargs(),
        )
        await client.connect()
        self._client = client

    async def login(self, username: str, password: str) -> None:
        """Authenticate with the SMTP server."""
        if self._client is None:
            raise RuntimeError("smtp client is not connected")
        await self._client.login(username, password)

    async def send_message(self, message: EmailMessage) -> object:
        """Submit ``message`` via SMTP DATA."""
        if self._client is None:
            raise RuntimeError("smtp client is not connected")
        return await self._client.send_message(message)

    async def quit(self) -> None:
        """Close the SMTP connection if open."""
        client = self._client
        self._client = None
        if client is None:
            return
        if client.is_connected:
            await client.quit()
        else:
            await client.close()

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.quit()


__all__ = [
    "AiomqttClient",
    "AiosmtpClient",
    "HttpxDatasetClient",
]
