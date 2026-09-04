"""TC-EV082 - US_FAA_NWS M15-M16 (#919 outlook / multi-area AIRMET).

[Corpus: product §F36] [Corpus: tests] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac2iwxxm.products.sigmet_airmet import parse_airmet

from metar_shared.xml_canonical import canonicalize_xml
from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "US_FAA_NWS"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def us_manifest() -> dict:
    return _load_manifest()


def test_tc_ev082_001_airmet_ice_outlook(us_manifest: dict) -> None:
    """M15 - ``OTLK VALID`` outlook emits forecast analysis + ``validTimeSubPeriod``."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "airmet_ice_outlook")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    assert "outlook" in ir
    assert ir["outlook"]["valid_from_hour"] == 21
    assert ir["outlook"]["valid_to_hour"] == 3
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert 'timeIndicator="FORECAST"' in result.xml
    assert "validTimeSubPeriod" in result.xml
    assert "AIRMETEvolvingConditionExtension" in result.xml
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev082_002_airmet_mod_turb_multi(us_manifest: dict) -> None:
    """M16 - AND-joined areas emit multiple ``AIRMETEvolvingCondition`` members."""
    case = next(c for c in us_manifest["cases"] if c["id"] == "airmet_mod_turb_multi")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    assert len(ir.get("areas", [])) == 2
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert result.xml.count("<iwxxm:AIRMETEvolvingCondition ") == 2
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    assert canonicalize_xml(result.xml) == expected


def test_tc_ev082_003_ev081_regression_pack(us_manifest: dict) -> None:
    """EV-079..081 US_FAA_NWS manifest rows remain green."""
    prior_ids = {
        "airmet_ifr",
        "airmet_isol_ts",
        "airmet_mod_turb",
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
