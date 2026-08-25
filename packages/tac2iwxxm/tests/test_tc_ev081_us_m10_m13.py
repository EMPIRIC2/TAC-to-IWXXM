"""TC-EV081 — US_FAA_NWS M10–M13 (#919 weather hazards, WST, TAF rules).

[Corpus: product §F36] [Corpus: tests] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml
from tac_validate import lint
from tac_validate.profiles import PROFILE_ANNEX3, PROFILE_IWXXM_US

from tac2iwxxm import convert
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "US_FAA_NWS"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def us_manifest() -> dict:
    return _load_manifest()


def test_tc_ev081_001_airmet_ifr_weather_hazards(us_manifest: dict) -> None:
    """M10 — IFR AIRMET emits ``AIRMETWeatherHazards`` with causingIFRConditions."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "airmet_ifr")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    assert ir.get("us_airmet_hazard", {}).get("causing_ifr_conditions") is True
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok and result.xml
    assert "AIRMETWeatherHazards" in result.xml
    assert 'causingIFRConditions="true"' in result.xml
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev081_002_convective_sigmet_wst(us_manifest: dict) -> None:
    """M11 — CONVECTIVE SIGMET parses and emits ``SIGMETWeatherHazards`` AreaTS."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "sigmet_conv_wst")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_sigmet(tac)
    assert ir.get("convective") is True
    assert ir.get("us_sigmet_hazard", {}).get("tag") == "11C"
    assert ir.get("geometry", {}).get("kind") == "polygon"
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok and result.xml
    assert "SIGMETWeatherHazards" in result.xml
    assert "AreaTS" in result.xml
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev081_003_us_taf_becmg_forbidden() -> None:
    """M13 — US_FAA_NWS lint rejects BECMG under iwxxm_us profile."""
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9000 BKN020 BECMG 1602/1604 15010KT="
    report = lint(tac, product="TAF", profile=PROFILE_IWXXM_US)
    codes = {i.code for i in report.issues}
    assert "US_TAF_BECMG_FORBIDDEN" in codes


def test_tc_ev081_004_us_taf_tempo_max_4h() -> None:
    """M13 — US_FAA_NWS lint rejects TEMPO windows longer than 4 hours."""
    tac = "TAF KJFK 151800Z 1600/1618 13005KT 9000 BKN020 TEMPO 1600/1605 15010KT="
    report = lint(tac, product="TAF", profile=PROFILE_IWXXM_US)
    codes = {i.code for i in report.issues}
    assert "US_TAF_TEMPO_MAX_4H" in codes


def test_tc_ev081_005_structured_visibility_fixtures_present(us_manifest: dict) -> None:
    """M12 — sector/tower/variable VIS goldens remain in US_FAA_NWS manifest (EV-063/M7)."""
    ids = {c["id"] for c in us_manifest["cases"]}
    assert {"rmk_sector_vis", "rmk_tower_vis", "rmk_var_vis"}.issubset(ids)


def _wst(*, until: str, body_tail: str, unit: str = "MKCC ", ahl: str = "") -> str:
    return (
        f"{ahl}{unit}CONVECTIVE SIGMET 11C VALID UNTIL {until} NE SD "
        f"FROM 30NNE FSD-60S OBH-60SE SNY-80W ANW-30NNE FSD {body_tail}"
    )


def test_tc_ev081_006_wst_until_hour_wrap() -> None:
    """M11 — VALID UNTIL 00xx wraps the 2-hour lookback across day boundary."""
    ir = parse_sigmet(_wst(until="090055Z", body_tail="AREA TS MOV FROM 21055KT. TOPS ABV FL450.="))
    assert ir["valid_to_hour"] == 0
    assert ir["valid_from_hour"] == 22
    assert ir["valid_from_day"] == 8


def test_tc_ev081_007_wst_hhmm_until_and_tops_to() -> None:
    """M11 — 4-digit UNTIL defaults day 9; TOPS TO FL sets top_qualifier TO."""
    ir = parse_sigmet(_wst(until="1055Z", body_tail="TOPS TO FL350.="))
    assert ir["valid_to_day"] == 9
    assert ir["valid_to_hour"] == 10
    assert ir["valid_to_minute"] == 55
    assert ir["top_fl"] == 350
    assert ir["top_qualifier"] == "TO"
    assert "motion_dir_deg" not in ir


def test_tc_ev081_008_wst_top_abv_blw_and_ahl() -> None:
    """M11 — TOP ABV/BLW and optional AHL prefix on convective SIGMET."""
    abv = parse_sigmet(_wst(until="091055Z", body_tail="TOP ABV FL450.="))
    assert abv["top_fl"] == 450
    assert abv["top_qualifier"] == "ABV"
    blw = parse_sigmet(_wst(until="091055Z", body_tail="TOP BLW FL180.="))
    assert blw["top_fl"] == 180
    assert blw["top_qualifier"] == "BLW"
    ahl = parse_sigmet(
        _wst(
            until="091055Z",
            body_tail="AREA TS MOV FROM 21055KT. TOPS ABV FL450.=",
            ahl="WSUS32 KKCI 091055\n",
        )
    )
    assert ahl["ahl_tt"] == "WS"
    assert ahl["convective"] is True


def test_tc_ev081_009_wst_default_unit_and_non_match() -> None:
    """M11 — missing issuing unit defaults MKCC; ordinary SIGMET is not convective."""
    ir = parse_sigmet(_wst(until="091055Z", body_tail="TOPS TO FL300.=", unit=""))
    assert ir["fir"] == "MKCC"
    ordinary = (
        "YUDD SIGMET 2 VALID 101200/101600 YUSO - YUDD FIR SEV TURB FCST "
        "WI N2700 E01700 - N2700 E02000 - N2500 E02000 - N2500 E01700 - N2700 E01700 "
        "FL250/370 MOV E 20KT NC="
    )
    assert parse_sigmet(ordinary).get("convective") is not True


def test_tc_ev081_010_taf_lint_isolation_and_tempo_ok() -> None:
    """M13 — annex3 does not apply US TAF codes; TEMPO ≤4h is allowed."""
    becmg = "TAF KJFK 151800Z 1600/1618 13005KT 9000 BKN020 BECMG 1602/1604 15010KT="
    annex = lint(becmg, product="TAF", profile=PROFILE_ANNEX3)
    assert "US_TAF_BECMG_FORBIDDEN" not in {i.code for i in annex.issues}
    tempo_ok = "TAF KJFK 151800Z 1600/1618 13005KT 9000 BKN020 TEMPO 1600/1604 15010KT="
    us_ok = lint(tempo_ok, product="TAF", profile=PROFILE_IWXXM_US)
    assert "US_TAF_TEMPO_MAX_4H" not in {i.code for i in us_ok.issues}
