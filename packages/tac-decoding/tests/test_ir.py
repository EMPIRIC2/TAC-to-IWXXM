"""Pack IR projection from a match.

[Corpus: adr/ADR-045] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.ir import project_ir
from tac_decoding.match import MatchResult, MatchSpan


def test_project_ir_copies_spans_and_context() -> None:
    match = MatchResult(
        spans=(MatchSpan(0, 5, "METAR", "Meteorological aerodrome report", "type"),),
        residuals=(MatchSpan(6, 10, "YUDO", "", ""),),
        steps=1,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    ir = project_ir(match, product="metar", pack_id="metar")
    assert ir["ir_version"] == 1
    assert ir["product"] == "METAR"
    assert ir["pack_id"] == "metar"
    assert ir["iwxxm_version"] == "2025-2"
    assert ir["profile"] == "annex3"
    assert isinstance(ir["spans"], list)
    assert ir["spans"][0] == {
        "rule_id": "type",
        "code": "METAR",
        "start": 0,
        "end": 5,
        "explanation": "Meteorological aerodrome report",
    }
    assert ir["residuals"][0]["code"] == "YUDO"


def test_project_ir_empty_match() -> None:
    match = MatchResult((), (), 0, None, None)
    ir = project_ir(match, product="SIGMET", pack_id="va_sigmet")
    assert ir["product"] == "SIGMET"
    assert ir["pack_id"] == "va_sigmet"
    assert ir["spans"] == []
    assert ir["residuals"] == []
    assert ir["iwxxm_version"] is None
