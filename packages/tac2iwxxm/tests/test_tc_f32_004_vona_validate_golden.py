"""TC-F32-004 — VONA convert → XSD+SCH + ADR-032 golden (S040 / EV-032 T2.6).

Accept path: annex3 convert of ``vona-A7-1`` is M-xsd/M-sch clean and
``canonicalize_xml`` equals the official peer / package golden (soft→strict).
Negatives remain under ``tac-validate`` TC-F32-001 (T2.2/T2.3).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
VENDOR_XML = Path(__file__).resolve().parents[3] / "vendor/schemas/iwxxm/2025-2/IWXXM/examples/vona-A7-1.xml"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
VONA_CASE_IDS = ("vona_a7_1",)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml or f"<iwxxm:{local}\n" in xml or f"<iwxxm:{local}>" in xml


@pytest.mark.parametrize("case_id", VONA_CASE_IDS)
def test_tc_f32_004_vona_m_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VONA",
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


@pytest.mark.parametrize("case_id", VONA_CASE_IDS)
def test_tc_f32_004_vona_m_golden_adr032(case_id: str) -> None:
    """ADR-032: convert equals package golden and vendor peer under canonicalize_xml."""
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    assert case.get("wmoReference") is not True
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    vendor = VENDOR_XML.read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert _has_root(result.xml, "VolcanoObservatoryNoticeForAviation")
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)
    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor)
    assert canonicalize_xml(golden) == canonicalize_xml(vendor)


def test_tc_f32_004_manifest_strict_peer() -> None:
    case = next(c for c in _load_manifest()["cases"] if c["id"] == "vona_a7_1")
    assert case["product"] == "VONA"
    assert case.get("seed") == "vona-A7-1"
    assert case.get("wmoReference") is not True
    assert case.get("soft_compare") is not True
