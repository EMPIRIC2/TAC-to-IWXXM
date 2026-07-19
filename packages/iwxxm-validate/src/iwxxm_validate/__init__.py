"""IWXXM XSD + Schematron validation engine (F2 package)."""

from __future__ import annotations

from iwxxm_validate.api import validate
from iwxxm_validate.models import Issue, ValidationReport
from iwxxm_validate.native import rust_available, rust_module
from iwxxm_validate.validate_iwxxm import validate_iwxxm

__version__ = "0.1.0"

__all__ = [
    "Issue",
    "ValidationReport",
    "__version__",
    "rust_available",
    "rust_module",
    "validate",
    "validate_iwxxm",
]
