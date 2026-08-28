"""TC-EV086 - EUR_RODEX + AFI + CAR_SAM exchange profile stubs (#921 / EV-086)."""

from __future__ import annotations

import pytest
from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.exchange_registry import (
    known_exchange_profile_ids,
    resolve_exchange_profile,
)
from dissemination.packaging import apply_exchange_packaging

_MEMBER_XML = (
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="uuid.member"><iwxxm:observation/></iwxxm:METAR>'
)

_STUB_WIRE_IDS = ("EUR_RODEX", "AFI", "CAR_SAM")
_STUB_CANONICAL = ("eur_rodex", "afi", "car_sam")


@pytest.mark.parametrize(
    ("wire_id", "canonical"),
    list(zip(_STUB_WIRE_IDS, _STUB_CANONICAL, strict=True)),
)
def test_tc_ev086_001_registry_resolves_regional_stubs(wire_id: str, canonical: str) -> None:
    """TC-EV086-001 - Registry resolves EUR_RODEX, AFI, CAR_SAM."""
    ids = known_exchange_profile_ids()
    assert wire_id in ids
    assert canonical in ids
    resolved = resolve_exchange_profile(wire_id)
    assert resolved is not None
    assert resolved.wire_id == wire_id
    assert resolved.canonical == canonical


@pytest.mark.parametrize("wire_id", _STUB_WIRE_IDS)
def test_tc_ev086_002_packaging_collect_for_each_stub(wire_id: str) -> None:
    """TC-EV086-002 - Each stub COLLECT-wraps via GLOBAL_AFS baseline."""
    bid = f"A_{wire_id}_SAMPLE.xml"
    packaged = apply_exchange_packaging(
        _MEMBER_XML,
        exchange_profile=wire_id,
        bulletin_identifier=bid,
    )
    assert is_collect_bulletin(packaged)
    assert bid in packaged
    assert "iwxxm:METAR" in packaged


def test_tc_ev086_003_unknown_exchange_fail_closed() -> None:
    """TC-EV086-003 - Garbage exchange id still rejected."""
    with pytest.raises(ValueError, match="unknown exchange profile"):
        apply_exchange_packaging(_MEMBER_XML, exchange_profile="NOT_A_REAL_EXCHANGE")


def test_tc_ev086_004_ev065_regression_global_afs_and_apac() -> None:
    """TC-EV086-004 - GLOBAL_AFS + APAC_ROBEX paths unchanged."""
    for profile, bid in (("GLOBAL_AFS", "A_GLOBAL.xml"), ("APAC_ROBEX", "A_APAC.xml")):
        packaged = apply_exchange_packaging(
            _MEMBER_XML,
            exchange_profile=profile,
            bulletin_identifier=bid,
        )
        assert is_collect_bulletin(packaged)
        assert bid in packaged
