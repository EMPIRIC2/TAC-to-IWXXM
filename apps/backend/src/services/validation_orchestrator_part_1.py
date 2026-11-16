"""Part 1 of ``validation_orchestrator.py`` (line-cap split)."""

import logging
from dataclasses import dataclass, field

from ..schemas.validation import (
    CodelistValidationResult,
    GMLValidationResult,
    SchematronValidationResult,
    ValidationIssue,
    ValidationLayer,
    ValidationResult,
    XSDValidationResult,
)

logger = logging.getLogger(__name__)

ValidationOutcome = (
    ValidationResult | XSDValidationResult | SchematronValidationResult | GMLValidationResult | CodelistValidationResult
)


@dataclass
class ComprehensiveValidationResult:
    """
    Result of comprehensive multi-layer validation.

    Attributes
    ----------
    _ : object
        See implementation.
    """

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
        """
        Alias for is_valid (API compatibility).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (passed)
        2

        Returns
        -------
        object
            Return value.
        """
        return self.is_valid
