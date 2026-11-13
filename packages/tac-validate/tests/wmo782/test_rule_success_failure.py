"""Success and failure cases for each WMO-782 cycle registry rule."""

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
def test_rule_failure_emits_code(
    code: str,
    severity: str,
    fail_tac: str,
    pass_tac: str,
) -> None:
    """Failure TAC must emit the target issue code."""
    del pass_tac, severity
    assert by_code(code).code == code
    product = "METAR" if fail_tac.startswith(("METAR", "SPECI")) else "TAF"
    if fail_tac.startswith("SPECI"):
        product = "SPECI"
    report = lint(fail_tac, product=product)
    codes = {i.code for i in report.issues}
    assert code in codes, f"{code} missing from {sorted(codes)}"


@pytest.mark.parametrize(
    ("code", "severity", "fail_tac", "pass_tac"),
    RULE_CASES,
    ids=[c[0] for c in RULE_CASES],
)
def test_rule_success_omits_code(
    code: str,
    severity: str,
    fail_tac: str,
    pass_tac: str,
) -> None:
    """Success TAC must not emit the target issue code."""
    del fail_tac, severity
    product = "METAR"
    if pass_tac.startswith("SPECI"):
        product = "SPECI"
    report = lint(pass_tac, product=product)
    codes = {i.code for i in report.issues}
    assert code not in codes, f"{code} unexpectedly in {sorted(codes)}"
