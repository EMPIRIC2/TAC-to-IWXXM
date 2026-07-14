"""T2.1 — iwxxm-validate Issue optional start/end (S011 / EV-008)."""

from __future__ import annotations

import msgspec

from iwxxm_validate.models import Issue


def test_issue_accepts_optional_start_end() -> None:
    issue = Issue(
        severity="error",
        code="sch",
        message="fail",
        location="line 1",
        start=0,
        end=4,
    )
    assert issue.start == 0
    assert issue.end == 4
    decoded = msgspec.json.decode(msgspec.json.encode(issue), type=Issue)
    assert decoded.start == 0
    assert decoded.end == 4
