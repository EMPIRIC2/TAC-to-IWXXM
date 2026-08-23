"""IWXXM XSD + Schematron validation engine (F2 package)."""

from __future__ import annotations

from iwxxm_validate.api import validate
from iwxxm_validate.c14n import c14n_equal, c14n_xml
from iwxxm_validate.metrics_validate import validate_for_quality_metrics
from iwxxm_validate.models import Issue, StageResult, ValidationReport
from iwxxm_validate.native import clear_schema_caches, rust_available, rust_module
from iwxxm_validate.validate_iwxxm import validate_iwxxm

__version__ = "0.2.0"

__all__ = [
    "Issue",
    "StageResult",
    "ValidationReport",
    "__version__",
    "c14n_equal",
    "c14n_xml",
    "clear_schema_caches",
    "rust_available",
    "rust_module",
    "validate",
    "validate_for_quality_metrics",
    "validate_iwxxm",
]
