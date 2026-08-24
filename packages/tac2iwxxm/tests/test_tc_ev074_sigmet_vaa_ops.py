"""TC-EV074 — CA_ECCC SIGMET/VAA validate-first ops (#1043).

[Corpus: product §F23] [Corpus: product §F26] [Corpus: product §F36]
[Corpus: tests §TC-EV074]
"""

from __future__ import annotations

from pathlib import Path

from iwxxm_validate.ca_eccc_layers import (
    STAGE_CA_XSD,
    STAGE_EXCHANGE,
    STAGE_WMO_XSD,
    ca_product_has_national_xsd,
)
from iwxxm_validate.ca_eccc_validate import validate_ca_eccc_layered

from tac2iwxxm.ca_ops_corpus import (
    extract_iwxxm_from_collect,
    load_ops_manifest,
    ops_fixture_root,
)

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"
_COVERAGE = _REPO / "docs" / "domain" / "rules" / "COVERAGE_MATRIX.md"
_HARVEST = _REPO / "scripts" / "iwxxm" / "harvest_ca_eccc_ops.py"
_FIXTURES = ops_fixture_root(_REPO)
_VENDOR_SIGMET = _REPO / "vendor" / "schemas" / "iwxxm" / "3.0.0" / "IWXXM" / "examples" / "sigmet-A6-1a-TS.xml"


def _ca_eccc_catalog_text() -> str:
    text = _CATALOG.read_text(encoding="utf-8")
    start = text.find("id: CA_ECCC")
    assert start >= 0, "CA_ECCC missing from catalog.yaml"
    rest = text.find("\n  - id:", start + 1)
    return text[start : rest if rest > 0 else None]


def test_tc_ev074_006_ca_xsd_skipped_for_unmapped_sigmet() -> None:
    """Unmapped products skip ca_xsd as not-applicable; METAR mapping still fail-closed."""
    assert ca_product_has_national_xsd("METAR") is True
    assert ca_product_has_national_xsd("SIGMET") is False
    assert ca_product_has_national_xsd("VAA") is False

    xml = _VENDOR_SIGMET.read_text(encoding="utf-8")
    report = validate_ca_eccc_layered(xml, product="SIGMET", levels=("xsd",))
    ca_stage = next(s for s in report.stages if s.stage == STAGE_CA_XSD)
    assert ca_stage.ok is True
    assert any(issue.code == "CA_XSD_NOT_APPLICABLE" for issue in ca_stage.issues)
    assert not any(issue.code == "CA_PRODUCT_XSD_NOT_FOUND" for issue in ca_stage.issues)

    exchange = next(s for s in report.stages if s.stage == STAGE_EXCHANGE)
    assert exchange.ok is True
    assert any(issue.code == "CA_EXCHANGE_NOT_APPLICABLE" for issue in exchange.issues)


def test_tc_ev074_006b_mapped_product_missing_xsd_still_errors(monkeypatch) -> None:
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_product_xsd_path", lambda _p: None)
    report = validate_ca_eccc_layered(
        "<?xml version='1.0'?><iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>",
        iwxxm_version="3.0.0",
        product="METAR",
        levels=("xsd",),
    )
    ca_stage = next(s for s in report.stages if s.stage == STAGE_CA_XSD)
    assert any(issue.code == "CA_PRODUCT_XSD_NOT_FOUND" for issue in ca_stage.issues)


def test_tc_ev074_007_catalog_lists_sigmet_vaa() -> None:
    block = _ca_eccc_catalog_text()
    assert "SIGMET" in block and "VAA" in block
    assert "ev074_validate_first: [SIGMET, VAA]" in block


def test_tc_ev074_001_harvest_script_includes_sigmet_vaa() -> None:
    text = _HARVEST.read_text(encoding="utf-8")
    assert "SIGMET" in text
    assert "VAA" in text
    assert "D-EV074-vaa-follow" in text or "deferred" in text.lower()


def test_tc_ev074_002_003_ops_fixture_counts() -> None:
    manifest = load_ops_manifest(_FIXTURES / "ops_manifest.json")
    grouped: dict[str, list] = {}
    for case in manifest["cases"]:
        grouped.setdefault(case["product"], []).append(case)
    sigmet = grouped.get("SIGMET", [])
    assert len(sigmet) >= 2, f"SIGMET ops count {len(sigmet)} < 2"
    for case in sigmet:
        assert (_FIXTURES / case["ops_xml"]).is_file()
        assert case.get("sigmet_kind")
    # VAA: MSC datamart has no VAA tree as of pin (D-EV074-vaa-follow).
    assert grouped.get("VAA", []) == []
    assert manifest.get("vaa_harvest") == "deferred_no_datamart_tree"


def test_tc_ev074_004_harvested_sigmet_wmo_under_ca_profile() -> None:
    """Harvested SIGMET COLLECT members pass WMO 3.0.0 XSD; ca_xsd skipped N/A."""
    manifest = load_ops_manifest(_FIXTURES / "ops_manifest.json")
    sigmet = [c for c in manifest["cases"] if c["product"] == "SIGMET"]
    assert len(sigmet) >= 2
    for case in sigmet:
        raw = (_FIXTURES / case["ops_xml"]).read_text(encoding="utf-8")
        inner = extract_iwxxm_from_collect(raw)
        assert inner is not None, f"COLLECT unwrap failed for {case['id']}"
        report = validate_ca_eccc_layered(inner, product="SIGMET", levels=("xsd",))
        wmo = next(s for s in report.stages if s.stage == STAGE_WMO_XSD)
        assert wmo.ok, [(i.code, i.message) for i in wmo.issues]
        ca_stage = next(s for s in report.stages if s.stage == STAGE_CA_XSD)
        assert ca_stage.ok is True
        assert any(i.code == "CA_XSD_NOT_APPLICABLE" for i in ca_stage.issues)
        assert not any(i.code == "CA_PRODUCT_XSD_NOT_FOUND" for i in report.issues)


def test_tc_ev074_005_vaa_harvest_deferred() -> None:
    """VAA ops harvest is deferred until MSC publishes a VAA tree (D-EV074-vaa-follow)."""
    manifest = load_ops_manifest(_FIXTURES / "ops_manifest.json")
    assert [c for c in manifest["cases"] if c["product"] == "VAA"] == []
    assert manifest.get("vaa_harvest") == "deferred_no_datamart_tree"


def test_tc_ev074_collect_unwraps_sigmet() -> None:
    xml = (
        '<?xml version="1.0"?>'
        '<collect:MeteorologicalBulletin xmlns:collect="http://def.wmo.int/collect/2014">'
        "<collect:meteorologicalInformation>"
        '<iwxxm:SIGMET xmlns:iwxxm="http://icao.int/iwxxm/3.0"/>'
        "</collect:meteorologicalInformation>"
        "</collect:MeteorologicalBulletin>"
    )
    inner = extract_iwxxm_from_collect(xml)
    assert inner is not None
    assert "SIGMET" in inner


def test_tc_ev074_008_coverage_matrix_documents_slice() -> None:
    text = _COVERAGE.read_text(encoding="utf-8")
    assert "SIGMET" in text and "VAA" in text
    assert "ca_xsd" in text or "ca_xsd" in text
    assert "1033" in text
    assert "deferred" in text.lower() or "D-EV074-vaa-follow" in text


def test_tc_ev074_010_code_ca_sigmet_note_only() -> None:
    coverage = _COVERAGE.read_text(encoding="utf-8")
    harvest = _HARVEST.read_text(encoding="utf-8")
    catalog = _CATALOG.read_text(encoding="utf-8")
    joined = coverage + harvest + catalog
    assert "1033" in joined
    assert "code-ca" in joined or "code_ca" in joined
    # Must not ship SIGMET code-ca rule files in this cycle.
    rules = list((_REPO / "packages").rglob("*code*ca*sigmet*"))
    assert rules == [], rules
