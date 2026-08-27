"""
IWXXM Validation Orchestrator

Coordinates validation layers with proper sequencing, parallelization,
and error handling. IWXXM layers (3-7) delegate to ``iwxxm_validation_adapter``
(``packages/iwxxm-validate``); TAC layers (1-2) remain in ``ValidationService``.
"""

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from ..schemas.validation import (
    CodelistValidationResult,
    GMLValidationResult,
    SchematronValidationResult,
    ValidationIssue,
    ValidationLayer,
    ValidationResult,
    ValidationSeverity,
    XSDValidationResult,
)
from ..services.validation import ValidationService
from . import iwxxm_validation_adapter as iwxxm_adapter

logger = logging.getLogger(__name__)

ValidationOutcome = (
    ValidationResult | XSDValidationResult | SchematronValidationResult | GMLValidationResult | CodelistValidationResult
)


@dataclass
class ComprehensiveValidationResult:
    """Result of comprehensive multi-layer validation."""

    is_valid: bool
    layers_run: list[ValidationLayer]
    layers_passed: list[ValidationLayer]
    layers_failed: list[ValidationLayer]
    all_issues: list[ValidationIssue]
    issues_by_layer: dict[ValidationLayer, list[ValidationIssue]] = field(default_factory=dict)
    version: str = ""
    stopped_at_layer: ValidationLayer | None = None

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
    3. Layer 3 (XML_WELLFORMED) - Blocking - package
    4. Layer 4 (XML_SCHEMA) - Blocking - package
    5-7. Layers 5-7 (SCHEMATRON, GML_REFERENCES, WMO_CODELISTS) - Parallel, non-blocking - package
    """

    def __init__(self) -> None:
        """Initialize validation orchestrator."""
        self.validation_service = ValidationService()

    def _is_validation_passed(self, result: ValidationOutcome) -> bool:
        """Check if validation passed, handling both ValidationResult and specialized types."""
        passed = getattr(result, "passed", None)
        if isinstance(passed, bool):
            return passed
        is_valid = getattr(result, "is_valid", None)
        if isinstance(is_valid, bool):
            return is_valid
        logger.warning(f"Unknown result type {type(result)}: cannot determine pass/fail")
        return False

    def validate_wellformed(self, xml_content: str) -> ValidationResult:
        """Public XML well-formedness validation helper."""
        return iwxxm_adapter.validate_wellformed(xml_content)

    def validate_xml_schema(self, xml_content: str, version: str) -> XSDValidationResult:
        """Public XML schema validation helper."""
        return iwxxm_adapter.validate_xml_schema(xml_content, version)

    def _validate_schematron(self, xml_content: str, version: str) -> SchematronValidationResult:
        """Schematron layer via package."""
        return iwxxm_adapter.validate_schematron(xml_content, version)

    def validate(
        self,
        xml_content: str,
        *,
        iwxxm_version: str,
        layers: list[ValidationLayer] | None = None,
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
        layers: list[ValidationLayer] | None = None,
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
        if layers is None:
            layers = list(ValidationLayer)

        layers_run: list[ValidationLayer] = []
        layers_passed: list[ValidationLayer] = []
        layers_failed: list[ValidationLayer] = []
        all_issues: list[ValidationIssue] = []
        issues_by_layer: dict[ValidationLayer, list[ValidationIssue]] = {}
        stopped_at_layer = None

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

        parallel_layers = [
            layer
            for layer in [ValidationLayer.SCHEMATRON, ValidationLayer.GML_REFERENCES, ValidationLayer.WMO_CODELISTS]
            if layer in layers
        ]

        if parallel_layers:
            logger.info(f"Running layers {parallel_layers} in parallel")

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures: dict[ValidationLayer, Future[Any]] = {}

                if ValidationLayer.SCHEMATRON in parallel_layers:
                    futures[ValidationLayer.SCHEMATRON] = executor.submit(
                        self._validate_schematron, xml_content, version
                    )

                if ValidationLayer.GML_REFERENCES in parallel_layers:
                    futures[ValidationLayer.GML_REFERENCES] = executor.submit(self._run_gml_layer, xml_content, version)

                if ValidationLayer.WMO_CODELISTS in parallel_layers:
                    futures[ValidationLayer.WMO_CODELISTS] = executor.submit(
                        self._run_codelist_layer, xml_content, version
                    )

                for layer, future in futures.items():
                    layers_run.append(layer)

                    try:
                        result = future.result(timeout=30)

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
                            message=f"Validation error: {e!s}",
                            code="VALIDATION_ERROR",
                        )
                        all_issues.append(issue)
                        issues_by_layer[layer] = [issue]

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

    @staticmethod
    def _run_gml_layer(xml_content: str, version: str) -> GMLValidationResult:
        is_valid, issues = iwxxm_adapter.validate_gml_references(xml_content, version)
        return GMLValidationResult(is_valid=is_valid, issues=issues)

    @staticmethod
    def _run_codelist_layer(xml_content: str, version: str) -> CodelistValidationResult:
        is_valid, issues = iwxxm_adapter.validate_wmo_codelists(xml_content, version)
        return CodelistValidationResult(is_valid=is_valid, issues=issues)


_orchestrator_instance: ValidationOrchestrator | None = None


def get_validation_orchestrator() -> ValidationOrchestrator:
    """Get singleton validation orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ValidationOrchestrator()
    return _orchestrator_instance
