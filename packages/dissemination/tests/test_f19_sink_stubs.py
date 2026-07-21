"""F19 adapter interface + staging stub behaviors (T5.1 / S-EV014-M2 / E14-05).

Defines the shared ``SinkAdapter`` contract (same interface as WIS2/EDIS) and the
staging/test-path behaviors for AMHS, SWIM, and AFS. Live F19 transport is optional
this cycle; T5.2 implements the stubs these tests describe.
"""

from __future__ import annotations

from typing import Any, get_args
from unittest.mock import patch

import pytest

from dissemination.allowlist import EgressDenied, parse_allowlist
from dissemination.f19_stubs import (
    F19_SINK_TYPES,
    F19Params,
    StagingSinkAdapter,
    get_staging_sink,
)
from dissemination.models import DRAWER_SINK_TYPES, SinkType
from dissemination.sink import SinkAdapter


@pytest.fixture(autouse=True)
def _public_dns_for_example_hosts():
    """Allowlist checks resolve hosts; map test FQDNs to a public address."""
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        yield


def _params(sink_type: str = "amhs", **overrides: Any) -> F19Params:
    base = dict(
        sink_type=sink_type,
        host="gateway.example.test",
        port=8080,
        username="operator",
        password="super-secret-token",
        endpoint="/submit",
    )
    base.update(overrides)
    return F19Params(**base)


def _allowlist(*hosts: str):
    return parse_allowlist(",".join(hosts))


@pytest.mark.parametrize("sink_type", ["amhs", "swim", "afs"])
def test_f19_sink_types_are_drawer_ready(sink_type: str) -> None:
    assert sink_type in get_args(SinkType)
    assert sink_type in F19_SINK_TYPES
    assert sink_type in DRAWER_SINK_TYPES


def test_drawer_sink_types_cover_f16_through_f19() -> None:
    expected = {
        "postgres",
        "mysql",
        "sqlserver",
        "sqlite",
        "wis2",
        "edis",
        "amhs",
        "swim",
        "afs",
    }
    assert set(DRAWER_SINK_TYPES) == expected
    assert set(F19_SINK_TYPES) == {"amhs", "swim", "afs"}


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
def test_staging_sink_implements_shared_adapter_interface(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    assert isinstance(adapter, SinkAdapter)
    assert isinstance(adapter, StagingSinkAdapter)
    assert adapter.sink_type == sink_type
    assert adapter.mode == "staging"


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
@pytest.mark.asyncio
async def test_staging_preflight_ok_without_live_transport(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    result = await adapter.preflight(
        params=_params(sink_type),
        allowlist=_allowlist("gateway.example.test"),
    )
    assert result.ok is True
    assert result.connectivity_ok is True
    assert result.diffs == []
    assert result.detail is None or "staging" in (result.detail or "").lower()


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
@pytest.mark.asyncio
async def test_staging_preflight_denies_host_not_allowlisted(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    with pytest.raises(EgressDenied):
        await adapter.preflight(
            params=_params(sink_type),
            allowlist=_allowlist("other.example.test"),
        )


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
@pytest.mark.asyncio
async def test_staging_send_ok_returns_staging_marker(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    result = await adapter.send(
        params=_params(sink_type),
        allowlist=_allowlist("gateway.example.test"),
        iwxxm_xml=b"<iwxxm/>",
    )
    assert result.ok is True
    assert result.kv_upload_key is not None
    assert sink_type in result.kv_upload_key
    assert "staging" in result.kv_upload_key.lower() or (
        result.detail is not None and "staging" in result.detail.lower()
    )


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
@pytest.mark.asyncio
async def test_staging_send_denies_host_not_allowlisted(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    with pytest.raises(EgressDenied):
        await adapter.send(
            params=_params(sink_type),
            allowlist=_allowlist("other.example.test"),
            iwxxm_xml="<iwxxm/>",
        )


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
@pytest.mark.asyncio
async def test_staging_send_requires_payload(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    with pytest.raises(ValueError, match="payload"):
        await adapter.send(
            params=_params(sink_type),
            allowlist=_allowlist("gateway.example.test"),
        )


@pytest.mark.parametrize("sink_type", list(F19_SINK_TYPES))
@pytest.mark.asyncio
async def test_staging_errors_redact_password(sink_type: str) -> None:
    adapter = get_staging_sink(sink_type)
    params = _params(sink_type, host="")
    with pytest.raises(ValueError) as exc_info:
        await adapter.preflight(
            params=params,
            allowlist=_allowlist("gateway.example.test"),
        )
    message = str(exc_info.value)
    assert "super-secret-token" not in message
    assert "***" in message or "host" in message.lower()


def test_get_staging_sink_rejects_unknown_type() -> None:
    with pytest.raises(ValueError, match="sink_type"):
        get_staging_sink("wis2")  # type: ignore[arg-type]
