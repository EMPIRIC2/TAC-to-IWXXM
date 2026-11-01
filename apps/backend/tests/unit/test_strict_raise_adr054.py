"""Unit tests for Strict raise helpers (ADR-054 / EV-severity-strict-ui)."""

from __future__ import annotations

from src.utilities.strict_raise import (
    apply_strict_validate_flags,
    compute_raised_severities,
    promote_convert_failure_severity,
)


def test_strict_off_raises_critical_and_error_only() -> None:
    """Strict OFF raises only critical and error."""
    assert compute_raised_severities(strict=False) == ["critical", "error"]


def test_strict_on_raises_full_ladder() -> None:
    """Strict ON with any step raises the full ladder."""
    assert compute_raised_severities(strict=True) == [
        "critical",
        "error",
        "warning",
        "info",
    ]


def test_preview_forces_validate_off() -> None:
    """Soft-preview never enables post-convert validation."""
    out, level = apply_strict_validate_flags(
        strict=True,
        strict_validate=True,
        preview=True,
        validate_output=True,
        validation_level="comprehensive",
    )
    assert out is False
    assert level == "basic"


def test_strict_on_validate_step_enables_comprehensive() -> None:
    """Strict + validate step drives validate_output and comprehensive level."""
    out, level = apply_strict_validate_flags(
        strict=True,
        strict_validate=True,
        preview=False,
        validate_output=False,
        validation_level="basic",
    )
    assert out is True
    assert level == "comprehensive"


def test_strict_off_leaves_validate_caller_flags() -> None:
    """Strict OFF does not force validation on."""
    out, level = apply_strict_validate_flags(
        strict=False,
        strict_validate=True,
        preview=False,
        validate_output=False,
        validation_level="basic",
    )
    assert out is False
    assert level == "basic"


def test_promote_iwxxm_stays_error() -> None:
    """IWXXM validation findings stay error severity."""
    assert (
        promote_convert_failure_severity(
            "error",
            layer="iwxxm_output",
            code="OUTPUT_VALIDATION_WARNING",
        )
        == "error"
    )


def test_promote_convert_fail_to_critical() -> None:
    """Non-IWXXM convert errors promote to critical."""
    assert promote_convert_failure_severity("error", layer=None, code="PARSE_FAILED") == "critical"
