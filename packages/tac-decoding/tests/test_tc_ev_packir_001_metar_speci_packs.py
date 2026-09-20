"""TC-EV-PACKIR-001 — METAR/SPECI builtin packs cover vendor golden peers.

[Corpus: tests] [Corpus: adr/ADR-045]
"""

from __future__ import annotations

from pathlib import Path

from tac_decoding.match import MatchContext, match_tac
from tac_decoding.packs import load_packs

_VENDOR = Path(__file__).resolve().parents[3] / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples"


def _tac(stem: str) -> str:
    return (_VENDOR / f"{stem}.tac").read_text(encoding="utf-8")


def test_builtin_metar_pack_has_rules() -> None:
    packs = {pack.id: pack for pack in load_packs()}
    assert packs["metar"].rules
    assert packs["speci"].rules


def test_metar_a3_1_spans_cover_tokens() -> None:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(
        _tac("metar-A3-1"),
        packs["metar"],
        context=MatchContext("2025-2", "annex3"),
    )
    assert result.spans
    # Residuals may only be the optional report terminator.
    assert all(span.code == "=" for span in result.residuals)
    rule_ids = {span.rule_id for span in result.spans}
    assert "report_type" in rule_ids
    assert "station" in rule_ids
    assert "wind" in rule_ids
    assert "visibility" in rule_ids
    assert "weather" in rule_ids
    assert "cloud" in rule_ids
    assert "temp_dew" in rule_ids
    assert "qnh" in rule_ids
    assert "trend_kind" in rule_ids


def test_speci_a3_2_spans_cover_tokens() -> None:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(
        _tac("speci-A3-2"),
        packs["speci"],
        context=MatchContext("2025-2", "annex3"),
    )
    assert result.spans
    assert all(span.code == "=" for span in result.residuals)
    rule_ids = {span.rule_id for span in result.spans}
    assert "report_type" in rule_ids
    assert "min_visibility" in rule_ids
    assert "nsc" in rule_ids
    assert "trend_kind" in rule_ids
