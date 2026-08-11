"""TC-EV055-002: match_status uses C14N equality (generator path).

Spec: docs/test-plan.md TC-EV055-002; AC2; ADR-035; D-S064-c14n=1;
D-S064-c14n-volatile=1.
"""

from __future__ import annotations

from iwxxm_validate.c14n import c14n_equal


def test_tc_ev055_002_c14n_equality_for_formatting_only_peers() -> None:
    """Formatting-only official/converted peers are equal under C14N (match_status semantics)."""
    official = """<?xml version="1.0"?>
<root xmlns="urn:x">
  <v>1</v>
</root>
"""
    converted = '<?xml version="1.0"?><root xmlns="urn:x"><v>1</v></root>'
    assert c14n_equal(official, converted) is True


def test_tc_ev055_002_c14n_equality_despite_volatile_ids() -> None:
    """gml:id churn alone must not yield match_status unequal (ADR-035 amend)."""
    official = (
        '<root xmlns="urn:x" xmlns:gml="http://www.opengis.net/gml/3.2">'
        '<child gml:id="uuid.11111111-1111-1111-1111-111111111111"><v>ok</v></child>'
        "</root>"
    )
    converted = (
        '<root xmlns="urn:x" xmlns:gml="http://www.opengis.net/gml/3.2">'
        '<child gml:id="uuid.22222222-2222-2222-2222-222222222222"><v>ok</v></child>'
        "</root>"
    )
    assert c14n_equal(official, converted) is True


def test_tc_ev055_002_generator_imports_c14n_not_adr032_for_match() -> None:
    """generate_quality_metrics must use c14n_xml / c14n_equal for match_status."""
    from pathlib import Path

    src = Path(__file__).resolve().parents[3] / "scripts" / "ci" / "generate_quality_metrics.py"
    text = src.read_text(encoding="utf-8")
    assert "c14n_equal" in text or "c14n_xml" in text
    # Match branch must not still depend on ADR-032 canonicalize for equality
    assert "canonicalize_xml(converted_xml) == canonicalize_xml(official_xml)" not in text
