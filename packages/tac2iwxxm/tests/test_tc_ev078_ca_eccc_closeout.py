"""TC-EV078 — CA_ECCC #916 closeout audit (EV-078).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV078]
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm.ca_ops_corpus import load_ops_manifest, ops_fixture_root

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"
_COVERAGE = _REPO / "docs" / "domain" / "rules" / "COVERAGE_MATRIX.md"
_FEATURE = _REPO / "docs" / "feature-list.md"
_CA_ECCC = _REPO / "docs" / "domain" / "profiles" / "semantic" / "CA_ECCC.md"
_FIXTURES = ops_fixture_root(_REPO)


def _ca_eccc_catalog_text() -> str:
    text = _CATALOG.read_text(encoding="utf-8")
    start = text.find("id: CA_ECCC")
    assert start >= 0
    rest = text.find("\n  - id:", start + 1)
    return text[start : rest if rest > 0 else None]


def test_tc_ev078_001_sigmet_exchange_slice_documented() -> None:
    """SIGMET exchange emit closed EV-076; catalog documents ev076_slice."""
    block = _ca_eccc_catalog_text()
    assert "ev076_slice: [SIGMET]" in block
    assert "ev074_validate_first: [VAA]" in block
    assert "harvest_ca_eccc_vaac_tac.py" in block


def test_tc_ev078_002_vaa_vaac_tac_and_airmet_ops_regression() -> None:
    """EV-077 ops corpus: ≥1 VAA TAC, ≥4 AIRMET datamart fixtures."""
    manifest = load_ops_manifest(_FIXTURES / "ops_manifest.json")
    grouped: dict[str, list] = {}
    for case in manifest["cases"]:
        grouped.setdefault(case["product"], []).append(case)
    airmet = [c for c in grouped.get("AIRMET", []) if c.get("tier") == "wmoReference"]
    assert len(airmet) >= 4, f"AIRMET ops count {len(airmet)} < 4"
    vaa = grouped.get("VAA", [])
    assert len(vaa) >= 1
    assert manifest.get("vaa_harvest") == "vaac_tac_waived"
    for case in vaa:
        assert (_FIXTURES / case["ops_tac"]).is_file()


def test_tc_ev078_003_coverage_matrix_residuals_waived() -> None:
    """X6 SIGMET emit met; X7 VAA emit waived; S2 VAA TAC met EV-077."""
    text = _COVERAGE.read_text(encoding="utf-8")
    assert "EV-076" in text and "SIGMET exchange" in text
    assert "D-EV074-vaa-follow" in text
    assert "EV-077" in text


def test_tc_ev078_004_standing_docs_no_stale_vaa_harvest_deferred() -> None:
    """Corpus cites EV-077 VAAC TAC waiver; not bare 'harvest deferred' without context."""
    feature = _FEATURE.read_text(encoding="utf-8")
    ca = _CA_ECCC.read_text(encoding="utf-8")
    assert "EV-077" in feature or "D-EV074-vaa-waiver-tac" in feature
    assert "EV-077" in ca or "D-EV074-vaa-waiver-tac" in ca
    assert "harvest deferred (D-EV074-vaa-follow)" not in ca.split("EV-077")[0]
