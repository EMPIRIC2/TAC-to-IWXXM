"""EV-013 / #667 — METAR remarks must not be silently ignored."""

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
