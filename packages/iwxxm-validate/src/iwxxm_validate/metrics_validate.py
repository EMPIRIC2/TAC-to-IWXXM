"""Quality-metrics validate entrypoint - native-first (EV-055 / #980 / #979).

Prefer ``validate_iwxxm`` so IWXXM 2025-2 Schematron (xslt2) and XSD are evaluated
when the Rust extension is built. Soft ``SCHEMATRON_SKIPPED`` /
``SCHEMA_IMPORT_WARNING`` from the lxml-only ``validate()`` path are not an
acceptable close for Quality metrics when native is available.
"""

from __future__ import annotations

from collections.abc import Sequence

from iwxxm_validate.models import ValidationReport
from iwxxm_validate.validate_iwxxm import validate_iwxxm


def validate_for_quality_metrics(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str = "annex3",
    levels: Sequence[str] | None = None,
) -> ValidationReport:
    """
    Validate IWXXM for Quality metrics / corpus precompute.

    Uses the F13 native hot path (``validate_iwxxm``), which evaluates 2025-2
    Schematron and strict XSD when ``iwxxm_validate._rust`` is built. Falls back
    to the same entrypoint's lxml path only when the extension is absent.

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    iwxxm_version :
        Release line (e.g. ``2025-2``).
    profile :
        ``annex3`` or ``iwxxm_us``.
    levels :
        Subset of ``xsd`` / ``schematron``. Default runs both.

    Returns
    -------
    ValidationReport
        Native evaluation when Rust is available.
    """
    return validate_iwxxm(
        xml_content,
        iwxxm_version=iwxxm_version,
        profile=profile,
        levels=levels,
    )


__all__ = ["validate_for_quality_metrics"]
