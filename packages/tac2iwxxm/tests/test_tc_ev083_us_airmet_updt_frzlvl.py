"""TC-EV083 — US_FAA_NWS M17–M18 (#919 CONUS UPDT header + FRZLVL subsection).

[Corpus: product §F36] [Corpus: tests] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

from tac2iwxxm import convert
from tac2iwxxm.products.sigmet_airmet import parse_airmet

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "US_FAA_NWS"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def us_manifest() -> dict:
    return _load_manifest()


def test_tc_ev083_001_airmet_zulu_updt_ice(us_manifest: dict) -> None:
    """M17 — CONUS ``UPDT`` header + ``BTN FRZLVL`` vertical extent + inline FRZLVL."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "airmet_zulu_updt_ice")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    assert ir.get("header_style") == "conus_updt"
    assert ir.get("conus_series") == "ZULU"
    assert ir.get("conus_update") == 4
    assert ir.get("lower_surface") == "FRZLVL"
    assert ir.get("upper_fl") == 200
    assert ir.get("inline_frzlvl_lo") == 60
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok and result.xml
    assert "freezingLevel" in result.xml
    assert 'lowerLimit uom="FL">60</aixm:lowerLimit>' in result.xml
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev083_002_airmet_frzlvl_section(us_manifest: dict) -> None:
    """M18 — standalone ``FRZLVL...`` subsection emits ``FreezingLevelForecast``."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "airmet_frzlvl_section")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    section = ir.get("frzlvl_section")
    assert isinstance(section, dict)
    assert section.get("ranging_to") == 120
    assert len(section.get("isopleths", [])) == 1
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok and result.xml
    assert "FreezingLevelForecast" in result.xml
    assert "isopleth" in result.xml
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev083_003_ev082_regression_pack(us_manifest: dict) -> None:
    """EV-079..082 US_FAA_NWS manifest rows remain green."""
    prior_ids = {
        "airmet_ifr",
        "airmet_isol_ts",
        "airmet_ice_outlook",
        "airmet_mod_turb",
        "airmet_mod_turb_multi",
        "sigmet_conv_wst",
        "sigmet_obsc_ts",
        "sigmet_sev_ice",
        "sigmet_vor_chain",
        "sigmet_vor_single",
    }
    for case in us_manifest["cases"]:
        if case["id"] not in prior_ids:
            continue
        tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
        result = convert(tac, product=case["product"], profile=PROFILE, iwxxm_version=IWXXM_VERSION)
        assert result.ok, case["id"]
        expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
        assert canonicalize_xml(result.xml) == expected, case["id"]


def test_tc_ev083_004_parse_conus_variants() -> None:
    """Exercise CONUS/FRZLVL parser branches for coverage."""
    from tac2iwxxm.products.sigmet_airmet import _phenomenon_from_conus_for_text, parse_airmet

    assert _phenomenon_from_conus_for_text("TURB") == "MOD_TURB"
    assert _phenomenon_from_conus_for_text("IFR") == "SFC_VIS"
    assert _phenomenon_from_conus_for_text("MTN OBSC") == "MT_OBSC"

    hawaii = (
        "HNLT WA 091000\n"
        "AIRMET TANGO UPDATE 1 FOR TURB VALID UNTIL 091600\n"
        "AIRMET TURB...KAUAI\n"
        "MOD TURB BLW 100. CONDS CONT BYD 1600Z."
    )
    ir_hi = parse_airmet(hawaii)
    assert ir_hi["phenomenon"] == "MOD_TURB"
    assert ir_hi["conus_series"] == "TANGO"

    wmo = (
        "WAUS43 KKCI 091445 CHIZ WA 091445 "
        "AIRMET ZULU UPDT 1 FOR ICE VALID UNTIL 092100 "
        "AIRMET ICE...MO BOUNDED BY BAE-BVT MOD ICE BTN FRZLVL AND FL180."
    )
    ir_wmo = parse_airmet(wmo)
    assert ir_wmo["mwo"] == "KKCI"
    assert ir_wmo["lower_surface"] == "FRZLVL"

    mult = (
        "YUDD AIRMET 2 VALID 151520/152100 YUSO-\n"
        "YUDD SHANLON FIR MOD ICE OBS SFC/FL120 STNR NC\n"
        "FRZLVL...RANGING FROM SFC-120 ACRS AREA MULT FRZLVL 015-085 BOUNDED BY INL-YQT\n"
        "040 ALG GLD-SLN-30W BDF"
    )
    sec = parse_airmet(mult)["frzlvl_section"]
    assert sec["multiple_levels"] is True
    assert sec["multi_lo"] == 15


def test_tc_ev083_005_parse_edge_branches() -> None:
    """Cover remaining CONUS/outlook parser branches."""
    from tac2iwxxm.products.sigmet_airmet import (
        _phenomenon_from_conus_for_text,
        _strip_conus_airmet_lead,
        parse_airmet,
    )

    assert _strip_conus_airmet_lead("MOD TURB BLW 100") == "MOD TURB BLW 100"
    assert _strip_conus_airmet_lead("AIRMET TURB...HI MOD TURB BLW 100") == "MOD TURB BLW 100"
    assert _phenomenon_from_conus_for_text("UNKNOWN") == "TS"

    wmo = (
        "WAUS43 KKCI 091445 CHIZ WA 091445 "
        "AIRMET ZULU UPDT 1 FOR ICE VALID UNTIL 092100 "
        "AIRMET ICE...MO MOD ICE BTN FRZLVL AND FL180."
    )
    assert parse_airmet(wmo)["valid_from_hour"] == 14

    outlook_same_day = (
        "YUDD AIRMET 3 VALID 151400/152100 YUSO-\n"
        "YUDD SHANLON FIR MOD ICE OBS SFC/FL200 STNR NC\n"
        "OTLK VALID 1800-2000Z...MOD ICE MO BOUNDED BY BAE-BVT MOD ICE BTN FRZLVL AND FL200"
    )
    outlook = parse_airmet(outlook_same_day)["outlook"]
    assert outlook["valid_to_day"] == 15
