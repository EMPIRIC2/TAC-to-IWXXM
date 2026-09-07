"""T2.1 - HTTP lint/validate issue models optional start/end (S011)."""

from __future__ import annotations

from src.schemas.validation import LintIssueModel, ValidateIssueModel


def test_lint_issue_model_accepts_start_end() -> None:
    model = LintIssueModel(
        severity="error",
        code="rule_x",
        message="bad",
        location="wind",
        start=12,
        end=18,
    )
    assert model.start == 12
    assert model.end == 18
    assert model.model_dump()["start"] == 12


def test_validate_issue_model_accepts_start_end() -> None:
    model = ValidateIssueModel(
        layer="xsd",
        level="error",
        message="bad",
        location="line 1",
        start=1,
        end=5,
    )
    assert model.start == 1
    assert model.end == 5
