"""TC-F20-002 - TAF annex3 golden expansion (S020 / EV-015 T2.1 / T4).

Asserts annex3 golden pack covers TAF exceptional themes (NIL/CNL/AMD/COR/CAVOK)
and convert → XSD+Schematron + M-golden for those cases.
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

TAF_CASE_IDS = (
    "taf_basic",
    "taf_nil",
    "taf_cnl",
    "taf_amd",
    "taf_cor",
    "taf_cavok",
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f20_002_annex3_taf_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(TAF_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in TAF_CASE_IDS:
            assert case["product"] == "TAF"
            assert case.get("theme") == "T4"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()


@pytest.mark.parametrize("case_id", TAF_CASE_IDS)
def test_tc_f20_002_taf_m_parse_xsd_sch(case_id: str) -> None:
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
    assert "iwxxm:TAF" in result.xml
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", TAF_CASE_IDS)
def test_tc_f20_002_taf_m_golden(case_id: str) -> None:
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
    assert result.ok is True
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)
