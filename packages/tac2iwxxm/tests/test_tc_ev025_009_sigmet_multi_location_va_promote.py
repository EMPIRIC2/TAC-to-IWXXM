"""TC-EV025-009 — #809 catalog promote gate (S032 / EV-025 T5.3).

Promote ``wmoPass`` only when ``canonicalize_xml`` equality holds under ADR-032
defaults. Soft-compare (TC-EV025-008) is green; equality does not hold yet → remain
``wmoReference`` with FIXTURE_GAPS note.
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


def test_tc_ev025_009_adr032_equality_not_yet() -> None:
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_multi_location_va.tac").read_text(encoding="utf-8")
    vendor = VENDOR_XML.read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert canonicalize_xml(result.xml) != canonicalize_xml(vendor)


def test_tc_ev025_009_catalog_remains_wmo_reference() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    # Locate the multi-location entry block.
    start = text.index("id: 'sigmet_multi_location_va'")
    end = text.index("},", start)
    block = text[start:end]
    assert "wmoReference: true" in block
    assert "wmoPass: true" not in block
    assert "wmoSeed: 'sigmet-multi-location-VA'" in block


def test_tc_ev025_009_fixture_gaps_documents_soft_not_equality() -> None:
    text = FIXTURE_GAPS.read_text(encoding="utf-8")
    assert "sigmet-multi-location-VA" in text or "multi-location-VA" in text
    assert "TC-EV025-008" in text or "soft-compare" in text.lower()
    assert "#809" in text
    # Must not claim wmoPass / ADR-032 equality yet.
    assert "wmoPass pending" in text.lower() or "equality pending" in text.lower()
