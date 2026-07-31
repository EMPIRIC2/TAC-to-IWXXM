"""TC-EV025-003 / #812 — SnowIncrease + sensor outage (UJ-040).

Asserts ``iwxxm-us:SnowIncrease`` (SNINCR) and ``InoperativeSensors`` /
``FailedSensors`` / ``MeteorologicalSensors`` under ``profile=iwxxm_us``.

TAC shapes follow FMH-1; XML pins follow iwxxm-us 3.0 PDF sample instances
(local ``.local/reference/iwxxm-us-metar-speci-pdf/``).
"""

from __future__ import annotations

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# PDF SnowIncrease sample: 2 in/h increase, 11 in on ground → FMH-1 SNINCR ii/dd.
_TAC_SNINCR = "METAR KJFK 231751Z 18008KT 2SM -SN BKN008 00/M01 A2992 RMK AO2 SNINCR 2/11="

# PDF InoperativeSensors sample: inoperative ceilometer → FMH-1 CHINO.
_TAC_CHINO = "METAR KJFK 231751Z 18008KT 10SM SCT040 25/18 A2992 RMK AO2 CHINO="

_SNOW_ELEMENT_HREF = "https://codes.nws.noaa.gov/FMH-1/StatisticallyProcessedWeatherElement/SNOW"
_CEILING_SENSOR_HREF = "https://codes.nws.noaa.gov/FMH-1/Sensor/CEILING"


def test_tc_ev025_003_snincr_emits_snow_increase() -> None:
    """Convert iwxxm_us must emit SnowIncrease with depth increase + total depth."""
    result = convert(
        _TAC_SNINCR,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:SnowIncrease" in xml
    assert "iwxxm-us:snowDepthIncrease" in xml
    assert "iwxxm-us:snowDepth" in xml
    assert _SNOW_ELEMENT_HREF in xml
    assert ">2<" in xml or ">2</" in xml
    assert ">11<" in xml or ">11</" in xml


def test_tc_ev025_003_chino_emits_inoperative_failed_sensors() -> None:
    """Convert iwxxm_us must emit InoperativeSensors wrapping FailedSensors CEILING."""
    result = convert(
        _TAC_CHINO,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:InoperativeSensors" in xml
    assert "iwxxm-us:FailedSensors" in xml
    assert _CEILING_SENSOR_HREF in xml
