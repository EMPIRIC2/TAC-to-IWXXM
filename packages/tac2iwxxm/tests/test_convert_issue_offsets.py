"""T2.2 - ConvertIssue optional start/end when locatable (S011 / EV-008)."""

from __future__ import annotations

from tac2iwxxm.codec import json_encoder

from tac2iwxxm import ConvertIssue, convert


def test_convert_issue_accepts_optional_start_end() -> None:
    import msgspec

    issue = ConvertIssue(
        severity="error",
        code="PARSE_ERROR",
        message="missing wind group",
        start=12,
        end=18,
    )
    assert issue.start == 12
    assert issue.end == 18
    decoded = msgspec.json.decode(json_encoder.encode(issue), type=ConvertIssue)
    assert decoded.start == 12
    assert decoded.end == 18


def test_parse_error_spans_tac_content() -> None:
    tac = "  NOT A REPORT  "
    result = convert(tac, product="METAR")
    assert result.ok is False
    issue = result.issues[0]
    assert issue.code == "PARSE_ERROR"
    assert issue.start is not None
    assert issue.end is not None
    leading = len(tac) - len(tac.lstrip())
    stripped = tac.strip()
    assert issue.start == leading
    assert issue.end == leading + len(stripped)


def test_malformed_remarks_include_token_spans() -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AOX SLPZZZ PK WND XXX="
    result = convert(tac, product="METAR", profile="iwxxm_us")
    remark_issues = [i for i in result.issues if i.code == "MALFORMED_REMARKS"]
    assert remark_issues
    spanned = [i for i in remark_issues if i.start is not None and i.end is not None]
    assert spanned, f"expected at least one spanned remark issue, got {remark_issues!r}"
    for issue in spanned:
        assert 0 <= issue.start < issue.end <= len(tac)
        assert tac[issue.start : issue.end]
