"""Unit tests for codes.wmo.int vendor URI drift check (#859 / TC-EV038-008)."""

from __future__ import annotations

from pathlib import Path

from scripts.iwxxm.codelist_uri_drift import (
    REGISTER_SPECS,
    diff_uri_sets,
    load_csv_member_uris,
    load_sch_rdf_member_uris,
    summarize_drift,
)

_REPO = Path(__file__).resolve().parents[2]
_ADOPT = _REPO / "docs" / "domain" / "iwxxm" / "RELEASE_LINE_ADOPTABILITY.md"
_RULES = _REPO / "docs" / "domain" / "rules" / "RULE_SOURCE_URLS.md"


def test_diff_uri_sets_reports_stable_uris() -> None:
    left = {
        "http://codes.wmo.int/common/nil/missing",
        "http://codes.wmo.int/common/nil/unknown",
    }
    right = {
        "http://codes.wmo.int/common/nil/missing",
        "http://codes.wmo.int/common/nil/withheld",
    }
    only_l, only_r = diff_uri_sets(left, right)
    assert only_l == ["http://codes.wmo.int/common/nil/unknown"]
    assert only_r == ["http://codes.wmo.int/common/nil/withheld"]


def test_load_sch_and_csv_common_nil_match(tmp_path: Path) -> None:
    rdf = tmp_path / "nil.rdf"
    rdf.write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://codes.wmo.int/common/nil/missing"/>
  <skos:Concept rdf:about="http://codes.wmo.int/common/nil/unknown"/>
</rdf:RDF>
""",
        encoding="utf-8",
    )
    csv = tmp_path / "nil.csv"
    csv.write_text(
        "id,notation,status\n"
        "http://codes.wmo.int/common/nil/missing,missing,stable\n"
        "http://codes.wmo.int/common/nil/unknown,unknown,stable\n",
        encoding="utf-8",
    )
    sch = load_sch_rdf_member_uris(rdf)
    vend = load_csv_member_uris(csv)
    assert sch == vend
    only_l, only_r = diff_uri_sets(sch, vend)
    assert only_l == [] and only_r == []


def test_summarize_real_aviation_registers_offline() -> None:
    """Pinned SCH RDF ↔ iwxxm-codelists CSV for aviation registers (non-flake)."""
    report, ok = summarize_drift(
        iwxxm_version="2025-2",
        repo_root=_REPO,
        registers=REGISTER_SPECS,
    )
    assert "codes.wmo.int URI drift" in report
    assert "http://codes.wmo.int/" in report
    assert "#889" in report
    assert ok, report


def test_docs_name_cadence_and_disposition() -> None:
    adopt = _ADOPT.read_text(encoding="utf-8")
    assert "#859" in adopt
    assert "make codelist-uri-drift" in adopt
    assert "TC-EV038-008" in adopt
    assert "D-S046-859" in adopt
    rules = _RULES.read_text(encoding="utf-8")
    assert "codelist-uri-drift" in rules
    assert "#859" in rules
