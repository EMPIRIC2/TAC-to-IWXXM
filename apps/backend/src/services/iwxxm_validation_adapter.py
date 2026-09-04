"""Thin backend adapter - all IWXXM validation delegates to ``packages/iwxxm-validate``."""

from __future__ import annotations

from collections.abc import Sequence

from iwxxm_validate import validate_iwxxm
from iwxxm_validate.models import Issue, ValidationReport

from ..schemas.validation import (
    SchematronValidationResult,
    ValidationIssue,
    ValidationLayer,
    ValidationResult,
    ValidationSeverity,
    XSDValidationResult,
)

_LAYER_MAP: dict[str, ValidationLayer] = {
    "wellformed": ValidationLayer.XML_WELLFORMED,
    "xsd": ValidationLayer.XML_SCHEMA,
    "schematron": ValidationLayer.SCHEMATRON,
    "gml": ValidationLayer.GML_REFERENCES,
    "codelists": ValidationLayer.WMO_CODELISTS,
    "wmo_xsd": ValidationLayer.XML_SCHEMA,
}


def pkg_issue_to_backend(issue: Issue, *, layer: ValidationLayer | None = None) -> ValidationIssue:
    """Map ``iwxxm_validate.Issue`` onto backend ``ValidationIssue``."""
    severity_raw = str(issue.severity).lower()
    level = ValidationSeverity.ERROR if severity_raw == "error" else ValidationSeverity.WARNING
    if severity_raw == "info":
        level = ValidationSeverity.INFO
    resolved_layer = layer or _LAYER_MAP.get(str(issue.layer), ValidationLayer.XML_SCHEMA)
    return ValidationIssue(
        layer=resolved_layer,
        level=level,
        message=str(issue.message),
        location=issue.location,
        code=str(issue.code),
    )


def _issues_for_level(report: ValidationReport, level: str) -> list[ValidationIssue]:
    backend_layer = _LAYER_MAP.get(level, ValidationLayer.XML_SCHEMA)
    return [
        pkg_issue_to_backend(issue, layer=backend_layer)
        for issue in report.issues
        if issue.layer == level or (level == "xsd" and issue.layer == "wmo_xsd")
    ]


def call_validate_iwxxm(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str = "annex3",
    levels: Sequence[str] | None = None,
    product: str | None = None,
) -> ValidationReport:
    """Invoke ``validate_iwxxm`` - single package entrypoint for backend IWXXM checks."""
    return validate_iwxxm(
        xml_content,
        iwxxm_version=iwxxm_version,
        profile=profile or "annex3",
        levels=levels,
        product=product,
    )


def validate_wellformed(xml_content: str) -> ValidationResult:
    """Layer 3 - XML well-formedness via package lxml check (stable operator messages)."""
    from iwxxm_validate.wellformed import run_wellformed_lxml

    issues = [
        pkg_issue_to_backend(issue, layer=ValidationLayer.XML_WELLFORMED) for issue in run_wellformed_lxml(xml_content)
    ]
    return ValidationResult(
        passed=not issues,
        layer=ValidationLayer.XML_WELLFORMED,
        issues=issues,
    )


def validate_xml_schema(
    xml_content: str,
    version: str,
    *,
    profile: str = "annex3",
) -> XSDValidationResult:
    """Layer 4 - XSD validation via package."""
    report = call_validate_iwxxm(
        xml_content,
        iwxxm_version=version,
        profile=profile,
        levels=("xsd",),
    )
    issues = _issues_for_level(report, "xsd")
    return XSDValidationResult(
        is_valid=not any(i.level == ValidationSeverity.ERROR for i in issues),
        issues=issues,
        schema_version=version,
    )


def validate_schematron(
    xml_content: str,
    version: str,
    *,
    profile: str = "annex3",
) -> SchematronValidationResult:
    """Layer 5 - Schematron validation via package."""
    report = call_validate_iwxxm(
        xml_content,
        iwxxm_version=version,
        profile=profile,
        levels=("schematron",),
    )
    issues = _issues_for_level(report, "schematron")
    return SchematronValidationResult(
        is_valid=not any(i.level == ValidationSeverity.ERROR for i in issues),
        issues=issues,
        schema_version=version,
        rules_evaluated=0 if not issues else 1,
    )


def validate_gml_references(
    xml_content: str,
    version: str,
    *,
    profile: str = "annex3",
) -> tuple[bool, list[ValidationIssue]]:
    """Layer 6 - GML reference validation via package."""
    report = call_validate_iwxxm(
        xml_content,
        iwxxm_version=version,
        profile=profile,
        levels=("gml",),
    )
    issues = _issues_for_level(report, "gml")
    is_valid = not any(i.level == ValidationSeverity.ERROR for i in issues)
    return is_valid, issues


def validate_wmo_codelists(
    xml_content: str,
    version: str,
    *,
    profile: str = "annex3",
) -> tuple[bool, list[ValidationIssue]]:
    """Layer 7 - WMO codelist validation via package."""
    report = call_validate_iwxxm(
        xml_content,
        iwxxm_version=version,
        profile=profile,
        levels=("codelists",),
    )
    issues = _issues_for_level(report, "codelists")
    is_valid = not any(i.level == ValidationSeverity.ERROR for i in issues)
    return is_valid, issues


__all__ = [
    "call_validate_iwxxm",
    "pkg_issue_to_backend",
    "validate_gml_references",
    "validate_schematron",
    "validate_wellformed",
    "validate_wmo_codelists",
    "validate_xml_schema",
]
