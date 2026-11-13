"""Validation assertions: severity, message, and span for each WMO-782 rule."""

from __future__ import annotations

import pytest
from tac_validate import lint
from tac_validate.issue_registry import by_code

from .cases import RULE_CASES


@pytest.mark.parametrize(
    ("code", "severity", "fail_tac", "pass_tac"),
    RULE_CASES,
    ids=[c[0] for c in RULE_CASES],
)
def test_rule_validation_fields(
    code: str,
    severity: str,
    fail_tac: str,
    pass_tac: str,
) -> None:
    """Failure emit matches registry severity and carries a non-empty message."""
    del pass_tac
    spec = by_code(code)
    assert spec.severity == severity
    product = "SPECI" if fail_tac.startswith("SPECI") else "METAR"
    report = lint(fail_tac, product=product)
    matched = [i for i in report.issues if i.code == code]
    assert matched, f"{code} not emitted"
    issue = matched[0]
    assert issue.severity == severity
    assert issue.message.strip()
    assert code in issue.code
    # Prefer character spans when the emitter can locate the token.
    if issue.start is not None and issue.end is not None:
        assert issue.end > issue.start
