"""TC-F6-020 / TC-F6-021: METAR/SPECI annex3 goldens (F6.a / T4.1).

Spec: docs/test-plan.md TC-F6-020, TC-F6-021;
docs/context/general-tac-iwxxm-converter.md accuracy metrics (M-parse / M-xsd / M-sch /
M-golden / M-field); docs/feature-list.md F6.a.

Oracle: package fixture pack ``fixtures/annex3_golden/`` (WMO-shaped IWXXM documents).
Gifts ``test-data/golden/`` remains for TC-F6-022 archive / M-parity (GPL-3; not copied).
"""

from __future__ import annotations

import json
from pathlib import Path

import msgspec
import pytest
from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
FIELD_ANNOTATIONS_PATH = Path(__file__).resolve().parent / "fixtures" / "metar_speci_field_annotations.json"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing annex3 golden manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return _load_manifest()


@pytest.fixture(scope="module")
def field_annotations() -> dict:
    if not FIELD_ANNOTATIONS_PATH.is_file():
        return {"cases": {}}
    return json.loads(FIELD_ANNOTATIONS_PATH.read_text(encoding="utf-8"))


def test_convert_exports_public_entrypoints() -> None:
    import tac2iwxxm

    assert callable(getattr(tac2iwxxm, "convert", None))
    assert getattr(tac2iwxxm, "ConvertResult", None) is not None
    assert getattr(tac2iwxxm, "ConvertError", None) is not None


def test_convert_result_is_msgspec_struct() -> None:
    from tac2iwxxm import ConvertResult

    assert issubclass(ConvertResult, msgspec.Struct)


def test_annex3_golden_manifest_present(golden_manifest: dict) -> None:
    assert golden_manifest.get("schema_version") == 1
    cases = golden_manifest.get("cases", [])
    assert len(cases) >= 7
    ids = {c["id"] for c in cases}
    assert {"metar_basic", "speci_basic", "metar_nil", "metar_cor", "metar_auto", "metar_cavok", "speci_cor"} <= ids
    for case in cases:
        assert (FIXTURES / case["tac"]).is_file()
        soft = case.get("soft_compare") is True
        if soft:
            # TC-EV025-008 / #809 — soft-compare cases omit package golden until ADR-032
            assert "golden" not in case or case.get("golden") in (None, "")
        else:
            assert (FIXTURES / case["golden"]).is_file()
        assert case["product"] in {"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA"}


ANNEX3_CASE_IDS = (
    "metar_basic",
    "speci_basic",
    "metar_nil",
    "metar_cor",
    "metar_auto",
    "metar_cavok",
    "speci_cor",
)


@pytest.mark.parametrize("case_id", ANNEX3_CASE_IDS)
def test_tc_f6_020_m_parse_xsd_sch_annex3(case_id: str, golden_manifest: dict) -> None:
    """M-parse / M-xsd / M-sch on golden pack (TC-F6-020 / TC-F15-002)."""
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

    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking issues for {case_id}: {[(i.code, i.message) for i in blocking]}"


@pytest.mark.parametrize("case_id", ANNEX3_CASE_IDS)
def test_tc_f6_021_m_golden_annex3(case_id: str, golden_manifest: dict) -> None:
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


@pytest.mark.parametrize("case_id", ANNEX3_CASE_IDS)
def test_tc_f6_021_m_field_where_annotated(case_id: str, golden_manifest: dict, field_annotations: dict) -> None:
    """M-field: IR field equality only when the fixture pack annotates expected fields."""
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
