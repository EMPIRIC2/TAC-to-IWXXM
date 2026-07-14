"""T2.2 — Parse-gate rules emit character offsets when locatable (S011 / EV-008)."""

from __future__ import annotations

from tac_validate import lint


def test_empty_tac_issue_spans_full_input() -> None:
    tac = "   "
    report = lint(tac, product="METAR")
    empty = next(i for i in report.issues if i.code == "EMPTY_TAC")
    assert empty.start == 0
    assert empty.end == len(tac)


def test_missing_keyword_spans_body() -> None:
    tac = "  KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034="
    report = lint(tac, product="METAR")
    missing = next(i for i in report.issues if i.code == "MISSING_PRODUCT_KEYWORD")
    stripped = tac.strip()
    leading = len(tac) - len(tac.lstrip())
    assert missing.start == leading
    assert missing.end == leading + len(stripped)
    assert tac[missing.start : missing.end] == stripped


def test_missing_terminator_highlights_report_end() -> None:
    tac = "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034"
    report = lint(tac, product="METAR")
    term = next(i for i in report.issues if i.code == "MISSING_TERMINATOR")
    assert term.start is not None and term.end is not None
    assert 0 <= term.start < term.end <= len(tac)
    leading = len(tac) - len(tac.lstrip())
    core = tac.strip().rstrip()
    assert term.start == leading + len(core) - 1
    assert term.end == leading + len(core)
    assert tac[term.start : term.end] == core[-1]


def test_taf_missing_terminator_has_offsets() -> None:
    tac = "TAF KJFK 101730Z 1018/1124 24008KT"
    report = lint(tac, product="TAF")
    term = next(i for i in report.issues if i.code == "MISSING_TERMINATOR")
    assert term.start is not None
    assert term.end is not None
    assert tac[term.start : term.end]


def test_speci_missing_keyword_has_offsets() -> None:
    tac = "KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034="
    report = lint(tac, product="SPECI")
    missing = next(i for i in report.issues if i.code == "MISSING_PRODUCT_KEYWORD")
    assert missing.start == 0
    assert missing.end == len(tac)


def test_unknown_product_has_no_tac_span() -> None:
    report = lint("METAR KJFK 101851Z NIL=", product="NOTAPRODUCT")
    unknown = next(i for i in report.issues if i.code == "UNKNOWN_PRODUCT")
    assert unknown.start is None
    assert unknown.end is None
