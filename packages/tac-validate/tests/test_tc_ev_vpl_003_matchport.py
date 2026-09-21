"""TC-EV-VPL-003 — MatchPort strict annex3 METAR when a port is supplied."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.detectors import run_theme_pack
from tac_validate.match_port import DecodeMatch, match_port_spans
from tac_validate.theme_checks import lint_profile

_TAC = "METAR 121251Z"


def test_omitted_port_keeps_tac_scan() -> None:
    report = lint(_TAC, product="METAR")
    assert "MISSING_DECODE_MATCH" not in {issue.code for issue in report.issues}


def test_empty_port_emits_missing_decode_match_for_each_theme() -> None:
    report = lint(_TAC, product="METAR", match_port=())
    codes = [issue.code for issue in report.issues]
    assert codes.count("MISSING_DECODE_MATCH") == 6


def test_other_product_ignores_empty_port() -> None:
    report = lint(_TAC, product="SPECI", match_port=())
    assert "MISSING_DECODE_MATCH" not in {issue.code for issue in report.issues}


def test_non_annex3_profile_keeps_scan() -> None:
    report = lint(_TAC, product="METAR", profile="iwxxm_us", match_port=())
    assert "MISSING_DECODE_MATCH" not in {issue.code for issue in report.issues}


def test_present_match_replaces_theme_span() -> None:
    token = match_port_spans.set((DecodeMatch(2, 5),))
    try:
        issues = run_theme_pack("metar-speci-r1-identity-order", _TAC, "METAR")
    finally:
        match_port_spans.reset(token)
    assert issues
    assert all(issue.start == 2 and issue.end == 5 for issue in issues)


def test_match_port_protocol_object() -> None:
    class _Port:
        def matches(self) -> tuple[DecodeMatch, ...]:
            return (DecodeMatch(0, 1),)

    report = lint(_TAC, product="METAR", match_port=_Port())
    assert "MISSING_DECODE_MATCH" not in {issue.code for issue in report.issues}
    matched = [issue for issue in report.issues if issue.start == 0 and issue.end == 1]
    assert matched


def test_profile_context_blocks_strict_mode() -> None:
    token = lint_profile.set("iwxxm_us")
    port = match_port_spans.set(())
    try:
        issues = run_theme_pack("metar-speci-r1-identity-order", _TAC, "METAR")
    finally:
        match_port_spans.reset(port)
        lint_profile.reset(token)
    assert "MISSING_DECODE_MATCH" not in {issue.code for issue in issues}
