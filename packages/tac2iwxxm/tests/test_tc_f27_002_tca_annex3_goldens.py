"""TC-F27-002 / TC-F27-003 — TCA annex3 golden stubs (S027 / EV-021 T4.1 / F27 theme T3).

Asserts WMO ``tc-advisory-A2-2`` is in the annex3 pack, root
``iwxxm:TropicalCycloneAdvisory``, and convert → M-xsd/M-sch under default
settings. Canonical golden equality is **T4.2** convert fidelity (ADR-032 / E21-2).

Always write “F27 theme T3” (not F20 TAF T3) — D-S027-EV021-s02m1-1.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

TCA_CASE_IDS = ("tca_a2_2",)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml


def test_tc_f27_002_annex3_tca_theme_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(TCA_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in TCA_CASE_IDS:
            assert case["product"] == "TCA"
            assert case.get("theme") == "T3"
            assert case.get("seed") == "tc-advisory-A2-2"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
            assert _has_root(golden, "TropicalCycloneAdvisory")


@pytest.mark.parametrize("case_id", TCA_CASE_IDS)
def test_tc_f27_002_tca_root_element(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="TCA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert result.product == "TCA"
    assert _has_root(result.xml, "TropicalCycloneAdvisory")
    assert not _has_root(result.xml, "TropicalCycloneSIGMET")
    assert "iwxxm:TropicalCycloneSIGMET" not in result.xml
    assert not _has_root(result.xml, "SIGMET")


@pytest.mark.parametrize("case_id", TCA_CASE_IDS)
def test_tc_f27_003_tca_m_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="TCA",
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


def test_tc_f27_002_tca_a2_2_content_signals() -> None:
    """GLORIA / YUFO seed: advisory root + cyclone identity under product=tca."""
    from tac2iwxxm import convert
    from tac2iwxxm.products.vaa_tca import parse_tca

    tac = (FIXTURES / "tca_a2_2.tac").read_text(encoding="utf-8")
    ir = parse_tca(tac, product="TCA")
    assert ir["product"] == "TCA"
    assert ir.get("iwxxm_root") == "TropicalCycloneAdvisory"
    assert "GLORIA" in str(ir.get("tc_name", "")).upper()
    assert "YUFO" in str(ir.get("tcac", "")).upper()
    result = convert(tac, product="TCA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert _has_root(result.xml, "TropicalCycloneAdvisory")
    assert "GLORIA" in result.xml.upper()
