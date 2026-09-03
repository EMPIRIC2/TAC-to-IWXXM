"""TC-F16-OPS-001..003 — DisseminationGateway façade, health, plan execute (EV-936 / ADR-041)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from dissemination.allowlist import parse_allowlist
from dissemination.f19_stubs import F19_SINK_TYPES
from dissemination.gateway import (
    DeliveryReceipt,
    DisseminationGateway,
    DisseminationMessage,
    ValidationResult,
)
from dissemination.health import GatewayHealth, default_health_for_kind
from dissemination.models import PreflightResponse, SendResponse
from dissemination.plan import DisseminationPlan, execute_plan
from dissemination.sink import SinkAdapter


def _allowlist(*hosts: str):
    return parse_allowlist(",".join(hosts) if hosts else "127.0.0.1")


class _FakeAdapter:
    """Minimal SinkAdapter for gateway unit tests."""

    def __init__(self, sink_type: str = "postgres") -> None:
        self._sink_type = sink_type
        self.preflight = AsyncMock(
            return_value=PreflightResponse(
                ok=True,
                connectivity_ok=True,
                diffs=[],
                handle="h1",
                detail=None,
            )
        )
        self.send = AsyncMock(return_value=SendResponse(ok=True, kv_upload_key="k1", detail="sent"))

    @property
    def sink_type(self) -> str:
        return self._sink_type


@pytest.fixture
def adapter() -> _FakeAdapter:
    return _FakeAdapter("postgres")


@pytest.fixture
def gateway(adapter: _FakeAdapter) -> DisseminationGateway:
    return DisseminationGateway(adapters={"postgres": adapter})  # type: ignore[arg-type]


def test_fake_adapter_satisfies_sink_protocol(adapter: _FakeAdapter) -> None:
    assert isinstance(adapter, SinkAdapter)


@pytest.mark.asyncio
async def test_validate_dispatches_to_adapter_preflight(gateway: DisseminationGateway, adapter: _FakeAdapter) -> None:
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={"uri": "postgresql://u:p@127.0.0.1/db"},
        allowlist=_allowlist("127.0.0.1"),
    )
    result = await gateway.validate(msg)
    assert isinstance(result, ValidationResult)
    assert result.ok is True
    assert result.connectivity_ok is True
    adapter.preflight.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_maps_ok_to_delivered(gateway: DisseminationGateway, adapter: _FakeAdapter) -> None:
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={"uri": "postgresql://u:p@127.0.0.1/db"},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipt = await gateway.send(msg)
    assert isinstance(receipt, DeliveryReceipt)
    assert receipt.status == "DELIVERED"
    assert receipt.gateway == "postgres"
    assert receipt.attempt == 1
    assert receipt.completed_at is not None
    adapter.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_maps_adapter_failure_to_failed(gateway: DisseminationGateway, adapter: _FakeAdapter) -> None:
    adapter.send.return_value = SendResponse(ok=False, detail="sink refused")
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipt = await gateway.send(msg)
    assert receipt.status == "FAILED"
    assert receipt.detail == "sink refused"


@pytest.mark.asyncio
async def test_send_unknown_gateway_raises(gateway: DisseminationGateway) -> None:
    msg = DisseminationMessage(
        gateway_kind="wis2",
        params={},
        allowlist=_allowlist("127.0.0.1"),
    )
    with pytest.raises(KeyError, match="wis2"):
        await gateway.send(msg)


@pytest.mark.asyncio
async def test_validate_unknown_gateway_raises(gateway: DisseminationGateway) -> None:
    msg = DisseminationMessage(
        gateway_kind="edis",
        params={},
        allowlist=_allowlist("127.0.0.1"),
    )
    with pytest.raises(KeyError, match="edis"):
        await gateway.validate(msg)


@pytest.mark.parametrize("kind", list(F19_SINK_TYPES))
def test_default_health_f19_is_staging_honest(kind: str) -> None:
    h = default_health_for_kind(kind)
    assert isinstance(h, GatewayHealth)
    assert h.gateway == kind
    assert h.ok is False
    assert h.connectivity_ok is False
    assert h.detail is not None
    assert "staging" in h.detail.lower() or "live" in h.detail.lower()


def test_default_health_db_kind_not_probed() -> None:
    h = default_health_for_kind("postgres")
    assert h.ok is False
    assert h.connectivity_ok is False
    assert h.detail is not None


@pytest.mark.asyncio
async def test_health_all_kinds_uses_defaults() -> None:
    gw = DisseminationGateway(
        adapters={
            "postgres": _FakeAdapter("postgres"),  # type: ignore[arg-type]
            "amhs": _FakeAdapter("amhs"),  # type: ignore[arg-type]
        }
    )
    results = await gw.health()
    assert len(results) == 2
    by_kind = {r.gateway: r for r in results}
    assert by_kind["amhs"].ok is False
    assert by_kind["postgres"].connectivity_ok is False


@pytest.mark.asyncio
async def test_health_single_kind_with_custom_probe() -> None:
    async def probe(kind: str) -> GatewayHealth:
        return GatewayHealth(ok=True, gateway=kind, connectivity_ok=True, detail="reachable")

    gw = DisseminationGateway(
        adapters={"wis2": _FakeAdapter("wis2")},  # type: ignore[arg-type]
        health_probe=probe,
    )
    results = await gw.health("wis2")
    assert len(results) == 1
    assert results[0].ok is True
    assert results[0].connectivity_ok is True


@pytest.mark.asyncio
async def test_execute_plan_dry_run_skips_send(gateway: DisseminationGateway, adapter: _FakeAdapter) -> None:
    plan = DisseminationPlan(
        plan_id="p1",
        validity_policy="valid-only",
        destination_refs=["postgres"],
        dry_run=True,
    )
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipts = await execute_plan(plan, msg, gateway)
    assert len(receipts) == 1
    assert receipts[0].status == "SKIPPED"
    assert "dry" in (receipts[0].detail or "").lower()
    adapter.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_plan_sends_and_audits(gateway: DisseminationGateway, adapter: _FakeAdapter) -> None:
    audited: list[DeliveryReceipt] = []

    async def audit_sink(receipt: DeliveryReceipt) -> None:
        audited.append(receipt)

    plan = DisseminationPlan(
        plan_id="p2",
        validity_policy="warn-ok",
        destination_refs=["postgres"],
        dry_run=False,
    )
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipts = await execute_plan(plan, msg, gateway, audit_sink=audit_sink)
    assert len(receipts) == 1
    assert receipts[0].status == "DELIVERED"
    assert len(audited) == 1
    assert audited[0].status == "DELIVERED"
    adapter.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_plan_valid_only_sends_when_preflight_ok(
    gateway: DisseminationGateway, adapter: _FakeAdapter
) -> None:
    plan = DisseminationPlan(
        plan_id="p3b",
        validity_policy="valid-only",
        destination_refs=["postgres"],
    )
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipts = await execute_plan(plan, msg, gateway)
    assert receipts[0].status == "DELIVERED"
    adapter.preflight.assert_awaited()
    adapter.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_plan_valid_only_skips_when_preflight_fails(
    gateway: DisseminationGateway, adapter: _FakeAdapter
) -> None:
    adapter.preflight.return_value = PreflightResponse(
        ok=False,
        connectivity_ok=False,
        diffs=[],
        detail="unreachable",
    )
    plan = DisseminationPlan(
        plan_id="p3",
        validity_policy="valid-only",
        destination_refs=["postgres"],
    )
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipts = await execute_plan(plan, msg, gateway)
    assert receipts[0].status == "SKIPPED"
    adapter.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_plan_multi_destination() -> None:
    pg = _FakeAdapter("postgres")
    wis2 = _FakeAdapter("wis2")
    gw = DisseminationGateway(
        adapters={"postgres": pg, "wis2": wis2},  # type: ignore[arg-type]
    )
    plan = DisseminationPlan(
        plan_id="p4",
        validity_policy="warn-ok",
        destination_refs=["postgres", "wis2"],
    )
    base = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipts = await execute_plan(plan, base, gw)
    assert [r.gateway for r in receipts] == ["postgres", "wis2"]
    assert all(r.status == "DELIVERED" for r in receipts)


def test_delivery_receipt_completed_at_timezone() -> None:
    now = datetime.now(UTC)
    r = DeliveryReceipt(
        status="DELIVERED",
        gateway="postgres",
        completed_at=now,
    )
    assert r.completed_at == now


def test_dissemination_plan_defaults() -> None:
    plan = DisseminationPlan(
        plan_id="x",
        validity_policy="valid-only",
        destination_refs=[],
    )
    assert plan.transforms == []
    assert plan.retry is None
    assert plan.dry_run is False


@pytest.mark.asyncio
async def test_send_exception_becomes_failed_receipt(gateway: DisseminationGateway, adapter: _FakeAdapter) -> None:
    adapter.send.side_effect = ValueError("boom secret=should-redact")
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={},
        allowlist=_allowlist("127.0.0.1"),
        iwxxm_xml="<x/>",
    )
    receipt = await gateway.send(msg)
    assert receipt.status == "FAILED"
    assert receipt.detail is not None
