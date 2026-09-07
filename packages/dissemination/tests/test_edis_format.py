"""EDIS message format + mocked SMTP submit tests (T4.1 / TC-F18-001 / E14-05).

Format fixtures define the T4.2 API surface; mocked aiosmtplib proves submit wiring
without live RTH Washington (TC-F18-002 remains live BYOC close gate).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from dissemination.allowlist import EgressDenied, parse_allowlist
from dissemination.edis import (
    EdisParams,
    EdisSubmitResult,
    build_edis_message,
    edis_preflight,
    edis_submit,
    format_wmo_ahl,
)


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


def test_format_wmo_ahl_metar_shape() -> None:
    assert format_wmo_ahl(tt="SA", aa="US", ii="31", cccc="KZNY", yygggg="121200") == ("SAUS31 KZNY 121200")


def test_format_wmo_ahl_optional_bbb() -> None:
    assert (
        format_wmo_ahl(tt="SA", aa="US", ii="31", cccc="KZNY", yygggg="121200", bbb="CCA") == "SAUS31 KZNY 121200 CCA"
    )


def test_build_edis_message_ascii_with_ahl_and_body() -> None:
    params = _params()
    body = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/12 A3012="
    msg = build_edis_message(params, tac_body=body)
    assert msg.startswith("SAUS31 KZNY 121200\n")
    assert body in msg
    assert msg.isascii()


def test_build_edis_message_rejects_non_ascii() -> None:
    params = _params()
    with pytest.raises(ValueError, match="ASCII"):
        build_edis_message(params, tac_body="METAR KJFK 121151Z café=")


def test_build_edis_message_rejects_non_ascii_ahl_fields() -> None:
    params = _params(cccc="KJN¥")
    with pytest.raises(ValueError, match="ASCII"):
        build_edis_message(params, tac_body="METAR KJFK 121151Z 18008KT=")


@pytest.mark.asyncio
async def test_edis_preflight_ok_with_mocked_smtp() -> None:
    params = _params()
    smtp = AsyncMock()
    smtp.connect = AsyncMock()
    smtp.login = AsyncMock()
    smtp.quit = AsyncMock()
    result = await edis_preflight(
        params,
        allowlist=_allowlist("smtp.gateway.example.test"),
        smtp=smtp,
    )
    assert result.ok is True
    assert result.connectivity_ok is True
    smtp.connect.assert_awaited_once()
    smtp.login.assert_awaited_once()
    smtp.quit.assert_awaited_once()


@pytest.mark.asyncio
async def test_edis_preflight_denies_host_not_allowlisted() -> None:
    params = _params()
    smtp = AsyncMock()
    with pytest.raises(EgressDenied):
        await edis_preflight(params, allowlist=_allowlist("other.example.test"), smtp=smtp)
    smtp.connect.assert_not_awaited()


@pytest.mark.asyncio
async def test_edis_submit_sends_ascii_message_via_mocked_smtp() -> None:
    params = _params()
    smtp = AsyncMock()
    smtp.connect = AsyncMock()
    smtp.login = AsyncMock()
    smtp.send_message = AsyncMock()
    smtp.quit = AsyncMock()
    tac = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/12 A3012="
    result = await edis_submit(
        params,
        tac_body=tac,
        allowlist=_allowlist("smtp.gateway.example.test"),
        smtp=smtp,
    )
    assert isinstance(result, EdisSubmitResult)
    assert result.ok is True
    assert result.ahl == "SAUS31 KZNY 121200"
    smtp.send_message.assert_awaited_once()
    sent = smtp.send_message.await_args.args[0]
    payload = sent.as_string()
    assert "SAUS31 KZNY 121200" in payload
    assert tac in payload
    assert payload.isascii()


@pytest.mark.asyncio
async def test_edis_submit_redacts_password_in_errors() -> None:
    params = _params()
    smtp = AsyncMock()
    smtp.connect = AsyncMock(side_effect=RuntimeError("auth failed secret-edis-token"))
    with pytest.raises(ValueError, match=r".*") as excinfo:
        await edis_submit(
            params,
            tac_body="METAR KJFK 121151Z 18008KT=",
            allowlist=_allowlist("smtp.gateway.example.test"),
            smtp=smtp,
        )
    assert "secret-edis-token" not in str(excinfo.value)
    assert "REDACTED" in str(excinfo.value)


def test_format_wmo_ahl_unknown_tt_falls_back() -> None:
    # map_t1t2 miss → keep raw TT (edis 117-118).
    assert format_wmo_ahl(tt="ZZ", aa="US", ii="31", cccc="KZNY", yygggg="121200") == ("ZZUS31 KZNY 121200")


def test_format_wmo_ahl_invalid_bbb_raises() -> None:
    with pytest.raises(ValueError, match=r".*"):
        format_wmo_ahl(
            tt="SA",
            aa="US",
            ii="31",
            cccc="KZNY",
            yygggg="121200",
            bbb="YYZ",
        )


def test_build_edis_message_rejects_empty_body() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        build_edis_message(_params(), tac_body="   ")


@pytest.mark.asyncio
async def test_edis_submit_without_auth_and_redact_without_secrets() -> None:
    params = _params(username=None, password=None)
    smtp = AsyncMock()
    smtp.connect = AsyncMock()
    smtp.send_message = AsyncMock()
    smtp.quit = AsyncMock()
    result = await edis_submit(
        params,
        tac_body="METAR KJFK 121151Z 18008KT=",
        allowlist=_allowlist("smtp.gateway.example.test"),
        smtp=smtp,
    )
    assert result.ok is True
    smtp.login.assert_not_called()

    smtp_fail = AsyncMock()
    smtp_fail.connect = AsyncMock(side_effect=RuntimeError("boom"))
    with pytest.raises(ValueError, match="boom"):
        await edis_submit(
            params,
            tac_body="METAR KJFK 121151Z 18008KT=",
            allowlist=_allowlist("smtp.gateway.example.test"),
            smtp=smtp_fail,
        )


@pytest.mark.asyncio
async def test_edis_submit_reraises_egress_denied() -> None:
    params = _params()
    smtp = AsyncMock()
    smtp.connect = AsyncMock()
    smtp.login = AsyncMock()
    smtp.send_message = AsyncMock(side_effect=EgressDenied("blocked"))
    smtp.quit = AsyncMock()
    with pytest.raises(EgressDenied):
        await edis_submit(
            params,
            tac_body="METAR KJFK 121151Z 18008KT=",
            allowlist=_allowlist("smtp.gateway.example.test"),
            smtp=smtp,
        )


@pytest.fixture(autouse=True)
def _public_dns_for_example_hosts():
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield
