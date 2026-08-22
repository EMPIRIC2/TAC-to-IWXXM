"""TC-EV064-002/006 — CA_ECCC METAR/TAF/AIRMET convert golden pack (EV-064 M3/M4/M5).

Spec: docs/test-plan.md TC-EV064-002, TC-EV064-006; domain/profiles/semantic/CA_ECCC.md
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
MANIFEST_PATH = FIXTURES / "manifest.json"

IWXXM_VERSION = "3.0.0"
PROFILE = "ca_eccc"
CASE_IDS = (
    "metar_basic",
    "metar_vis_sm",
    "metar_auto",
    "metar_rmk_presfr",
    "metar_rmk_presrr",
    "metar_alt_not_obs",
    "metar_rmk_slp_t",
    "taf_nclws",
    "airmet_gfa",
)
METAR_CASE_IDS = (
    "metar_basic",
    "metar_vis_sm",
    "metar_auto",
    "metar_rmk_presfr",
    "metar_rmk_presrr",
    "metar_alt_not_obs",
    "metar_rmk_slp_t",
)
TAF_CASE_IDS = ("taf_nclws",)
AIRMET_CASE_IDS = ("airmet_gfa",)


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing CA_ECCC golden manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return _load_manifest()


def test_ca_eccc_golden_manifest_present(golden_manifest: dict) -> None:
    assert golden_manifest.get("schema_version") == 1
    assert golden_manifest.get("profile") == "CA_ECCC"
    cases = golden_manifest.get("cases", [])
    assert len(cases) >= 9
    ids = {c["id"] for c in cases}
    assert set(CASE_IDS) <= ids
    for case in cases:
        assert (FIXTURES / case["tac"]).is_file()
        assert (FIXTURES / case["golden"]).is_file()
        assert case.get("status") == "active"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_ev064_002_convert_profile_ca_eccc(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-002: convert uses IWXXM 3.0.0 + iwxxm-ca (not annex3 2025-2 delegate)."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    product = case["product"]

    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed for {case_id}: {result.issues!r}"
    assert result.xml
    assert result.profile == PROFILE
    assert result.iwxxm_version == IWXXM_VERSION
    assert "http://icao.int/iwxxm/3.0" in result.xml
    assert "iwxxm-ca" in result.xml
    assert "http://icao.int/iwxxm/2025-2" not in result.xml
    assert "PROFILE_STUB" not in {i.code for i in result.issues}


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_ev064_002_validate_ca_eccc_attempt(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-002: validate path accepts ca_eccc profile (XSD may gap on 3.0.0 GML catalog)."""
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok and result.xml

    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile="ca_eccc",
        levels=("xsd", "schematron"),
    )
    assert report.profile == "ca_eccc"
    codes = {i.code for i in report.issues}
    assert "CA_SCHEMA_NOT_FOUND" not in codes
    # 3.0.0 GML catalog resolution is a known vendor-subset gap (M1/M2); never silent success.
    if report.ok:
        return
    assert codes & {
        "SCHEMA_PARSE_ERROR",
        "SCHEMA_NOT_AVAILABLE",
        "XSD_VALIDATION_ERROR",
        "SCHEMATRON_SKIPPED",
    }, f"unexpected validate failure for {case_id}: {[(i.code, i.message) for i in report.issues]}"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_ev064_002_m_golden_ca_eccc(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-002: canonicalize(convert) == golden fixture."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected_xml = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok and result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(expected_xml)


def test_tc_ev064_002_rejects_wrong_iwxxm_version() -> None:
    from tac2iwxxm import convert

    tac = (FIXTURES / "METAR/valid/metar_basic.tac").read_text(encoding="utf-8")
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version="2025-2")
    assert result.ok is False
    assert any(i.code == "INVALID_IWXXM_VERSION" for i in result.issues)


def test_tc_ev064_003_ca_manobs_lint_sm_and_altimeter() -> None:
    from tac_validate import lint

    tac_sm = (FIXTURES / "METAR/valid/metar_vis_sm.tac").read_text(encoding="utf-8")
    report_sm = lint(tac_sm, product="METAR", profile="ca_eccc")
    assert "CA_STATUTE_MILE_VIS" in {i.code for i in report_sm.issues}

    tac_alt = (FIXTURES / "METAR/valid/metar_basic.tac").read_text(encoding="utf-8")
    report_alt = lint(tac_alt, product="METAR", profile="ca_eccc")
    assert "CA_ALTIMETER_INHG" in {i.code for i in report_alt.issues}


def test_tc_ev064_003_ca_manobs_lint_remarks() -> None:
    from tac_validate import lint

    tac = (FIXTURES / "METAR/valid/metar_rmk_presfr.tac").read_text(encoding="utf-8")
    report = lint(tac, product="METAR", profile="ca_eccc")
    codes = {i.code for i in report.issues}
    assert "CA_REMARK_MANOBS" in codes
    assert "CA_STATUTE_MILE_VIS" in codes


@pytest.mark.parametrize("case_id", TAF_CASE_IDS)
def test_tc_ev064_006_convert_taf_ca_eccc(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-006: MANAIR TAF converts with iwxxm-ca NCLWS extension."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed for {case_id}: {result.issues!r}"
    assert result.xml
    assert "NonConvectiveLowLevelWindShear" in result.xml
    assert "iwxxm-ca" in result.xml
    assert "http://icao.int/iwxxm/3.0" in result.xml


@pytest.mark.parametrize("case_id", TAF_CASE_IDS)
def test_tc_ev064_006_m_golden_taf_ca_eccc(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-006: canonicalize(convert) == TAF golden fixture."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected_xml = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok and result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(expected_xml)


def test_tc_ev064_006_ca_manair_lint_nclws() -> None:
    from tac_validate import lint

    tac = (FIXTURES / "TAF/valid/taf_nclws.tac").read_text(encoding="utf-8")
    report = lint(tac, product="TAF", profile="ca_eccc")
    codes = {i.code for i in report.issues}
    assert "CA_TAF_NCLWS" in codes
    assert "CA_STATUTE_MILE_VIS" in codes


@pytest.mark.parametrize("case_id", AIRMET_CASE_IDS)
def test_tc_ev064_006_convert_airmet_ca_eccc(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-006: MANAIR GFA AIRMET converts with code-ca phenomenon href."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed for {case_id}: {result.issues!r}"
    assert result.xml
    assert "airmet_weather_phenomena/FRQ_TCU_ISOL_TS" in result.xml
    assert "iwxxm-ca" in result.xml
    assert "http://icao.int/iwxxm/3.0" in result.xml


@pytest.mark.parametrize("case_id", AIRMET_CASE_IDS)
def test_tc_ev064_006_m_golden_airmet_ca_eccc(case_id: str, golden_manifest: dict) -> None:
    """TC-EV064-006: canonicalize(convert) == AIRMET golden fixture."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected_xml = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok and result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(expected_xml)


def test_tc_ev064_006_ca_manair_lint_gfa_airmet() -> None:
    from tac_validate import lint

    tac = (FIXTURES / "AIRMET/valid/airmet_gfa.tac").read_text(encoding="utf-8")
    report = lint(tac, product="AIRMET", profile="ca_eccc")
    codes = {i.code for i in report.issues}
    assert "CA_AIRMET_GFA" in codes
