"""TC-F20-003 - SPECI annex3 golden expansion (S020 / EV-015 T3.5-T3.6 / S3).

Asserts annex3 golden pack covers SPECI exceptional themes and convert →
XSD+Schematron + M-golden (root ``iwxxm:SPECI``).
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

SPECI_CASE_IDS = (
    "speci_basic",
    "speci_cor",
    "speci_nil",
    "speci_cavok",
    "speci_nsc",
    "speci_ncd",
    "speci_nosig",
    "speci_nsw_trend",
    "speci_vv_not_obs",
    "speci_wx_slash",
    "speci_rvr",
    "speci_wind_sector",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f20_003_annex3_speci_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(SPECI_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in SPECI_CASE_IDS:
            assert case["product"] == "SPECI"
            assert case.get("theme") == "S3"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            assert "iwxxm:SPECI" in (FIXTURES / case["golden"]).read_text(encoding="utf-8")


@pytest.mark.parametrize("case_id", SPECI_CASE_IDS)
def test_tc_f20_003_speci_m_parse_xsd_sch(case_id: str) -> None:
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
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", SPECI_CASE_IDS)
def test_tc_f20_003_speci_m_golden(case_id: str) -> None:
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
