"""TC-EV079 — US_FAA_NWS SIGMET/AIRMET national layer slice (EV-079 / #919 M8).

Manifest-driven goldens under ``fixtures/profiles/US_FAA_NWS/`` exercise US SIGMET/AIRMET
phenomenon tokens and IWXXM-US namespace emit via canonical ``US_FAA_NWS``.

[Corpus: product §F36] [Corpus: tests §TC-EV079] [Corpus: domain-profiles §US_FAA_NWS]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

from tac2iwxxm import convert
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "US_FAA_NWS"

SIGMET_CASES = ("sigmet_obsc_ts", "sigmet_sev_ice")
AIRMET_CASES = ("airmet_isol_ts", "airmet_ifr", "airmet_mod_turb")


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing US_FAA_NWS manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def us_manifest() -> dict:
    return _load_manifest()


def test_tc_ev079_001_manifest_sigmet_airmet_rows(us_manifest: dict) -> None:
    """SIGMET/AIRMET slice lists ≥2 cases each with US rule ids."""
    cases = us_manifest.get("cases", [])
    sigmet = [c for c in cases if c.get("product") == "SIGMET"]
    airmet = [c for c in cases if c.get("product") == "AIRMET"]
    assert len(sigmet) >= 2
    assert len(airmet) >= 3
    for case in sigmet + airmet:
        rid = case.get("rule_id", "")
        assert rid.startswith("US.")
        assert (FIXTURES / case["tac"]).is_file()
        assert (FIXTURES / case["golden"]).is_file()


@pytest.mark.parametrize("case_id", SIGMET_CASES)
def test_tc_ev079_002_sigmet_phenomenon_tokens(case_id: str, us_manifest: dict) -> None:
    """US SIGMET parser maps OBSC TS and SEV ICE tokens."""
    case = next(c for c in us_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_sigmet(tac)
    if case_id == "sigmet_obsc_ts":
        assert ir["phenomenon"] == "OBSC_TS"
    else:
        assert ir["phenomenon"] == "SEV_ICE"
        assert ir.get("geometry", {}).get("kind") == "polygon"


@pytest.mark.parametrize(
    "case_id,expected",
    [
        ("airmet_isol_ts", "ISOL_TS"),
        ("airmet_ifr", "SFC_VIS"),
        ("airmet_mod_turb", "MOD_TURB"),
    ],
)
def test_tc_ev079_003_airmet_phenomenon_tokens(case_id: str, expected: str, us_manifest: dict) -> None:
    """US AIRMET parser maps IFR shorthand and MOD TURB tokens."""
    case = next(c for c in us_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    ir = parse_airmet(tac)
    assert ir["phenomenon"] == expected


@pytest.mark.parametrize("case_id", SIGMET_CASES + AIRMET_CASES)
def test_tc_ev079_004_sigmet_airmet_golden_convert(case_id: str, us_manifest: dict) -> None:
    """US_FAA_NWS SIGMET/AIRMET fixtures round-trip to M-goldens with iwxxm-us namespace."""
    case = next(c for c in us_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{case_id}: {result.issues!r}"
    assert result.xml
    assert "www.weather.gov/iwxxm-us" in result.xml
    assert canonicalize_xml(result.xml) == expected
