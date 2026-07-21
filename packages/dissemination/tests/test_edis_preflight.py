"""EDIS SMTP preflight connectivity tests (T4.3 / TC-F18 / E14-09).

Proves connect/login (or connect-only) without ``send_message`` — no live SMTP
in CI. Live RTH BYOC remains TC-F18-002.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dissemination.allowlist import EgressDenied, parse_allowlist
from dissemination.edis import EdisParams, edis_preflight
from dissemination.transports import AiosmtpClient


def _params(**overrides: Any) -> EdisParams:
    base = dict(
        smtp_host="smtp.gateway.example.test",
        smtp_port=587,
        mail_from="publisher@example.test",
        mail_to="rth@gateway.example.test",
        username="edis-user",
        password="secret-edis-token",
        use_tls=True,
        tt="SA",
        aa="US",
        ii="31",
        cccc="KZNY",
        yygggg="121200",
    )
    base.update(overrides)
    return EdisParams(**base)


def _allowlist(*hosts: str):
    return parse_allowlist(",".join(hosts))


@pytest.fixture(autouse=True)
def _public_dns_for_example_hosts():
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield


def _smtp_mock(*, login_side_effect: Exception | None = None) -> AsyncMock:
    smtp = AsyncMock()
    smtp.connect = AsyncMock()
    smtp.login = AsyncMock(side_effect=login_side_effect)
    smtp.send_message = AsyncMock()
    smtp.quit = AsyncMock()
    return smtp


@pytest.mark.asyncio
async def test_preflight_connect_login_quit_never_sends() -> None:
    smtp = _smtp_mock()
    result = await edis_preflight(
        _params(),
        allowlist=_allowlist("smtp.gateway.example.test"),
        smtp=smtp,
    )
    assert result.ok is True
    assert result.connectivity_ok is True
    assert result.diffs == []
    smtp.connect.assert_awaited_once()
    smtp.login.assert_awaited_once_with("edis-user", "secret-edis-token")
    smtp.quit.assert_awaited_once()
    smtp.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_preflight_skips_login_when_credentials_absent() -> None:
    smtp = _smtp_mock()
    result = await edis_preflight(
        _params(username=None, password=None),
        allowlist=_allowlist("smtp.gateway.example.test"),
        smtp=smtp,
    )
    assert result.ok is True
    assert result.connectivity_ok is True
    smtp.connect.assert_awaited_once()
    smtp.login.assert_not_awaited()
    smtp.quit.assert_awaited_once()
    smtp.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_preflight_denies_host_not_allowlisted() -> None:
    smtp = _smtp_mock()
    with pytest.raises(EgressDenied):
        await edis_preflight(
            _params(),
            allowlist=_allowlist("other.example.test"),
            smtp=smtp,
        )
    smtp.connect.assert_not_awaited()
    smtp.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_preflight_connect_failure_redacts_password() -> None:
    smtp = _smtp_mock()
    smtp.connect = AsyncMock(side_effect=RuntimeError("connect failed secret-edis-token"))
    with pytest.raises(ValueError) as excinfo:
        await edis_preflight(
            _params(),
            allowlist=_allowlist("smtp.gateway.example.test"),
            smtp=smtp,
        )
    assert "secret-edis-token" not in str(excinfo.value)
    assert "REDACTED" in str(excinfo.value)
    smtp.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_preflight_login_failure_redacts_and_quits() -> None:
    smtp = _smtp_mock(login_side_effect=RuntimeError("auth failed secret-edis-token"))
    with pytest.raises(ValueError) as excinfo:
        await edis_preflight(
            _params(),
            allowlist=_allowlist("smtp.gateway.example.test"),
            smtp=smtp,
        )
    assert "secret-edis-token" not in str(excinfo.value)
    assert "REDACTED" in str(excinfo.value)
    smtp.quit.assert_awaited_once()
    smtp.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_aiosmtp_client_connect_login_quit_no_send_via_mocked_lib() -> None:
    """AiosmtpClient wires aiosmtplib without ever calling send_message in preflight."""
    inner = AsyncMock()
    inner.connect = AsyncMock()
    inner.login = AsyncMock()
    inner.send_message = AsyncMock()
    inner.quit = AsyncMock()
    smtp_ctor = MagicMock(return_value=inner)
    with patch("dissemination.transports.aiosmtplib.SMTP", smtp_ctor):
        client = AiosmtpClient(
            hostname="smtp.gateway.example.test",
            port=587,
            use_tls=True,
        )
        result = await edis_preflight(
            _params(),
            allowlist=_allowlist("smtp.gateway.example.test"),
            smtp=client,
        )
    assert result.ok is True
    smtp_ctor.assert_called_once()
    kwargs = smtp_ctor.call_args.kwargs
    assert kwargs["hostname"] == "smtp.gateway.example.test"
    assert kwargs["port"] == 587
    assert kwargs.get("start_tls") is True
    inner.connect.assert_awaited_once()
    inner.login.assert_awaited_once_with("edis-user", "secret-edis-token")
    inner.quit.assert_awaited_once()
    inner.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_aiosmtp_client_smtps_port_uses_implicit_tls() -> None:
    inner = AsyncMock()
    inner.connect = AsyncMock()
    inner.quit = AsyncMock()
    smtp_ctor = MagicMock(return_value=inner)
    with patch("dissemination.transports.aiosmtplib.SMTP", smtp_ctor):
        client = AiosmtpClient(hostname="smtp.example.test", port=465, use_tls=True)
        await client.connect()
        await client.quit()
    kwargs = smtp_ctor.call_args.kwargs
    assert kwargs["use_tls"] is True
    assert kwargs.get("start_tls") is False
