"""TC-EV063 / #1025 — canonical wire ids; emit keys for engine only.

[Corpus: domain] [Corpus: product F35]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tac2iwxxm.profile_registry import (
    known_semantic_profile_ids,
    resolve_semantic_profile,
)

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
METAR_BASIC_TAC = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8")
US_RMK_TAC = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP149 PK WND 20032/2118="


def test_tc_ev063_001_canonical_icao_2025_convert_success() -> None:
    result = convert(METAR_BASIC_TAC, product="METAR", profile="ICAO_2025")
    assert result.ok
    assert result.xml
    assert result.semantic_profile == "icao_2025"
    assert result.profile == "annex3"
    assert result.deprecated_alias_used is False


@pytest.mark.parametrize("alias", ["annex3", "iwxxm_us"])
def test_tc_ev063_001_wire_resolve_rejects_former_aliases(alias: str) -> None:
    assert resolve_semantic_profile(alias) is None


def test_tc_ev063_002_us_faa_nws_canonical_convert() -> None:
    result = convert(US_RMK_TAC, product="METAR", profile="US_FAA_NWS")
    assert result.ok
    assert result.semantic_profile == "us_faa_nws"
    assert result.deprecated_alias_used is False
    assert "iwxxm-us:Addendum" in result.xml or "humanReadableText" in result.xml


def test_tc_ev063_002_emit_key_iwxxm_us_still_engine_ok() -> None:
    """Emit key remains valid for library convert; not a wire alias."""
    result = convert(US_RMK_TAC, product="METAR", profile="iwxxm_us")
    assert result.ok
    assert result.deprecated_alias_used is False


def test_tc_ev063_003_unknown_semantic_profile() -> None:
    result = convert(METAR_BASIC_TAC, product="METAR", profile="NOT_A_PROFILE")
    assert not result.ok
    assert result.issues[0].code == "UNSUPPORTED_PROFILE"


def test_resolve_rejects_removed_aliases_on_wire() -> None:
    assert resolve_semantic_profile("annex3") is None
    assert resolve_semantic_profile("iwxxm_us") is None
    assert "annex3" not in known_semantic_profile_ids()
    assert "iwxxm_us" not in known_semantic_profile_ids()


def test_resolve_canonical_success() -> None:
    resolved = resolve_semantic_profile("ICAO_2025")
    assert resolved is not None
    assert resolved.canonical == "icao_2025"
    assert resolved.emit_key == "annex3"
    assert resolved.alias_used is False
