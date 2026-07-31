"""TC-EV025-009 — #809 catalog promote to wmoPass (S033 / EV-026 T2.3).

Promote when ``canonicalize_xml`` equality holds under ADR-032 defaults
(TC-EV025-008 green). Catalog tier ``wmoPass`` + FIXTURE_GAPS equality note cleared.
"""

from __future__ import annotations

from pathlib import Path

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
VENDOR_XML = (
    Path(__file__).resolve().parents[3] / "vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-multi-location-VA.xml"
)
CATALOG = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/examplesCatalog.ts"
FIXTURE_GAPS = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"


def test_tc_ev025_009_adr032_equality_holds() -> None:
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_multi_location_va.tac").read_text(encoding="utf-8")
    vendor = VENDOR_XML.read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor)


def test_tc_ev025_009_catalog_is_wmo_pass() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    start = text.index("id: 'sigmet_multi_location_va'")
    end = text.index("},", start)
    block = text[start:end]
    assert "wmoPass: true" in block
    assert "wmoReference: true" not in block
    assert "wmoSeed: 'sigmet-multi-location-VA'" in block
    assert "passer" in block.lower()


def test_tc_ev025_009_fixture_gaps_documents_equality_passer() -> None:
    text = FIXTURE_GAPS.read_text(encoding="utf-8")
    assert "sigmet-multi-location-VA" in text or "multi-location-VA" in text
    assert "TC-EV025-008" in text or "equality" in text.lower()
    assert "#809" in text
    assert "wmoPass" in text
    assert "equality pending" not in text.lower()
