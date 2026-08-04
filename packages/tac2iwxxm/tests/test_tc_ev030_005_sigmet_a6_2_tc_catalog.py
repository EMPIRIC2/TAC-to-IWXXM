"""TC-EV030-005 — #829 A6-2-TC catalog unlock (S037) → EV-032 `wmoPass` (#835).

Quality path + ADR-032 equality are green. Catalog tier is ``wmoPass`` after
TC-EV032-003 / T1.4 (was ``wmoReference`` at EV-030 T2.4).
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
    """#835 residual closed in EV-032 — keep a peer assert here for unlock gate."""
    from tac2iwxxm import convert

    tac = (FIXTURES / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")
    vendor = VENDOR_XML.read_text(encoding="utf-8")
    result = convert(tac, product="SIGMET", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert result.xml is not None
    assert canonicalize_xml(result.xml) == canonicalize_xml(vendor)


def test_tc_ev030_005_catalog_is_wmo_pass() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    start = text.index("id: 'sigmet_a6_2_tc'")
    end = text.index("},", start)
    block = text[start:end]
    assert "wmoPass: true" in block
    assert "wmoReference: true" not in block
    assert "wmoSeed: 'sigmet-A6-2-TC'" in block
    assert "passer" in block.lower()
    assert FE_BODY.is_file()
    assert FE_BODY.read_text(encoding="utf-8") == (FIXTURES / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")


def test_tc_ev030_005_fixture_gaps_documents_unlock() -> None:
    text = FIXTURE_GAPS.read_text(encoding="utf-8")
    assert "sigmet-A6-2-TC" in text
    assert "wmoPass" in text
    assert "Unlocked" in text or "unlocked" in text
