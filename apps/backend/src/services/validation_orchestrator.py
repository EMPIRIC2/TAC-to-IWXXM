"""
IWXXM Validation Orchestrator

Coordinates all 7 validation layers with proper sequencing, parallelization,
and error handling. Provides comprehensive validation results for IWXXM documents.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import lxml.etree as etree

from ..schemas.validation import ValidationIssue, ValidationLayer, ValidationResult, ValidationSeverity
from ..services.validation import ValidationService
from ..utilities.codelist_parser import get_codelist_parser
from ..utilities.gml_validator import get_gml_validator
from ..utilities.schema_registry import get_schema_registry
from ..utilities.schematron_validator import get_schematron_validator
from ..utilities.xsd_validator import XSDValidationResult, get_xsd_validator

logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveValidationResult:
    """Result of comprehensive multi-layer validation."""

    is_valid: bool
    layers_run: List[ValidationLayer]
    layers_passed: List[ValidationLayer]
    layers_failed: List[ValidationLayer]
    all_issues: List[ValidationIssue]
    issues_by_layer: Dict[ValidationLayer, List[ValidationIssue]] = field(default_factory=dict)
    version: str = ""
    stopped_at_layer: Optional[ValidationLayer] = None

    @property
    def passed(self) -> bool:
        """Alias for is_valid (API compatibility)."""
        return self.is_valid


class ValidationOrchestrator:
    """
    Orchestrates comprehensive IWXXM validation across all 7 layers.

    Validation Sequence:
    1. Layer 1 (AIRPORT_ICAO) - Blocking
    2. Layer 2 (TAC_SYNTAX) - Blocking
    3. Layer 3 (XML_WELLFORMED) - Blocking
    4. Layer 4 (XML_SCHEMA) - Blocking
    5-7. Layers 5-7 (SCHEMATRON, GML_REFERENCES, WMO_CODELISTS) - Parallel, non-blocking

    If any blocking layer fails, validation stops and returns immediately.
    Non-blocking layers run in parallel and all results are collected.
    """

    def __init__(self):
        """Initialize validation orchestrator with all validators."""
        self.validation_service = ValidationService()
        self.xsd_validator = get_xsd_validator()
        self.schematron_validator = get_schematron_validator()
        self.gml_validator = get_gml_validator()
        self.schema_registry = get_schema_registry()

    def _is_validation_passed(self, result) -> bool:
        """Check if validation passed, handling both ValidationResult and specialized types."""
        if hasattr(result, "passed"):
            return result.passed
        elif hasattr(result, "is_valid"):
            return result.is_valid
        else:
            logger.warning(f"Unknown result type {type(result)}: cannot determine pass/fail")
            return False

    def _validate_wellformed(self, xml_content: str) -> ValidationResult:
        """
        Validate XML is well-formed (Layer 3).

        Args:
            xml_content: XML string to validate

        Returns:
            ValidationResult with wellformedness check
        """
        issues = []

        try:
            etree.fromstring(xml_content.encode("utf-8"))

            logger.debug("XML wellformedness check passed")
            return ValidationResult(passed=True, layer=ValidationLayer.XML_WELLFORMED, issues=[])

        except etree.XMLSyntaxError as e:
            issue = ValidationIssue(
                layer=ValidationLayer.XML_WELLFORMED,
                level=ValidationSeverity.ERROR,
                message=f"XML is not well-formed: {str(e)}",
                location=f"line {getattr(e, 'lineno', '?')}, column {getattr(e, 'offset', '?')}",
            )
            issues.append(issue)

            logger.warning(f"XML wellformedness check failed: {str(e)}")
            return ValidationResult(passed=False, layer=ValidationLayer.XML_WELLFORMED, issues=[issue])

    def validate_wellformed(self, xml_content: str) -> ValidationResult:
        """Public XML well-formedness validation helper."""
        return self._validate_wellformed(xml_content)

    @staticmethod
    def _pkg_issue_to_backend(
        issue: object,
        *,
        layer: ValidationLayer,
    ) -> ValidationIssue:
        """Map ``iwxxm_validate.Issue`` fields onto backend ``ValidationIssue``."""
        severity_raw = str(getattr(issue, "severity", "error")).lower()
        level = ValidationSeverity.ERROR if severity_raw == "error" else ValidationSeverity.WARNING
        return ValidationIssue(
            layer=layer,
            level=level,
            message=str(getattr(issue, "message", "")),
            location=getattr(issue, "location", None),
            code=str(getattr(issue, "code", "NATIVE_ISSUE")),
        )

    def validate_xml_schema(self, xml_content: str, version: str) -> XSDValidationResult:
        """Public XML schema validation helper (native-first when Rust is built)."""
        try:
            from iwxxm_validate import rust_available, validate_iwxxm

            if rust_available():
                report = validate_iwxxm(
                    xml_content,
                    iwxxm_version=version,
                    profile="annex3",
                    levels=("xsd",),
                )
                issues = [self._pkg_issue_to_backend(i, layer=ValidationLayer.XML_SCHEMA) for i in report.issues]
                return XSDValidationResult(
                    is_valid=report.ok,
                    issues=issues,
                    schema_version=version,
                )
        except Exception as exc:  # noqa: BLE001 — fall back to legacy lxml
            logger.warning("Native XSD path unavailable; using lxml validator: %s", exc)

        return self.xsd_validator.validate(xml_content, version)

    def _validate_schematron(self, xml_content: str, version: str):
        """Schematron layer (native-first when Rust is built)."""
        try:
            from iwxxm_validate import rust_available, validate_iwxxm

            from ..utilities.schematron_validator import SchematronValidationResult

            if rust_available():
                report = validate_iwxxm(
                    xml_content,
                    iwxxm_version=version,
                    profile="annex3",
                    levels=("schematron",),
                )
                issues = [self._pkg_issue_to_backend(i, layer=ValidationLayer.SCHEMATRON) for i in report.issues]
                return SchematronValidationResult(
                    is_valid=report.ok,
                    issues=issues,
                    schema_version=version,
                    rules_evaluated=0 if not report.issues else 1,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Native Schematron path unavailable; using lxml validator: %s", exc)

        return self.schematron_validator.validate(xml_content, version)

    def validate(
        self,
        xml_content: str,
        *,
        iwxxm_version: str,
        layers: Optional[List[ValidationLayer]] = None,
    ) -> ComprehensiveValidationResult:
        """Validate IWXXM XML for selected layers (typically 3-7)."""
        return self.validate_complete(
            tac_text="",
            xml_content=xml_content,
            version=iwxxm_version,
            layers=layers,
            stop_on_error=False,
        )

    def validate_complete(
        self,
        tac_text: str,
        xml_content: str,
        version: str,
        layers: Optional[List[ValidationLayer]] = None,
        stop_on_error: bool = True,
    ) -> ComprehensiveValidationResult:
        """
        Perform comprehensive validation across all selected layers.

        Args:
            tac_text: Original TAC (text) input
            xml_content: Converted XML content
            version: IWXXM version (e.g., '2025-2')
            layers: Specific layers to run, or None for all
            stop_on_error: If True, stop at first blocking layer failure

        Returns:
            ComprehensiveValidationResult with all validation outcomes
        """
        # Default to all layers if not specified
        if layers is None:
            layers = list(ValidationLayer)

        layers_run = []
        layers_passed = []
        layers_failed = []
        all_issues = []
        issues_by_layer = {}
        stopped_at_layer = None

        # Layer 1: AIRPORT_ICAO (Blocking)
        if ValidationLayer.AIRPORT_ICAO in layers:
            logger.info("Running Layer 1: AIRPORT_ICAO validation")
            layers_run.append(ValidationLayer.AIRPORT_ICAO)

            try:
                result = self.validation_service.validate_airport_icao(tac_text)

                if result.issues:
                    all_issues.extend(result.issues)
                    issues_by_layer[ValidationLayer.AIRPORT_ICAO] = result.issues

                if self._is_validation_passed(result):
                    layers_passed.append(ValidationLayer.AIRPORT_ICAO)
                else:
                    layers_failed.append(ValidationLayer.AIRPORT_ICAO)

                    if stop_on_error:
                        logger.warning("Layer 1 failed, stopping validation")
                        stopped_at_layer = ValidationLayer.AIRPORT_ICAO
                        return ComprehensiveValidationResult(
                            is_valid=False,
                            layers_run=layers_run,
                            layers_passed=layers_passed,
                            layers_failed=layers_failed,
                            all_issues=all_issues,
                            issues_by_layer=issues_by_layer,
                            version=version,
                            stopped_at_layer=stopped_at_layer,
                        )
            except Exception as e:
                logger.error(f"Layer 1 validation error: {e}")
                layers_failed.append(ValidationLayer.AIRPORT_ICAO)

        # Layer 2: TAC_SYNTAX (Blocking)
        if ValidationLayer.TAC_SYNTAX in layers:
            logger.info("Running Layer 2: TAC_SYNTAX validation")
            layers_run.append(ValidationLayer.TAC_SYNTAX)

            try:
                result = self.validation_service.validate_tac_syntax(tac_text)

                if result.issues:
                    all_issues.extend(result.issues)
                    issues_by_layer[ValidationLayer.TAC_SYNTAX] = result.issues

                if self._is_validation_passed(result):
                    layers_passed.append(ValidationLayer.TAC_SYNTAX)
                else:
                    layers_failed.append(ValidationLayer.TAC_SYNTAX)

                    if stop_on_error:
                        logger.warning("Layer 2 failed, stopping validation")
                        stopped_at_layer = ValidationLayer.TAC_SYNTAX
                        return ComprehensiveValidationResult(
                            is_valid=False,
                            layers_run=layers_run,
                            layers_passed=layers_passed,
                            layers_failed=layers_failed,
                            all_issues=all_issues,
                            issues_by_layer=issues_by_layer,
                            version=version,
                            stopped_at_layer=stopped_at_layer,
                        )
            except Exception as e:
                logger.error(f"Layer 2 validation error: {e}")
                layers_failed.append(ValidationLayer.TAC_SYNTAX)

        # Layer 3: XML_WELLFORMED (Blocking)
        if ValidationLayer.XML_WELLFORMED in layers:
            logger.info("Running Layer 3: XML_WELLFORMED validation")
            layers_run.append(ValidationLayer.XML_WELLFORMED)

            try:
                result = self.validate_wellformed(xml_content)

                if result.issues:
                    all_issues.extend(result.issues)
                    issues_by_layer[ValidationLayer.XML_WELLFORMED] = result.issues

                if self._is_validation_passed(result):
                    layers_passed.append(ValidationLayer.XML_WELLFORMED)
                else:
                    layers_failed.append(ValidationLayer.XML_WELLFORMED)

                    if stop_on_error:
                        logger.warning("Layer 3 failed, stopping validation")
                        stopped_at_layer = ValidationLayer.XML_WELLFORMED
                        return ComprehensiveValidationResult(
                            is_valid=False,
                            layers_run=layers_run,
                            layers_passed=layers_passed,
                            layers_failed=layers_failed,
                            all_issues=all_issues,
                            issues_by_layer=issues_by_layer,
                            version=version,
                            stopped_at_layer=stopped_at_layer,
                        )
            except Exception as e:
                logger.error(f"Layer 3 validation error: {e}")
                layers_failed.append(ValidationLayer.XML_WELLFORMED)

        # Layer 4: XML_SCHEMA (Blocking)
        if ValidationLayer.XML_SCHEMA in layers:
            logger.info("Running Layer 4: XML_SCHEMA validation")
            layers_run.append(ValidationLayer.XML_SCHEMA)

            try:
                result = self.validate_xml_schema(xml_content, version)

                if result.issues:
                    all_issues.extend(result.issues)
                    issues_by_layer[ValidationLayer.XML_SCHEMA] = result.issues

                if self._is_validation_passed(result):
                    layers_passed.append(ValidationLayer.XML_SCHEMA)
                else:
                    layers_failed.append(ValidationLayer.XML_SCHEMA)

                    if stop_on_error:
                        logger.warning("Layer 4 failed, stopping validation")
                        stopped_at_layer = ValidationLayer.XML_SCHEMA
                        return ComprehensiveValidationResult(
                            is_valid=False,
                            layers_run=layers_run,
                            layers_passed=layers_passed,
                            layers_failed=layers_failed,
                            all_issues=all_issues,
                            issues_by_layer=issues_by_layer,
                            version=version,
                            stopped_at_layer=stopped_at_layer,
                        )
            except Exception as e:
                logger.error(f"Layer 4 validation error: {e}")
                layers_failed.append(ValidationLayer.XML_SCHEMA)

        # Layers 5-7: Non-blocking, run in parallel
        parallel_layers = [
            layer
            for layer in [ValidationLayer.SCHEMATRON, ValidationLayer.GML_REFERENCES, ValidationLayer.WMO_CODELISTS]
            if layer in layers
        ]

        if parallel_layers:
            logger.info(f"Running layers {parallel_layers} in parallel")

            # Run parallel validators
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}

                # Layer 5: SCHEMATRON
                if ValidationLayer.SCHEMATRON in parallel_layers:
                    try:
                        # Native-first (EV-055); legacy lxml only when Rust unavailable.
                        from iwxxm_validate import rust_available as _rust_schematron_ok

                        if not _rust_schematron_ok() and self.schematron_validator is None:
                            raise RuntimeError("Schematron validator unavailable")
                        futures[ValidationLayer.SCHEMATRON] = executor.submit(
                            self._validate_schematron, xml_content, version
                        )
                    except Exception as e:
                        logger.warning(f"Schematron setup warning: {e}")
                        layers_run.append(ValidationLayer.SCHEMATRON)
                        issue = ValidationIssue(
                            layer=ValidationLayer.SCHEMATRON,
                            level=ValidationSeverity.WARNING,
                            message=f"Schematron validation unavailable: {str(e)}",
                            code="SCHEMATRON_SETUP_WARNING",
                        )
                        all_issues.append(issue)
                        issues_by_layer[ValidationLayer.SCHEMATRON] = [issue]
                        layers_passed.append(ValidationLayer.SCHEMATRON)

                # Layer 6: GML_REFERENCES
                if ValidationLayer.GML_REFERENCES in parallel_layers:
                    try:
                        futures[ValidationLayer.GML_REFERENCES] = executor.submit(
                            self.gml_validator.validate, xml_content, version
                        )
                    except Exception as e:
                        logger.warning(f"GML setup warning: {e}")
                        layers_run.append(ValidationLayer.GML_REFERENCES)
                        issue = ValidationIssue(
                            layer=ValidationLayer.GML_REFERENCES,
                            level=ValidationSeverity.WARNING,
                            message=f"GML reference validation unavailable: {str(e)}",
                            code="GML_SETUP_WARNING",
                        )
                        all_issues.append(issue)
                        issues_by_layer[ValidationLayer.GML_REFERENCES] = [issue]
                        layers_passed.append(ValidationLayer.GML_REFERENCES)

                # Layer 7: WMO_CODELISTS
                if ValidationLayer.WMO_CODELISTS in parallel_layers:
                    try:
                        codelists_dir = self.schema_registry.get_codelists_dir(version)
                        parser = get_codelist_parser(version, codelists_dir)
                        futures[ValidationLayer.WMO_CODELISTS] = executor.submit(
                            parser.validate_xml_codelists, xml_content
                        )
                    except Exception as e:
                        logger.warning(f"WMO codelist setup warning: {e}")
                        layers_run.append(ValidationLayer.WMO_CODELISTS)
                        issue = ValidationIssue(
                            layer=ValidationLayer.WMO_CODELISTS,
                            level=ValidationSeverity.WARNING,
                            message=f"WMO codelist validation unavailable: {str(e)}",
                            code="WMO_CODELISTS_SETUP_WARNING",
                        )
                        all_issues.append(issue)
                        issues_by_layer[ValidationLayer.WMO_CODELISTS] = [issue]
                        layers_passed.append(ValidationLayer.WMO_CODELISTS)

                # Collect results
                for layer, future in futures.items():
                    layers_run.append(layer)

                    try:
                        result = future.result(timeout=30)  # 30 second timeout

                        if result.issues:
                            all_issues.extend(result.issues)
                            issues_by_layer[layer] = result.issues

                        if self._is_validation_passed(result):
                            layers_passed.append(layer)
                        else:
                            layers_failed.append(layer)

                    except Exception as e:
                        logger.error(f"Layer {layer} validation error: {e}")
                        layers_failed.append(layer)

                        issue = ValidationIssue(
                            layer=layer,
                            level=ValidationSeverity.ERROR,
                            message=f"Validation error: {str(e)}",
                            code="VALIDATION_ERROR",
                        )
                        all_issues.append(issue)
                        issues_by_layer[layer] = [issue]

        # Determine overall validity
        is_valid = len(layers_failed) == 0

        logger.info(
            f"Validation complete: {len(layers_passed)} passed, "
            f"{len(layers_failed)} failed, {len(all_issues)} total issues"
        )

        return ComprehensiveValidationResult(
            is_valid=is_valid,
            layers_run=layers_run,
            layers_passed=layers_passed,
            layers_failed=layers_failed,
            all_issues=all_issues,
            issues_by_layer=issues_by_layer,
            version=version,
            stopped_at_layer=stopped_at_layer,
        )


# Singleton instance
_orchestrator_instance: Optional[ValidationOrchestrator] = None


def get_validation_orchestrator() -> ValidationOrchestrator:
    """
    Get singleton validation orchestrator instance.

    Returns:
        ValidationOrchestrator instance
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ValidationOrchestrator()
    return _orchestrator_instance
