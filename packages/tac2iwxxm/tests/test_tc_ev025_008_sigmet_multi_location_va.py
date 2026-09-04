"""TC-EV025-008 - #809 sigmet-multi-location-VA ADR-032 equality (S033 / EV-026 T1.1).

Strict gate (E26-TC=1): convert annex3 → ``canonicalize_xml`` equals vendor XML under
default pin. Soft-compare / inequality assert removed. Catalog promote remains TC-EV025-009.
"""

from __future__ import annotations

import json
from pathlib import Path

from lxml import etree

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
VENDOR_STEM = Path(__file__).resolve().parents[3] / (
    "vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-multi-location-VA"
)
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
CASE_ID = "sigmet_multi_location_va"
IW = "{http://icao.int/iwxxm/2025-2}"
GML = "{http://www.opengis.net/gml/3.2}"
METCE = "{http://def.wmo.int/metce/2013}"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml


def _parse(xml: str) -> etree._Element:
    return etree.fromstring(xml.encode("utf-8"))


def test_tc_ev025_008_package_and_vendor_fixtures_present() -> None:
    case = next(c for c in _load_manifest()["cases"] if c["id"] == CASE_ID)
    assert case["product"] == "SIGMET"
    assert case.get("theme") == "V3"
    assert case.get("seed") == "sigmet-multi-location-VA"
    assert case.get("soft_compare") is not True
    assert (FIXTURES / case["tac"]).is_file()
    assert VENDOR_STEM.with_suffix(".tac").is_file()
    assert VENDOR_STEM.with_suffix(".xml").is_file()
    package_tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8").strip()
    vendor_tac = VENDOR_STEM.with_suffix(".tac").read_text(encoding="utf-8").strip()
    assert package_tac == vendor_tac


def test_tc_ev025_008_canonicalize_equals_vendor() -> None:
    """ADR-032 strict equality vs vendor (EV-026)."""
    from tac2iwxxm.products.sigmet_airmet import parse_sigmet

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == CASE_ID)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    vendor_xml = VENDOR_STEM.with_suffix(".xml").read_text(encoding="utf-8")

    ir = parse_sigmet(tac, product="SIGMET")
    assert ir["phenomenon"] == "VA"
    assert ir.get("iwxxm_root") == "VolcanicAshSIGMET"
    locations = ir.get("locations") or []
    assert len(locations) >= 2, f"expected ≥2 AND-locations, got {len(locations)}"
    assert ir.get("volcano", {}).get("name", "").upper().startswith("MT ASHVAL")

    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "SIGMET")
    assert "iwxxm:VolcanicAshAdvisory" not in result.xml

    actual = _parse(result.xml)
    vendor = _parse(vendor_xml)

    actual_collections = actual.findall(f"{IW}analysisCollection")
    vendor_collections = vendor.findall(f"{IW}analysisCollection")
    assert len(actual_collections) >= 2
    assert len(actual_collections) == len(vendor_collections)

    for coll in actual_collections:
        assert coll.find(f".//{IW}SIGMETEvolvingConditionCollection") is not None
        evolving = coll.find(f".//{IW}SIGMETEvolvingConditionCollection")
        assert evolving is not None
        assert evolving.get("timeIndicator") == "OBSERVATION"
        assert coll.find(f"{IW}analysisAndForecastPositionAnalysis/{IW}forecastPositionAnalysis") is not None
        assert coll.find(f".//{IW}SIGMETPositionCollection") is not None

    actual_pos = actual.findall(f".//{GML}posList")
    vendor_pos = vendor.findall(f".//{GML}posList")
    assert len(actual_pos) >= 4
    assert len(actual_pos) == len(vendor_pos)

    actual_text = result.xml
    assert ">250<" in actual_text
    assert ">370<" in actual_text
    assert ">150<" in actual_text
    assert ">300<" in actual_text

    volcano = actual.find(f"{IW}eruptingVolcano/{METCE}Volcano")
    assert volcano is not None
    name = volcano.findtext(f"{METCE}name") or ""
    assert "ASHVAL" in name.upper()

    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor_xml)


def test_tc_ev025_008_soft_m_xsd_smoke() -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == CASE_ID)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking: {[(i.code, i.message) for i in blocking]}"
