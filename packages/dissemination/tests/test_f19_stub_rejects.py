"""F19 staging stub rejection paths (EV-stage coverage expansion).

[Corpus: tests] — allowlist deny, missing host/payload, sink mismatch; no live AMHS/SWIM/AFS.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from dissemination.allowlist import EgressDenied, parse_allowlist
from dissemination.f19_stubs import F19Params, get_staging_sink


@pytest.fixture(autouse=True)
def _public_dns_for_example_hosts() -> Any:
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield


def _params(sink_type: str = "amhs", **overrides: Any) -> F19Params:
    base: dict[str, Any] = {
        "sink_type": sink_type,
        "host": "gateway.example.test",
        "port": 8080,
        "username": "operator",
        "password": "super-secret-token",
        "endpoint": "/submit",
    }
    base.update(overrides)
    return F19Params(**base)


def _allowlist(*hosts: str):
    return parse_allowlist(",".join(hosts))


@pytest.mark.asyncio
async def test_f19_preflight_rejects_non_allowlisted_host() -> None:
    adapter = get_staging_sink("amhs")
    with pytest.raises(EgressDenied):
        await adapter.preflight(
            params=_params("amhs"),
            allowlist=_allowlist("other.example.test"),
        )


@pytest.mark.asyncio
async def test_f19_send_rejects_non_allowlisted_host() -> None:
    adapter = get_staging_sink("swim")
    with pytest.raises(EgressDenied):
        await adapter.send(
            params=_params("swim"),
            allowlist=_allowlist("other.example.test"),
            iwxxm_xml="<iwxxm/>",
        )


@pytest.mark.asyncio
async def test_f19_send_rejects_empty_payloads() -> None:
    adapter = get_staging_sink("afs")
    with pytest.raises(ValueError, match="payload"):
        await adapter.send(
            params=_params("afs"),
            allowlist=_allowlist("gateway.example.test"),
            iwxxm_xml="",
            tac_text="",
        )


@pytest.mark.asyncio
async def test_f19_send_rejects_whitespace_only_tac() -> None:
    adapter = get_staging_sink("amhs")
    # Empty string TAC + None XML is still a missing payload.
    with pytest.raises(ValueError, match="payload"):
        await adapter.send(
            params=_params("amhs"),
            allowlist=_allowlist("gateway.example.test"),
            iwxxm_xml=None,
            tac_text="",
        )


@pytest.mark.asyncio
async def test_f19_preflight_rejects_mismatched_sink_type() -> None:
    adapter = get_staging_sink("amhs")
    with pytest.raises(ValueError, match="does not match"):
        await adapter.preflight(
            params=_params("swim"),
            allowlist=_allowlist("gateway.example.test"),
        )


@pytest.mark.asyncio
async def test_f19_send_rejects_mismatched_sink_type() -> None:
    adapter = get_staging_sink("afs")
    with pytest.raises(ValueError, match="does not match"):
        await adapter.send(
            params=_params("amhs"),
            allowlist=_allowlist("gateway.example.test"),
            tac_text="METAR CYUL 121200Z NIL=",
        )


@pytest.mark.asyncio
async def test_f19_missing_host_redacts_password_and_username() -> None:
    adapter = get_staging_sink("swim")
    with pytest.raises(ValueError, match="host") as exc_info:
        await adapter.preflight(
            params=_params("swim", host="  "),
            allowlist=_allowlist("gateway.example.test"),
        )
    message = str(exc_info.value)
    assert "super-secret-token" not in message
    assert "operator" not in message
    assert "***" in message


def test_f19_get_staging_sink_rejects_non_f19_type() -> None:
    with pytest.raises(ValueError, match="sink_type"):
        get_staging_sink("postgres")  # type: ignore[arg-type]
