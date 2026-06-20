"""Unit tests for validation schema helpers."""

from src.schemas.validation import (
    AggregatedValidationResult,
    ValidationLayer,
    ValidationLevel,
    ValidationRequest,
    ValidationResult,
)


def test_add_issue_sets_failed_on_error_level() -> None:
    result = ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX)

    result.add_issue(
        level=ValidationLevel.ERROR,
        message="Invalid token",
        location="line 1",
        code="INVALID_TAC",
        suggestion="Fix token order",
    )

    assert result.passed is False
    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.layer == ValidationLayer.TAC_SYNTAX
    assert issue.level == ValidationLevel.ERROR
    assert issue.location == "line 1"
    assert issue.code == "INVALID_TAC"
    assert issue.suggestion == "Fix token order"


def test_add_issue_keeps_passed_on_info_level() -> None:
    result = ValidationResult(passed=True, layer=ValidationLayer.XML_SCHEMA)

    result.add_issue(
        level=ValidationLevel.INFO,
        message="Optional field missing",
    )

    assert result.passed is True
    assert len(result.issues) == 1
    assert result.issues[0].level == ValidationLevel.INFO


def test_aggregate_from_results_computes_totals() -> None:
    passed_result = ValidationResult(
        passed=True,
        layer=ValidationLayer.AIRPORT_ICAO,
        execution_time_ms=4.0,
    )
    failed_result = ValidationResult(
        passed=False,
        layer=ValidationLayer.TAC_SYNTAX,
        execution_time_ms=6.5,
    )
    failed_result.add_issue(level=ValidationLevel.WARNING, message="Warning only")
    failed_result.add_issue(level=ValidationLevel.ERROR, message="Error")

    aggregated = AggregatedValidationResult.from_results([passed_result, failed_result])

    assert aggregated.passed is False
    assert aggregated.total_issues == 2
    assert aggregated.layers_validated == [
        ValidationLayer.AIRPORT_ICAO,
        ValidationLayer.TAC_SYNTAX,
    ]
    assert aggregated.execution_time_ms == 10.5


def test_validation_request_defaults() -> None:
    request = ValidationRequest(content="METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013")

    assert request.content_type == "tac"
    assert request.layers is None
    assert request.iwxxm_version is None
