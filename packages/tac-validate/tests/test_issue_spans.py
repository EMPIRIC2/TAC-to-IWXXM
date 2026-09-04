"""T2.1 - Issue models accept optional character spans (S011 / EV-008)."""

from __future__ import annotations

import msgspec
from tac_validate.models import Issue


def test_issue_accepts_optional_start_end() -> None:
    issue = Issue(
        severity="error",
        code="rule_x",
        message="bad wind",
        location="wind",
        start=12,
        end=18,
    )
    assert issue.start == 12
    assert issue.end == 18
    encoded = msgspec.json.encode(issue)
    decoded = msgspec.json.decode(encoded, type=Issue)
    assert decoded.start == 12
    assert decoded.end == 18


def test_issue_start_end_default_none() -> None:
    issue = Issue(severity="warning", code="w", message="m")
    assert issue.start is None
    assert issue.end is None
