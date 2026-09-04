"""MVP stage registry — ADR-042 §10."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from iwxxm_validate import validate as iwxxm_validate
from tac_validate import lint as tac_lint

from tac2iwxxm import convert as tac2iwxxm_convert
from workflows.models import StageIssue, WorkflowDefinition, WorkflowMessage

# Module-level aliases so tests (and F8 parity patches) can monkeypatch here.
tac_lint_fn = tac_lint
tac2iwxxm_convert_fn = tac2iwxxm_convert
iwxxm_validate_fn = iwxxm_validate

_SCHEMATRON_SOFT = frozenset({"SCHEMATRON_SKIPPED"})


@dataclass(slots=True)
class StageOutcome:
    """Result of a single stage."""

    ok: bool
    issues: list[StageIssue]
    xml: str | None = None


def _issue(stage: str, severity: str, code: str, message: str) -> StageIssue:
    return StageIssue(stage=stage, severity=severity, code=code, message=message)


def run_validate_tac(
    message: WorkflowMessage,
    definition: WorkflowDefinition,
    *,
    xml: str | None,
) -> StageOutcome:
    """Run ``tac_validate.lint``."""
    del definition, xml
    report = tac_lint_fn(message.tac, product=message.product.upper())
    issues = [_issue("validate-tac", issue.severity, issue.code, issue.message) for issue in report.issues]
    return StageOutcome(ok=bool(report.ok), issues=issues, xml=None)


def run_convert_iwxxm(
    message: WorkflowMessage,
    definition: WorkflowDefinition,
    *,
    xml: str | None,
) -> StageOutcome:
    """Run ``tac2iwxxm.convert``."""
    del xml
    result = tac2iwxxm_convert_fn(
        message.tac,
        product=message.product.upper(),
        profile=definition.profile_id,
        iwxxm_version=definition.iwxxm_version,
    )
    issues = [_issue("convert-iwxxm", issue.severity, issue.code, issue.message) for issue in result.issues]
    if not result.ok or not result.xml:
        return StageOutcome(ok=False, issues=issues, xml=None)
    return StageOutcome(ok=True, issues=issues, xml=result.xml)


def _iwxxm_stage(
    stage: str,
    levels: tuple[str, ...],
    *,
    xml: str,
    definition: WorkflowDefinition,
) -> StageOutcome:
    report = iwxxm_validate_fn(
        xml,
        iwxxm_version=definition.iwxxm_version,
        profile=definition.profile_id,
        levels=levels,
    )
    issues: list[StageIssue] = []
    blocking: list[StageIssue] = []
    for issue in report.issues:
        if issue.severity == "error" and issue.code in _SCHEMATRON_SOFT:
            # Soft-pass: omit from aggregated issues (F8 parity).
            continue
        item = _issue(stage, issue.severity, issue.code, issue.message)
        issues.append(item)
        if issue.severity == "error":
            blocking.append(item)
    return StageOutcome(ok=not blocking, issues=issues, xml=xml)


def run_validate_xsd(
    message: WorkflowMessage,
    definition: WorkflowDefinition,
    *,
    xml: str | None,
) -> StageOutcome:
    """Run IWXXM XSD validation."""
    del message
    if not xml:
        return StageOutcome(
            ok=False,
            issues=[_issue("validate-xsd", "error", "MISSING_XML", "no XML to validate")],
            xml=None,
        )
    return _iwxxm_stage("validate-xsd", ("xsd",), xml=xml, definition=definition)


def run_validate_schematron(
    message: WorkflowMessage,
    definition: WorkflowDefinition,
    *,
    xml: str | None,
) -> StageOutcome:
    """Run IWXXM Schematron validation (SCHEMATRON_SKIPPED soft-pass)."""
    del message
    if not xml:
        return StageOutcome(
            ok=False,
            issues=[
                _issue(
                    "validate-schematron",
                    "error",
                    "MISSING_XML",
                    "no XML to validate",
                )
            ],
            xml=None,
        )
    return _iwxxm_stage(
        "validate-schematron",
        ("schematron",),
        xml=xml,
        definition=definition,
    )


StageHandler = Callable[..., StageOutcome]

STAGE_REGISTRY: dict[str, StageHandler] = {
    "validate-tac": run_validate_tac,
    "convert-iwxxm": run_convert_iwxxm,
    "validate-xsd": run_validate_xsd,
    "validate-schematron": run_validate_schematron,
}


def run_stage(
    stage_id: str,
    message: WorkflowMessage,
    definition: WorkflowDefinition,
    *,
    xml: str | None,
) -> StageOutcome:
    """
    Dispatch one stage by id.

    Raises
    ------
    KeyError
        Unknown stage id (caller should fail-closed).
    """
    handler = STAGE_REGISTRY[stage_id]
    return handler(message, definition, xml=xml)


__all__ = [
    "STAGE_REGISTRY",
    "StageOutcome",
    "iwxxm_validate_fn",
    "run_convert_iwxxm",
    "run_stage",
    "run_validate_schematron",
    "run_validate_tac",
    "run_validate_xsd",
    "tac2iwxxm_convert_fn",
    "tac_lint_fn",
]
