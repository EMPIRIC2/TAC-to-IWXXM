"""TC-EVBRIDGE-008 — Dissemination library transforms (send paths only)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from dissemination.allowlist import parse_allowlist
from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.gateway import DisseminationGateway, DisseminationMessage
from dissemination.models import PreflightResponse, SendResponse
from dissemination.plan import DisseminationPlan, execute_plan
from dissemination.transforms import (
    apply_dissemination_transforms,
    normalize_transform_steps,
)
from tac2iwxxm.library_assets import get_first_party_library_asset

_SAMPLE = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="m1">'
    "<iwxxm:observation/></iwxxm:METAR>"
)


def test_normalize_transform_steps_accepts_dicts_and_strings() -> None:
    steps = normalize_transform_steps(
        [
            {"id": "envelope", "type": "envelope"},
            "checksum",
        ]
    )
    assert [s.type for s in steps] == ["envelope", "checksum"]


def test_apply_transforms_envelope_and_checksum() -> None:
    seed = get_first_party_library_asset("LIB.DISSEMINATION.ICAO_2025")
    assert seed is not None
    result = apply_dissemination_transforms(
        _SAMPLE,
        seed.body["transforms"],
        bulletin_identifier="A_TEST.xml",
    )
    assert is_collect_bulletin(result.xml)
    assert "dissemination-checksum:" in result.xml
    assert "A_TEST.xml" in result.xml
    assert "envelope" in result.applied
    assert "checksum" in result.applied


def test_unknown_transform_type_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown dissemination transform"):
        apply_dissemination_transforms(_SAMPLE, [{"type": "not_a_real_step"}])


def test_empty_transforms_is_noop() -> None:
    result = apply_dissemination_transforms(_SAMPLE, [])
    assert result.xml == _SAMPLE
    assert result.applied == ()


def test_normalize_skips_none_non_list_empty_and_bad_items() -> None:
    assert normalize_transform_steps(None) == []
    assert normalize_transform_steps({"type": "envelope"}) == []
    assert normalize_transform_steps(["", "  ", 42, {"type": ""}, {"id": ""}]) == []
    steps = normalize_transform_steps([{"id": "only-id"}, {"type": "checksum", "params": "ignore"}])
    assert [s.type for s in steps] == ["only-id", "checksum"]
    assert steps[1].params == {}


def test_topic_filename_without_bulletin_id_uses_default() -> None:
    result = apply_dissemination_transforms(_SAMPLE, [{"type": "topic_filename"}])
    assert "A_UNKNOWN.xml" in result.xml
    assert "topic_filename" in result.applied


def test_checksum_without_xml_declaration_prefixes_comment() -> None:
    bare = '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"/>'
    result = apply_dissemination_transforms(bare, ["checksum"])
    assert result.xml.startswith("<!-- dissemination-checksum:")
    assert "checksum" in result.applied


def test_checksum_broken_xml_decl_falls_through() -> None:
    broken_decl = "<?xml version='1.0'<root/>"
    result = apply_dissemination_transforms(broken_decl, [{"type": "checksum"}])
    assert result.xml.startswith("<!-- dissemination-checksum:")


def test_bulletin_rewrap_non_collect_and_collect_without_member() -> None:
    non_collect = apply_dissemination_transforms(_SAMPLE, [{"type": "bulletin_rewrap"}])
    assert is_collect_bulletin(non_collect.xml)

    # Already-COLLECT without meteorologicalInformation: wrap is a no-op, path still runs.
    empty_collect = (
        '<?xml version="1.0"?>\n'
        "<collect:MeteorologicalBulletin "
        'xmlns:collect="http://def.wmo.int/collect/2014">'
        "<collect:bulletinIdentifier>A_OLD.xml</collect:bulletinIdentifier>"
        "</collect:MeteorologicalBulletin>"
    )
    rewrapped = apply_dissemination_transforms(
        empty_collect,
        [{"type": "bulletin_rewrap"}],
        bulletin_identifier="A_NEW.xml",
    )
    assert "bulletin_rewrap" in rewrapped.applied
    assert is_collect_bulletin(rewrapped.xml)
    assert "A_OLD.xml" in rewrapped.xml


def test_checksum_then_bulletin_rewrap_covers_elif_chain() -> None:
    result = apply_dissemination_transforms(
        _SAMPLE,
        ["checksum", "bulletin_rewrap"],
        bulletin_identifier="A_CHAIN.xml",
    )
    assert "checksum" in result.applied
    assert "bulletin_rewrap" in result.applied
    assert is_collect_bulletin(result.xml)


def test_topic_filename_when_wrap_omits_bulletin_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """_ensure_collect_then_set_bulletin_id falls through when id element is absent."""
    from dissemination import transforms as transforms_mod

    def _wrap_no_id(xml: str, *, bulletin_identifier: str | None = None) -> str:
        return (
            '<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014">'
            f"{xml}"
            "</collect:MeteorologicalBulletin>"
        )

    monkeypatch.setattr(transforms_mod, "wrap_global_afs_collect", _wrap_no_id)
    result = apply_dissemination_transforms(
        "<iwxxm:METAR/>",
        [{"type": "topic_filename", "params": {"filename": "A_FALLBACK.xml"}}],
    )
    assert "topic_filename" in result.applied
    assert "MeteorologicalBulletin" in result.xml


@pytest.mark.asyncio
async def test_execute_plan_applies_transforms_when_set() -> None:
    """plan.py lines 89-99: apply transforms when plan.transforms is set."""

    class _Adapter:
        sink_type = "postgres"

        def __init__(self) -> None:
            self.preflight = AsyncMock(
                return_value=PreflightResponse(ok=True, connectivity_ok=True, diffs=[], handle="h")
            )
            self.send = AsyncMock(return_value=SendResponse(ok=True, kv_upload_key="k", detail="ok"))

    adapter = _Adapter()
    gateway = DisseminationGateway(adapters={"postgres": adapter})  # type: ignore[arg-type]
    plan = DisseminationPlan(
        plan_id="p-xf",
        validity_policy="warn-ok",
        destination_refs=["postgres"],
        transforms=["checksum"],
    )
    msg = DisseminationMessage(
        gateway_kind="postgres",
        params={"bulletin_identifier": "A_PLAN.xml"},
        allowlist=parse_allowlist("127.0.0.1"),
        iwxxm_xml=_SAMPLE,
    )
    receipts = await execute_plan(plan, msg, gateway)
    assert receipts[0].status == "DELIVERED"
    assert "dissemination-checksum:" in adapter.send.await_args.kwargs["iwxxm_xml"]
    assert isinstance(receipts[0].completed_at, datetime)
    assert receipts[0].completed_at.tzinfo is UTC

    plan2 = DisseminationPlan(
        plan_id="p-xf2",
        validity_policy="warn-ok",
        destination_refs=["postgres"],
        transforms=["checksum"],
    )
    msg2 = DisseminationMessage(
        gateway_kind="postgres",
        params="not-a-dict",
        allowlist=parse_allowlist("127.0.0.1"),
        iwxxm_xml="<iwxxm:METAR/>",
    )
    receipts2 = await execute_plan(plan2, msg2, gateway)
    assert receipts2[0].status == "DELIVERED"
    assert "dissemination-checksum:" in adapter.send.await_args.kwargs["iwxxm_xml"]
