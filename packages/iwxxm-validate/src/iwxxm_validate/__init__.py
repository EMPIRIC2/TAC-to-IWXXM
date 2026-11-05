"""IWXXM XSD + Schematron validation engine (F2 package).

Call :func:`iwxxm_validate.api.validate` for XSD/Schematron reports against
pinned vendor schemas. Public APIs use NumPy docstrings
(``docs/engineering/docstrings.md``).

Start here
----------
- Validate IWXXM XML: :func:`validate` / :func:`validate_iwxxm`
- Compare two documents for Quality Metrics (ignore formatting):
  :func:`to_canonical_xml` / :func:`canonical_xml_equal`
  (aliases ``c14n_xml`` / ``c14n_equal`` remain for one CalVer window)
- Quality Metrics-oriented validation: :func:`validate_for_quality_metrics`
- Rust engine probe: :func:`rust_available`
"""

from __future__ import annotations

from iwxxm_validate.api import validate
from iwxxm_validate.canonical_xml import (
    c14n_equal,
    c14n_xml,
    canonical_xml_equal,
    to_canonical_xml,
)
from iwxxm_validate.metrics_validate import validate_for_quality_metrics
from iwxxm_validate.models import Issue, StageResult, ValidationReport
from iwxxm_validate.native import clear_schema_caches, rust_available, rust_module
from iwxxm_validate.validate_iwxxm import validate_iwxxm

__version__ = "2026.9.22"

__all__ = [
    "Issue",
    "StageResult",
    "ValidationReport",
    "__version__",
    "c14n_equal",
    "c14n_xml",
    "canonical_xml_equal",
    "clear_schema_caches",
    "rust_available",
    "rust_module",
    "to_canonical_xml",
    "validate",
    "validate_for_quality_metrics",
    "validate_iwxxm",
]
