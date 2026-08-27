"""TC-EV063-001..003 - semantic profile canonical ids + aliases (EV-063 / F35)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
METAR_BASIC_TAC = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8")
US_RMK_TAC = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP149 PK WND 20032/2118="


@pytest.mark.parametrize(
    ("profile_a", "profile_b"),
    [
        ("annex3", "ICAO_2025"),
        ("ICAO_2025", "annex3"),
    ],
)
def test_tc_ev063_001_alias_annex3_equiv_icao_2025(profile_a: str, profile_b: str) -> None:
    """Alias annex3 and canonical ICAO_2025 produce identical IWXXM."""
    result_a = convert(METAR_BASIC_TAC, product="METAR", profile=profile_a)
    result_b = convert(METAR_BASIC_TAC, product="METAR", profile=profile_b)
    assert result_a.ok
    assert result_b.ok
    assert result_a.xml == result_b.xml
    assert result_a.semantic_profile == "icao_2025"
    assert result_b.semantic_profile == "icao_2025"


def test_tc_ev063_001_alias_annex3_deprecation_signal() -> None:
    result = convert(METAR_BASIC_TAC, product="METAR", profile="annex3")
    assert result.ok
    assert result.deprecated_alias_used
    codes = {issue.code for issue in result.issues}
    assert "DEPRECATED_PROFILE_ALIAS" in codes


@pytest.mark.parametrize(
    ("profile_a", "profile_b"),
    [
        ("iwxxm_us", "US_FAA_NWS"),
        ("US_FAA_NWS", "iwxxm_us"),
    ],
)
def test_tc_ev063_002_us_faa_nws_equiv_iwxxm_us(profile_a: str, profile_b: str) -> None:
    result_a = convert(US_RMK_TAC, product="METAR", profile=profile_a)
    result_b = convert(US_RMK_TAC, product="METAR", profile=profile_b)
    assert result_a.ok
    assert result_b.ok
    assert result_a.xml == result_b.xml
    assert result_a.semantic_profile == "us_faa_nws"
    assert "iwxxm-us:Addendum" in result_a.xml or "humanReadableText" in result_a.xml


def test_tc_ev063_003_unknown_semantic_profile() -> None:
    result = convert(METAR_BASIC_TAC, product="METAR", profile="NOT_A_PROFILE")
    assert not result.ok
    assert result.issues[0].code == "UNSUPPORTED_PROFILE"
