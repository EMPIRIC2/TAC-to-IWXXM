"""TC-F25-001 / TC-F25-002 - WMO TAF annex3 goldens (S026 / EV-020 T4.1-T4.3 / F25 W3).

Asserts vendor ``taf-A5-1`` / ``taf-A5-2`` (AMD/CNL) are in the annex3 pack and
``canonicalize_xml(convert(...))`` equals vendor under defaults (ADR-032 / E20-E1).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

WMO_TAF_CASES = (
    ("taf_a5_1", "taf-A5-1", False),
    ("taf_a5_2", "taf-A5-2", True),
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f25_001_annex3_wmo_taf_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    expected = {case_id for case_id, *_ in WMO_TAF_CASES}
    assert expected <= ids
    by_id = {c["id"]: c for c in data["cases"]}
    for case_id, seed, is_cancel in WMO_TAF_CASES:
        case = by_id[case_id]
        assert case["product"] == "TAF"
        assert case.get("theme") == "W3"
        assert case.get("seed") == seed
        assert (FIXTURES / case["tac"]).is_file()
        assert (FIXTURES / case["golden"]).is_file()
        golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
        assert "iwxxm:TAF" in golden
        if is_cancel:
            assert 'isCancelReport="true"' in golden
            assert "cancelledReportValidPeriod" in golden


@pytest.mark.parametrize(
    ("case_id", "_seed", "is_cancel"),
    WMO_TAF_CASES,
    ids=[c[0] for c in WMO_TAF_CASES],
)
def test_tc_f25_001_taf_wmo_m_golden(case_id: str, _seed: str, is_cancel: bool) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="TAF",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert "iwxxm:TAF" in result.xml
    if is_cancel:
        assert 'isCancelReport="true"' in result.xml
        assert "cancelledReportValidPeriod" in result.xml
        assert "validPeriod" not in result.xml or "cancelledReportValidPeriod" in result.xml
        assert "baseForecast" not in result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


@pytest.mark.parametrize(
    ("case_id", "_seed", "_is_cancel"),
    WMO_TAF_CASES,
    ids=[c[0] for c in WMO_TAF_CASES],
)
def test_tc_f25_002_taf_wmo_m_xsd_sch(case_id: str, _seed: str, _is_cancel: bool) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="TAF",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"
