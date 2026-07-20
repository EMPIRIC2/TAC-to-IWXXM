"""EV-013 / #667 — METAR remarks must not be silently ignored (TC-F6-013 / UJ-026)."""

from __future__ import annotations

from tac2iwxxm import convert
from tac2iwxxm.products.metar_speci import parse_metar_speci


def test_annex3_emits_remarks_excluded_when_rmk_present() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP176="
    result = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "iwxxm-us:Addendum" not in result.xml
    codes = [i.code for i in result.issues]
    assert "REMARKS_EXCLUDED" in codes
    excluded = next(i for i in result.issues if i.code == "REMARKS_EXCLUDED")
    assert excluded.severity == "info"
    assert "RMK" in (excluded.message or "").upper() or "remark" in (excluded.message or "").lower()


def test_annex3_no_remarks_excluded_without_rmk() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
    result = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok
    assert all(i.code != "REMARKS_EXCLUDED" for i in result.issues)


def test_iwxxm_us_retains_unparsed_remarks_as_human_readable_text() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WND DATA ESTMD="
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "iwxxm-us:Addendum" in result.xml
    assert "iwxxm-us:humanReadableText" in result.xml
    assert "WND DATA ESTMD" in result.xml
    assert "REMARKS_EXCLUDED" not in [i.code for i in result.issues]


def test_iwxxm_us_keeps_additive_t_and_p_in_free_text() -> None:
    tac = "METAR KJFK 231751Z AUTO 18012KT 10SM CLR 15/07 A3005 RMK AO2 SLP176 T01560070 P0001="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("remark_temp_tenths_c") == 15.6
    assert ir.get("remark_dewpoint_tenths_c") == 7.0
    assert ir.get("precip_inches") == 0.01
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "humanReadableText" in result.xml
    assert "T01560070" in result.xml
    assert "P0001" in result.xml
    assert "seaLevelPressure" in result.xml


def test_iwxxm_us_structured_only_remarks_omit_empty_human_readable() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP149="
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "observingSystemType" in result.xml
    assert "seaLevelPressure" in result.xml
    assert "humanReadableText" not in result.xml


def test_annex3_speci_emits_remarks_excluded_with_rmk_span() -> None:
    """SPECI follows the same annex3 exclusion bar as METAR (UJ-026)."""
    tac = "SPECI KJFK 231815Z 18015KT 3SM -RA BKN015 14/12 A2998 RMK AO2 P0003="
    result = convert(tac, product="SPECI", profile="annex3", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "iwxxm-us:" not in result.xml
    excluded = next(i for i in result.issues if i.code == "REMARKS_EXCLUDED")
    assert excluded.severity == "info"
    assert excluded.location == "remarks"
    assert excluded.start is not None and excluded.end is not None
    assert tac[excluded.start : excluded.end] == "RMK"


def test_parse_strips_structured_tokens_from_remarks_free_text() -> None:
    """AO/SLP/PK are consumed; T/P and plain language remain for never-drop emit."""
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 SLP176 PK WND 28045/1745 T01560070 P0001 WSHFT 1715="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("remarks_present") is True
    assert ir.get("observing_system_type") == "AO2"
    assert ir.get("sea_level_pressure_hpa") == 1017.6
    assert ir.get("peak_wind_dir_deg") == 280
    assert ir.get("peak_wind_speed_kt") == 45
    free = ir.get("remarks_free_text") or ""
    assert "AO2" not in free
    assert "SLP176" not in free
    assert "PK WND" not in free
    assert "T01560070" in free
    assert "P0001" in free
    assert "WSHFT 1715" in free


def test_iwxxm_us_peak_wind_and_free_text_coexist() -> None:
    """Structured PK WND emit must not drop leftover REMARKS (never-drop)."""
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 PK WND 28045/1745 VIRGA NE="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("remarks_free_text") == "VIRGA NE"
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "iwxxm-us:AerodromePeakWind" in result.xml
    assert '<iwxxm-us:windDirection uom="deg">280</iwxxm-us:windDirection>' in result.xml
    assert "<iwxxm-us:humanReadableText>VIRGA NE</iwxxm-us:humanReadableText>" in result.xml


def test_iwxxm_us_negative_tenths_temp_decoded_and_retained() -> None:
    """FMH-1 T1… sign bit → negative °C IR; token stays in free-text."""
    tac = "METAR KJFK 231751Z 27008KT 10SM CLR M02/M05 A3012 RMK AO2 T10221055="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("remark_temp_tenths_c") == -2.2
    assert ir.get("remark_dewpoint_tenths_c") == -5.5
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "T10221055" in result.xml


def test_iwxxm_us_plain_language_only_remarks_emit_addendum() -> None:
    """Remarks without AO/SLP/PK still get an Addendum via humanReadableText."""
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK TORNADO B13 12 NE="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("remarks_free_text") == "TORNADO B13 12 NE"
    assert ir.get("observing_system_type") is None
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "iwxxm-us:Addendum" in result.xml
    assert "TORNADO B13 12 NE" in result.xml
    assert "observingSystemType" not in result.xml


def test_iwxxm_us_escapes_special_chars_in_human_readable_text() -> None:
    """Free-text emit must XML-escape reserved characters."""
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK FOG & HAZE <1SM="
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "FOG &amp; HAZE &lt;1SM" in result.xml
    assert "FOG & HAZE <1SM" not in result.xml


def test_speci_iwxxm_us_retains_unparsed_remarks() -> None:
    """SPECI iwxxm_us never-drop path mirrors METAR."""
    tac = "SPECI KJFK 231815Z 18015KT 2SM BR BKN008 14/13 A2995 RMK AO2 VIS 1V3="
    result = convert(tac, product="SPECI", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert "iwxxm-us:humanReadableText" in result.xml
    assert "VIS 1V3" in result.xml
    assert all(i.code != "REMARKS_EXCLUDED" for i in result.issues)
