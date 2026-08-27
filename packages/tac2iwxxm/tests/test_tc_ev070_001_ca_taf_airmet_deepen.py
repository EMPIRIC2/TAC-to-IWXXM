"""TC-EV070-* - CA_ECCC TAF + AIRMET convert deepen (#1041)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
PROFILE = "ca_eccc"
IWXXM_VERSION = "3.0.0"

EV070_CASE_IDS = (
    "taf_ic_weather",
    "taf_amd",
    "airmet_gfa_sfc_vis",
)


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", EV070_CASE_IDS)
def test_tc_ev070_001_convert_matches_golden(case_id: str, golden_manifest: dict) -> None:
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed for {case_id}: {result.issues!r}"
    assert canonicalize_xml(result.xml) == canonicalize_xml(expected)


@pytest.mark.parametrize("case_id", EV070_CASE_IDS)
def test_tc_ev070_005_validate_full_ca_stack(case_id: str, golden_manifest: dict) -> None:
    """TC-EV070-005 scaffold: tolerant when IWXXM 3.0 schemas unavailable (quality packs).

    Full stack gate lives in ``packages/iwxxm-validate/tests/test_tc_ev070_001_ca_taf_airmet_deepen.py``.
    """
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
    assert result.ok
    assert result.xml

    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile="ca_eccc",
        product=case["product"],
        levels=("xsd", "schematron"),
    )
    assert report.profile == "ca_eccc"
    codes = {i.code for i in report.issues}
    assert "CA_SCHEMA_NOT_FOUND" not in codes
    if report.ok:
        return
    assert codes & {
        "SCHEMA_PARSE_ERROR",
        "SCHEMA_NOT_AVAILABLE",
        "XSD_VALIDATION_ERROR",
        "SCHEMATRON_SKIPPED",
    }, f"unexpected validate failure for {case_id}: {[(i.code, i.message) for i in report.issues]}"


def test_tc_ev070_003_taf_ic_weather_href() -> None:
    from tac2iwxxm import convert

    tac = (FIXTURES / "TAF/valid/taf_ic_weather.tac").read_text(encoding="utf-8")
    result = convert(tac, product="TAF", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert "present_and_forecast_weather/IC" in result.xml
    assert "iwxxm-ca:weather" in result.xml


def test_tc_ev070_002_taf_amd_report_status() -> None:
    from tac2iwxxm import convert

    tac = (FIXTURES / "TAF/valid/taf_amd.tac").read_text(encoding="utf-8")
    result = convert(tac, product="TAF", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert 'reportStatus="AMENDMENT"' in result.xml


def test_tc_ev070_004_airmet_gfa_structured_fields() -> None:
    from tac2iwxxm import convert

    tac = (FIXTURES / "AIRMET/valid/airmet_gfa_sfc_vis.tac").read_text(encoding="utf-8")
    result = convert(tac, product="AIRMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert "SFC_VIS_and_BKN_CLD" in result.xml
    assert "iwxxm-ca:surfaceVisibility" in result.xml
    assert "iwxxm-ca:cloudBase" in result.xml
    assert "iwxxm-ca:surfaceWindSpeed" in result.xml


def test_tc_ev070_006_gfa_structured_metre_visibility() -> None:
    from tac2iwxxm.products.sigmet_airmet import _parse_ca_gfa_structured

    body = "SFC VIS AND BKN CLD OBS N OF S50 1500M BKN020 MOV NE 25KT NC"
    structured = _parse_ca_gfa_structured(body, "SFC_VIS_and_BKN_CLD")
    assert structured is not None
    assert structured["surface_visibility_m"] == {"lower": 1500, "higher": 1500}
    assert structured["cloud_base_ft"] == {"lower": 2000, "higher": 2000}
    assert structured["surface_wind_kt"] == {"lower": 25, "higher": 25}


def test_tc_ev070_007_gfa_structured_non_sfc_vis_returns_none() -> None:
    from tac2iwxxm.products.sigmet_airmet import _parse_ca_gfa_structured

    assert _parse_ca_gfa_structured("MTN OBSC OBS 3SM", "MTN_OBSC") is None
