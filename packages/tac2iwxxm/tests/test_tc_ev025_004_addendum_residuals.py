"""TC-EV025-004 / M4.6 - Addendum residuals + RecentWeather.

Asserts PRESFR/PRESRR, maintenance ``$``, CONTRAILS/AURORA/NOSPECI flags,
and FMH-1 precip begin/end → ``RecentWeather`` under ``iwxxm_us``.
"""

from __future__ import annotations

from tac2iwxxm.products.metar_speci import parse_metar_speci

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

_PRES_FALLING = "https://codes.nws.noaa.gov/FMH-1/PressureChangingRapidly/FALLING"
_PRES_RISING = "https://codes.nws.noaa.gov/FMH-1/PressureChangingRapidly/RISING"
_WX_RA = "http://codes.wmo.int/306/4678/RA"

_TAC_PRESFR = "METAR KJFK 231751Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 PRESFR="
_TAC_PRESRR = "METAR KJFK 231751Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 PRESRR="
_TAC_FLAGS = "METAR KJFK 231751Z AUTO 18008KT 10SM CLR 15/07 A3005 RMK AO2 CONTRAILS AURORA NOSPECI $="
_TAC_RECENT = "METAR KJFK 231751Z 18008KT 5SM -RA BKN012 14/12 A2998 RMK AO2 RAB28E32="


def test_tc_ev025_004_presfr_emits() -> None:
    """PRESFR → pressureChangeIndicator FALLING."""
    result = convert(
        _TAC_PRESFR,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert f'pressureChangeIndicator xlink:href="{_PRES_FALLING}"' in xml
    assert "PRESFR" not in xml


def test_tc_ev025_004_presrr_emits() -> None:
    """PRESRR → pressureChangeIndicator RISING."""
    result = convert(
        _TAC_PRESRR,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert f'pressureChangeIndicator xlink:href="{_PRES_RISING}"' in xml


def test_tc_ev025_004_addendum_flags_emits() -> None:
    """CONTRAILS / AURORA / NOSPECI / $ → boolean Addendum flags."""
    ir = parse_metar_speci(_TAC_FLAGS, product="METAR")
    assert ir.get("condensation_trail") is True
    assert ir.get("aurora") is True
    assert ir.get("no_specials") is True
    assert ir.get("maintenance_indicator") is True

    result = convert(
        _TAC_FLAGS,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "<iwxxm-us:condensationTrail>true</iwxxm-us:condensationTrail>" in xml
    assert "<iwxxm-us:aurora>true</iwxxm-us:aurora>" in xml
    assert "<iwxxm-us:noSpecials>true</iwxxm-us:noSpecials>" in xml
    assert "<iwxxm-us:maintenanceIndicator>true</iwxxm-us:maintenanceIndicator>" in xml
    assert "CONTRAILS" not in xml
    assert "NOSPECI" not in xml


def test_tc_ev025_004_recent_weather_emits() -> None:
    """RAB28E32 → RecentWeather RA with begin/end on observation hour."""
    ir = parse_metar_speci(_TAC_RECENT, product="METAR")
    recent = ir.get("recent_weather_us")
    assert isinstance(recent, list)
    assert len(recent) == 1
    assert recent[0].get("phenomenon_href") == _WX_RA
    assert recent[0].get("begin_minute") == 28
    assert recent[0].get("end_minute") == 32

    result = convert(
        _TAC_RECENT,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:RecentWeather" in xml
    assert _WX_RA in xml
    assert "<gml:beginPosition>2023-06-23T17:28:00Z</gml:beginPosition>" in xml
    assert "<gml:endPosition>2023-06-23T17:32:00Z</gml:endPosition>" in xml
    assert "RAB28E32" not in xml
