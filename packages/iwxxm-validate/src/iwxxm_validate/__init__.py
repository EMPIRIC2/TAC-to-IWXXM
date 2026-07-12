"""IWXXM XSD + Schematron validation engine (F2 package)."""

from __future__ import annotations

from iwxxm_validate.api import validate
from iwxxm_validate.models import Issue, ValidationReport

__version__ = "0.1.0"

__all__ = ["Issue", "ValidationReport", "__version__", "validate"]
