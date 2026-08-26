"""TC-EV084 — US_FAA_NWS M19 (#919 WAUS multi-section AIRMET bulletin).

[Corpus: product §F36] [Corpus: tests] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

from tac2iwxxm import convert
from tac2iwxxm.geometry.reference_point import UnknownVOR, parse_vor_reference_geometry
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


def test_tc_ev084_001_airmet_waus_multisection(us_manifest: dict) -> None:
    """M19 — ICE + FROM geometry + inline FRZLVL + OTLK + FRZLVL subsection in one bulletin."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "airmet_waus_multisection")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    assert ir.get("header_style") == "conus_updt"
    assert ir.get("geometry", {}).get("kind") == "polygon"
    assert isinstance(ir.get("outlook"), dict)
    assert isinstance(ir.get("frzlvl_section"), dict)
    assert ir.get("inline_frzlvl_lo") == 60
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok and result.xml
    assert "gml:posList" in result.xml
    assert "FreezingLevelForecast" in result.xml
    assert "cond.chiz.outlook.1" in result.xml
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev084_002_vor_to_chain_and_wsw() -> None:
    """CONUS ``FROM … TO …`` chains and ``WSW`` bearings parse."""
    from tac2iwxxm.geometry.reference_point import ReferencePointGeometryParser

    with pytest.raises(UnknownVOR):
        parse_vor_reference_geometry("FROM 30WSW FOD TO DBQ TO 50NW DEC MOD ICE")
    known = parse_vor_reference_geometry(
        "FROM 10SSW EED TO 30NNE BZA TO 50S TRM TO 10SSW EED MOD ICE BTN FRZLVL AND FL200"
    )
    assert known is not None
    assert known["kind"] == "polygon"
    table = {"DBQ": {"lat": 42.0, "lon": -90.6}, "MKC": {"lat": 39.0, "lon": -94.7}}
    bare = ReferencePointGeometryParser(table).parse_from_body("FROM DBQ TO MKC MOD ICE")
    assert bare is not None
    assert len(bare.get("reference_points", [])) == 2


def test_tc_ev084_003_ev083_regression_pack(us_manifest: dict) -> None:
    """EV-079..083 US_FAA_NWS manifest rows remain green."""
    prior_ids = {
        "airmet_frzlvl_section",
        "airmet_ifr",
        "airmet_isol_ts",
        "airmet_ice_outlook",
        "airmet_mod_turb",
        "airmet_mod_turb_multi",
        "airmet_zulu_updt_ice",
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
