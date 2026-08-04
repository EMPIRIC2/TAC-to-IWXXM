"""TC-EV030-005 — #829 A6-2-TC catalog unlock as wmoReference (S037 / EV-030 T2.4).

Quality path (lint → convert → validate) is green for annex3 ``sigmet_a6_2_tc``.
ADR-032 ``canonicalize_xml`` equality vs vendor is green as of EV-032 / #835
(``test_tc_ev032_002_a6_2_tc_adr032_equality``). Catalog promote to ``wmoPass`` is
TC-EV032-003 / T1.4 — this module still expects ``wmoReference`` until then.
"""

from __future__ import annotations

from pathlib import Path

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
VENDOR_XML = Path(__file__).resolve().parents[3] / "vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-A6-2-TC.xml"
CATALOG = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/examplesCatalog.ts"
FIXTURE_GAPS = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md"
FE_BODY = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/bodies/sigmet_a6_2_tc.tac"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"


def test_tc_ev030_005_quality_path_green() -> None:
    """Lint → convert → XSD+SCH still green for A6-2-TC (unlock gate)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="SIGMET")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert "TropicalCycloneSIGMET" in result.xml

    validation = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_tc_ev030_005_adr032_equality_holds() -> None:
    """#835 residual closed in EV-032 — keep a peer assert here for M2 unlock gate."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")
    vendor = VENDOR_XML.read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert result.xml is not None
    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor)


def test_tc_ev030_005_catalog_is_wmo_reference() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    start = text.index("id: 'sigmet_a6_2_tc'")
    end = text.index("},", start)
    block = text[start:end]
    assert "wmoReference: true" in block
    assert "wmoPass: true" not in block
    assert "wmoSeed: 'sigmet-A6-2-TC'" in block
    assert "reference" in block.lower()
    assert FE_BODY.is_file()
    assert FE_BODY.read_text(encoding="utf-8") == (FIXTURES / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")


def test_tc_ev030_005_fixture_gaps_documents_unlock() -> None:
    text = FIXTURE_GAPS.read_text(encoding="utf-8")
    assert "sigmet-A6-2-TC" in text
    assert "wmoReference" in text
    assert "deferred (#738)" not in text.lower() or "Unlocked" in text
    assert "Unlocked" in text or "unlocked" in text
