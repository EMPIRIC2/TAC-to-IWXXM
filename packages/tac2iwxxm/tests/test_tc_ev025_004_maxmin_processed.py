"""TC-EV025-004 / M4.5 - MaxMinTemperatures + ProcessedProperty + ObservingSystem.

Asserts FMH-1 additive ``1``/``2``/``4`` max-min, precip ``P``/``6``/``7`` as
``processedQuantity``, and ``AO1``/``AO2`` ObservingSystemType hrefs under
``iwxxm_us``.

XML pins follow iwxxm-us 3.0 PDF sample shapes
(local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm.products.metar_speci import parse_metar_speci

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# 6-h max 15.6 °C / min 7.0 °C (1/2 snTTT).
_TAC_MAXMIN_6H = "METAR KJFK 231751Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 10156 20070="

# 24-h max 21.1 °C / min -2.2 °C (4snTTTsnTTT).
_TAC_MAXMIN_24H = "METAR KJFK 231251Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 402111022="

# Hourly precip 0.15 in (Prrrr).
_TAC_PRECIP_P = "METAR KJFK 231751Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 P0015="

# Trace precip P0000 → BELOW 0.01 in (PDF ProcessedProperty sample).
_TAC_PRECIP_TRACE = "METAR KJFK 231751Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 P0000="

# 3-/6-h precip group 6RRRR (0.35 in) - period from observation hour.
_TAC_PRECIP_6 = "METAR KJFK 231851Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 60035="

# 24-h precip 7R24R24R24 (1.23 in).
_TAC_PRECIP_7 = "METAR KJFK 231251Z 18008KT 10SM CLR 15/07 A3005 RMK AO2 70123="

_TAC_AO1 = "METAR KJFK 231751Z AUTO 18008KT 10SM CLR 15/07 A3005 RMK AO1="

_PRECIP_ELEM = "https://codes.nws.noaa.gov/FMH-1/StatisticallyProcessedWeatherElement/PRECIPITATION"
_STAT_ACCUM = "http://codes.wmo.int/grib2/codeflag/4.10/1"
_OBS_AO1 = "https://codes.nws.noaa.gov/FMH-1/ObservingSystemType/AO1"
_OBS_AO2 = "https://codes.nws.noaa.gov/FMH-1/ObservingSystemType/AO2"


def test_tc_ev025_004_maxmin_6h_parses() -> None:
    """Parse 1snTTT + 2snTTT into max_min_temperatures PT6H."""
    ir = parse_metar_speci(_TAC_MAXMIN_6H, product="METAR")
    rows = ir.get("max_min_temperatures")
    assert isinstance(rows, list)
    assert len(rows) == 1
    row = rows[0]
    assert row.get("preceding_period") == "PT6H"
    assert row.get("max_c") == 15.6
    assert row.get("min_c") == 7.0


def test_tc_ev025_004_maxmin_6h_emits() -> None:
    """Convert must emit MaxMinTemperatures PT6H on Addendum."""
    result = convert(
        _TAC_MAXMIN_6H,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:MaxMinTemperatures" in xml
    assert "<iwxxm-us:precedingPeriod>PT6H</iwxxm-us:precedingPeriod>" in xml
    assert 'maxTemperature uom="Cel">15.6</iwxxm-us:maxTemperature>' in xml
    assert 'minTemperature uom="Cel">7.0</iwxxm-us:minTemperature>' in xml
    assert "10156" not in xml  # consumed from free-text when structured
    assert "20070" not in xml


def test_tc_ev025_004_maxmin_24h_emits() -> None:
    """4snTTTsnTTT → MaxMinTemperatures PT24H."""
    result = convert(
        _TAC_MAXMIN_24H,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:MaxMinTemperatures" in xml
    assert "<iwxxm-us:precedingPeriod>PT24H</iwxxm-us:precedingPeriod>" in xml
    assert 'maxTemperature uom="Cel">21.1</iwxxm-us:maxTemperature>' in xml
    assert 'minTemperature uom="Cel">-2.2</iwxxm-us:minTemperature>' in xml


def test_tc_ev025_004_processed_precip_p_emits() -> None:
    """P0015 → processedQuantity PRECIPITATION PT1H 0.15 in."""
    ir = parse_metar_speci(_TAC_PRECIP_P, product="METAR")
    qty = ir.get("processed_quantities")
    assert isinstance(qty, list)
    assert len(qty) == 1
    assert qty[0].get("value_period") == "PT1H"
    assert qty[0].get("processed_value") == 0.15

    result = convert(
        _TAC_PRECIP_P,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "iwxxm-us:ProcessedProperty" in xml
    assert "iwxxm-us:processedQuantity" in xml
    assert _PRECIP_ELEM in xml
    assert _STAT_ACCUM in xml
    assert "<iwxxm-us:valuePeriod>PT1H</iwxxm-us:valuePeriod>" in xml
    assert 'processedValue uom="[in_i]">0.15</iwxxm-us:processedValue>' in xml
    assert "P0015" not in xml


def test_tc_ev025_004_processed_precip_trace_below() -> None:
    """P0000 → BELOW qualifier + 0.01 in (PDF sample)."""
    result = convert(
        _TAC_PRECIP_TRACE,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "<iwxxm-us:qualifier>BELOW</iwxxm-us:qualifier>" in xml
    assert 'processedValue uom="[in_i]">0.01</iwxxm-us:processedValue>' in xml


def test_tc_ev025_004_processed_precip_6_emits() -> None:
    """6RRRR at 18Z → PT6H precipitation accumulation."""
    ir = parse_metar_speci(_TAC_PRECIP_6, product="METAR")
    qty = ir.get("processed_quantities")
    assert isinstance(qty, list)
    assert any(q.get("value_period") == "PT6H" and q.get("processed_value") == 0.35 for q in qty)

    result = convert(
        _TAC_PRECIP_6,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "<iwxxm-us:valuePeriod>PT6H</iwxxm-us:valuePeriod>" in xml
    assert 'processedValue uom="[in_i]">0.35</iwxxm-us:processedValue>' in xml


def test_tc_ev025_004_processed_precip_7_emits() -> None:
    """7R24R24R24 → PT24H precipitation."""
    result = convert(
        _TAC_PRECIP_7,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert "<iwxxm-us:valuePeriod>PT24H</iwxxm-us:valuePeriod>" in xml
    assert 'processedValue uom="[in_i]">1.23</iwxxm-us:processedValue>' in xml


def test_tc_ev025_004_observing_system_ao1_href() -> None:
    """AO1 must emit ObservingSystemType codelist href."""
    result = convert(
        _TAC_AO1,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"failed: {result.issues!r}"
    xml = result.xml or ""
    assert f'observingSystemType xlink:href="{_OBS_AO1}"' in xml
    assert _OBS_AO2 not in xml
