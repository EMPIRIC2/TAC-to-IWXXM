"""
Strict raise policy helpers for convert/lint/validate (ADR-054).

Server returns all issues; raised_severities describes which severities the
client should treat as raised given Strict and step flags.
"""

from __future__ import annotations

from typing import Final

RAISED_OFF: Final[tuple[str, ...]] = ("critical", "error")
RAISED_ON: Final[tuple[str, ...]] = ("critical", "error", "warning", "info")


def apply_strict_validate_flags(
    *,
    strict: bool,
    strict_validate: bool,
    preview: bool,
    validate_output: bool,
    validation_level: str,
) -> tuple[bool, str]:
    """
    Resolve validate_output / validation_level from Strict master + validate step.

    Soft-preview always forces validation off. When Strict is on and the validate
    step is on, enable comprehensive post-convert validation unless the caller
    already requested a deeper or equal level via validate_output.

    Parameters
    ----------
    strict :
        Master Strict flag.
    strict_validate :
        Validate-step contribution when Strict is on.
    preview :
        Soft-preview mode.
    validate_output :
        Caller validate_output form field.
    validation_level :
        Caller validation_level form field.

    Returns
    -------
    tuple[bool, str]
        Resolved ``(validate_output, validation_level)``.
    """
    if preview:
        return False, "basic"
    level = (validation_level or "basic").strip().lower() or "basic"
    out = bool(validate_output)
    if strict and strict_validate:
        out = True
        if level == "basic":
            level = "comprehensive"
    return out, level


def compute_raised_severities(
    *,
    strict: bool,
    strict_lint: bool = True,
    strict_convert: bool = True,
    strict_validate: bool = True,
) -> list[str]:
    """
    Severities considered raised for this request.

    Strict OFF raises only critical and error. Strict ON raises the full ladder
    when at least one of lint/convert/validate steps is enabled (decode omitted).

    Parameters
    ----------
    strict :
        Master Strict flag.
    strict_lint :
        Include lint-originated findings when Strict is on.
    strict_convert :
        Include convert findings when Strict is on.
    strict_validate :
        Include IWXXM validation findings when Strict is on.

    Returns
    -------
    list[str]
        Ordered severity tokens for the raised set.
    """
    if not strict:
        return list(RAISED_OFF)
    if not (strict_lint or strict_convert or strict_validate):
        return list(RAISED_OFF)
    return list(RAISED_ON)


def promote_convert_failure_severity(severity: str, *, layer: str | None, code: str | None) -> str:
    """
    Map convert-path failures to ``critical``; keep IWXXM validation as ``error``.

    Parameters
    ----------
    severity :
        Current issue severity token.
    layer :
        Optional issue layer.
    code :
        Optional machine-readable code.

    Returns
    -------
    str
        Severity token after promotion rules.
    """
    token = (severity or "error").strip().lower()
    layer_l = (layer or "").strip().lower()
    code_u = (code or "").strip().upper()
    if token in {"warning", "info", "critical"}:
        return token
    if layer_l in {"iwxxm_output", "schema", "schematron", "icao_opmet"} or code_u in {
        "OUTPUT_VALIDATION_WARNING",
        "SCHEMATRON_ASSERT",
        "SCHEMATRON_SKIPPED",
        "XSD_INVALID",
    }:
        return "error"
    if token == "error":
        return "critical"
    return token
