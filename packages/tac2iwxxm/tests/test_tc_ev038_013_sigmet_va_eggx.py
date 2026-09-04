"""TC-EV038-013 - promote sigmet-VA-EGGX to ADR-032 equality (#856 / G3).

Strict gate: convert annex3 of vendor-aligned TAC → ``canonicalize_xml`` equals
vendor ``sigmet-VA-EGGX.xml`` under default pin. Catalog ``wmoPass`` is TC follow-on
(T4.7 / FE catalog).
"""

from __future__ import annotations

import json
from pathlib import Path

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
VENDOR_STEM = Path(__file__).resolve().parents[3] / ("vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-VA-EGGX")
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
CASE_ID = "sigmet_va_eggx"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_ev038_013_package_tac_matches_vendor() -> None:
    case = next(c for c in _load_manifest()["cases"] if c["id"] == CASE_ID)
    assert case["product"] == "SIGMET"
    assert case.get("seed") == "sigmet-VA-EGGX"
    package_tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8").strip()
    vendor_tac = VENDOR_STEM.with_suffix(".tac").read_text(encoding="utf-8").strip()
    assert package_tac == vendor_tac


def test_tc_ev038_013_canonicalize_equals_vendor() -> None:
    """ADR-032 strict equality vs vendor (S046 / EV-038 / #856)."""
    from tac2iwxxm.products.sigmet_airmet import parse_sigmet

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == CASE_ID)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    vendor_xml = VENDOR_STEM.with_suffix(".xml").read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    ir = parse_sigmet(tac, product="SIGMET")
    assert ir["phenomenon"] == "VA"
    assert ir.get("iwxxm_root") == "VolcanicAshSIGMET"
    assert ir.get("fir_name") == "SHANWICK OCEANIC FIR"
    assert ir.get("volcano", {}).get("name") == "MT HEKLA"
    locations = ir.get("locations") or []
    assert len(locations) == 1
    assert locations[0].get("forecast") is not None

    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert "VolcanicAshSIGMET" in result.xml
    assert "eruptingVolcano" in result.xml
    assert "forecastPositionAnalysis" in result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor_xml)
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)
