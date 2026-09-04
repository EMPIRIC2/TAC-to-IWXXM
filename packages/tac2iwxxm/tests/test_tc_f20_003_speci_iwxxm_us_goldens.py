"""TC-F20-003 - SPECI iwxxm_us golden expansion (S020 / EV-015 T3.5-T3.6 / S3).

Asserts iwxxm_us SPECI S3 themes and convert → XSD+Schematron + M-golden.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "iwxxm_us_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

SPECI_US_CASE_IDS = (
    "speci_us_ao2",
    "speci_us_cor",
    "speci_us_cavok",
    "speci_us_nil",
    "speci_us_nosig",
    "speci_us_auto",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f20_003_iwxxm_us_speci_themes_present() -> None:
    data = _load_manifest()
    assert data.get("profile") == "iwxxm_us"
    ids = {c["id"] for c in data["cases"]}
    assert set(SPECI_US_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in SPECI_US_CASE_IDS:
            assert case["product"] == "SPECI"
            assert case.get("theme") == "S3"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
            assert "iwxxm:SPECI" in golden
            if case["id"] != "speci_us_nil":
                assert "iwxxm-us" in golden or "weather.gov/iwxxm-us" in golden


@pytest.mark.parametrize("case_id", SPECI_US_CASE_IDS)
def test_tc_f20_003_speci_us_m_parse_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SPECI",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert "iwxxm:SPECI" in result.xml
    if case_id != "speci_us_nil":
        assert "iwxxm-us" in result.xml or "weather.gov/iwxxm-us" in result.xml
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", SPECI_US_CASE_IDS)
def test_tc_f20_003_speci_us_m_golden(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SPECI",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)
