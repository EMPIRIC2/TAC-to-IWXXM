"""IWXXM XSD + Schematron validation engine (F2 package)."""

from __future__ import annotations

from iwxxm_validate.api import validate
from iwxxm_validate.metrics_validate import validate_for_quality_metrics
from iwxxm_validate.models import Issue, ValidationReport
from iwxxm_validate.native import clear_schema_caches, rust_available, rust_module
from iwxxm_validate.validate_iwxxm import validate_iwxxm

__version__ = "0.1.2"

__all__ = [
    "Issue",
    "ValidationReport",
    "__version__",
    "clear_schema_caches",
    "rust_available",
    "rust_module",
    "validate",
    "validate_for_quality_metrics",
    "validate_iwxxm",
]
