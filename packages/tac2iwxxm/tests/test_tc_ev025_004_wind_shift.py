"""TC-EV025-004 / M4.1 - AerodromeWindShift (WSHFT / FROPA).

Asserts ``iwxxm-us:AerodromeWindShift`` under ``iwxxm:AerodromeSurfaceWind``
extension for FMH-1 ``WSHFT hhmm`` and ``WSHFT hhmm FROPA``.

XML pins follow iwxxm-us 3.0 PDF sample instances
(local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm.products.metar_speci import parse_metar_speci

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# FMH-1 wind shift at 17:15 without frontal passage.
_TAC_WSHFT = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WSHFT 1715="

# PDF sample: wind shift with frontal passage.
_TAC_WSHFT_FROPA = "METAR KJFK 231751Z 27018KT 10SM SCT040 15/07 A3005 RMK AO2 WSHFT 0210 FROPA="


def test_tc_ev025_004_wshft_parses_ir() -> None:
    """Parse must extract wind-shift time from WSHFT hhmm."""
    ir = parse_metar_speci(_TAC_WSHFT, product="METAR")
    assert ir.get("wind_shift_hour") == 17
    assert ir.get("wind_shift_minute") == 15
    assert ir.get("wind_shift_frontal_passage") is False


def test_tc_ev025_004_wshft_fropa_parses_ir() -> None:
    """Parse must set frontal-passage when FROPA follows WSHFT."""
    ir = parse_metar_speci(_TAC_WSHFT_FROPA, product="METAR")
    assert ir.get("wind_shift_hour") == 2
    assert ir.get("wind_shift_minute") == 10
    assert ir.get("wind_shift_frontal_passage") is True


def test_tc_ev025_004_wshft_emits_aerodrome_wind_shift() -> None:
    """Convert iwxxm_us must emit AerodromeWindShift with timeOfWindShift."""
    result = convert(
        _TAC_WSHFT,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:AerodromeWindShift" in xml
    assert "iwxxm-us:timeOfWindShift" in xml
    assert "2023-06-23T17:15:00Z" in xml
    assert 'frontalPassage="true"' not in xml
    # Structured WSHFT must not remain only as free-text (consumed into extension).
    if "humanReadableText" in xml:
        free = xml.split("humanReadableText", 1)[1]
        assert "WSHFT" not in free


def test_tc_ev025_004_wshft_fropa_emits_frontal_passage() -> None:
    """Convert iwxxm_us must set frontalPassage when FROPA present."""
    result = convert(
        _TAC_WSHFT_FROPA,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert 'iwxxm-us:AerodromeWindShift frontalPassage="true"' in xml
    assert "2023-06-23T02:10:00Z" in xml


def test_tc_ev025_004_wshft_coexists_with_peak_wind() -> None:
    """Peak wind and wind shift must both emit under surfaceWind."""
    tac = "METAR KJFK 231751Z 31016G30KT 10SM FEW040 15/07 A3005 RMK AO2 PK WND 31030/1431 WSHFT 1715="
    result = convert(
        tac,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:AerodromePeakWind" in xml
    assert "iwxxm-us:AerodromeWindShift" in xml
