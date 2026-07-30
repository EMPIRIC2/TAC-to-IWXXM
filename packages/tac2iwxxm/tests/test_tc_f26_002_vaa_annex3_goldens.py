"""TC-F26-002 / TC-F26-003 — VAA annex3 golden (S027 / EV-021 T2.1 / F26 theme V3).

Asserts WMO ``va-advisory-A7-2`` is in the annex3 pack, root
``iwxxm:VolcanicAshAdvisory``, convert → M-xsd/M-sch, and ``canonicalize_xml``
equals vendor golden under default convert settings (ADR-032 / E21-2).

Always write “F26 theme V3” (not F23 VA-SIGMET V3) — D-S027-EV021-s02m1-1.
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

VAA_CASE_IDS = ("vaa_a7_2",)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml


def test_tc_f26_002_annex3_vaa_theme_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(VAA_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in VAA_CASE_IDS:
            assert case["product"] == "VAA"
            assert case.get("theme") == "V3"
            assert case.get("seed") == "va-advisory-A7-2"
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
            assert _has_root(golden, "VolcanicAshAdvisory")


@pytest.mark.parametrize("case_id", VAA_CASE_IDS)
def test_tc_f26_002_vaa_root_element(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VAA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert result.product == "VAA"
    assert _has_root(result.xml, "VolcanicAshAdvisory")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")
    assert "iwxxm:VolcanicAshSIGMET" not in result.xml
    assert not _has_root(result.xml, "SIGMET")


@pytest.mark.parametrize("case_id", VAA_CASE_IDS)
def test_tc_f26_003_vaa_m_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VAA",
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


@pytest.mark.parametrize("case_id", VAA_CASE_IDS)
def test_tc_f26_002_vaa_m_golden(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VAA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


def test_tc_f26_002_vaa_a7_2_content_signals() -> None:
    """Karymsky / TOKYO seed: advisory root + volcano identity under product=vaa."""
    from tac2iwxxm import convert
    from tac2iwxxm.products.vaa_tca import parse_vaa

    tac = (FIXTURES / "vaa_a7_2.tac").read_text(encoding="utf-8")
    ir = parse_vaa(tac, product="VAA")
    assert ir["product"] == "VAA"
    assert ir.get("iwxxm_root") == "VolcanicAshAdvisory"
    assert "KARYMSKY" in str(ir.get("volcano", "")).upper()
    assert str(ir.get("vaac", "")).upper() == "TOKYO"
    assert ir.get("eruption_date") == "2024-09-23T00:00:00Z"
    assert any(f.get("status") == "NO_VOLCANIC_ASH_EXPECTED" for f in ir.get("forecasts") or [])
    result = convert(tac, product="VAA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert _has_root(result.xml, "VolcanicAshAdvisory")
    assert "TOKYO" in result.xml
    assert "KARYMSKY" in result.xml.upper() or "Karymsky" in result.xml
    assert 'status="NO_VOLCANIC_ASH_EXPECTED"' in result.xml
