"""TC-F6-003 subset: METAR/SPECI iwxxm_us goldens (F6.b / T4.10).

Spec: docs/test-plan.md TC-F6-003, TC-F6-020/021 cutover gate for iwxxm_us;
docs/feature-list.md F6.b; docs/context/general-tac-iwxxm-converter.md US extension pattern;
D-S008-05-batch2 (F6.b in M4).

Oracle: package fixture pack ``fixtures/iwxxm_us_golden/`` (WMO body + iwxxm-us extensions).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "iwxxm_us_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
FIELD_ANNOTATIONS_PATH = Path(__file__).resolve().parent / "fixtures" / "iwxxm_us_field_annotations.json"

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"
CASE_IDS = ("metar_us_ao2_slp", "speci_us_ao2", "metar_us_pk_wnd")


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing iwxxm_us golden manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return _load_manifest()


@pytest.fixture(scope="module")
def field_annotations() -> dict:
    if not FIELD_ANNOTATIONS_PATH.is_file():
        return {"cases": {}}
    return json.loads(FIELD_ANNOTATIONS_PATH.read_text(encoding="utf-8"))


def test_iwxxm_us_golden_manifest_present(golden_manifest: dict) -> None:
    assert golden_manifest.get("schema_version") == 1
    assert golden_manifest.get("profile") == PROFILE
    cases = golden_manifest.get("cases", [])
    assert len(cases) >= 3
    for case in cases:
        assert (FIXTURES / case["tac"]).is_file()
        assert (FIXTURES / case["golden"]).is_file()
        assert case["product"] in {"METAR", "SPECI"}


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_f6_003_m_parse_xsd_sch_iwxxm_us(case_id: str, golden_manifest: dict) -> None:
    """M-parse / M-xsd / M-sch on iwxxm_us golden pack (TC-F6-003 / TC-F6-020)."""
    from iwxxm_validate import validate

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

    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert result.xml, f"M-parse produced empty XML for {case_id}"
    assert result.product == product
    assert result.profile == PROFILE
    assert result.iwxxm_version == IWXXM_VERSION
    assert "iwxxm-us" in result.xml or "www.weather.gov/iwxxm-us" in result.xml

    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking issues for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_f6_003_m_golden_iwxxm_us(case_id: str, golden_manifest: dict) -> None:
    """M-golden: canonicalize(convert XML) == canonicalize(fixture golden)."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected_xml = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    expected = canonicalize_xml(expected_xml)

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok and result.xml
    actual = canonicalize_xml(result.xml)
    assert actual == expected, (
        f"M-golden mismatch for {case_id}:\nexpected: {expected[:240]}...\nactual:   {actual[:240]}..."
    )


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_f6_003_m_field_where_annotated(
    case_id: str,
    golden_manifest: dict,
    field_annotations: dict,
) -> None:
    """M-field: IR US extension fields when annotated."""
    annotations = field_annotations.get("cases", {}).get(case_id)
    if not annotations:
        pytest.skip(f"no M-field annotations for {case_id}")

    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert result.ir is not None, f"M-field requires ConvertResult.ir for {case_id}"

    for key, expected in annotations.items():
        assert key in result.ir, f"missing IR field {key!r} for {case_id}"
        assert result.ir[key] == expected, (
            f"M-field mismatch {case_id}.{key}: expected {expected!r}, got {result.ir[key]!r}"
        )
