"""msgspec models for IWXXM validation reports (ADR-016)."""

from __future__ import annotations

import msgspec


class Issue(msgspec.Struct, frozen=True):
    """
    Single validation finding.

    Parameters
    ----------
    severity :
        ``error``, ``warning``, or ``info``.
    code :
        Machine-readable issue code (e.g. ``XML_SYNTAX_ERROR``).
    message :
        Human-readable description.
    layer :
        Validation layer (``xsd``, ``schematron``, ``wellformed``).
    location :
        Optional document location hint.
    """

    severity: str
    code: str
    message: str
    layer: str
    location: str | None = None


class ValidationReport(msgspec.Struct, frozen=True):
    """
    Aggregate result of ``validate()``.

    Parameters
    ----------
    ok :
        ``True`` when no blocking (error-severity) issues remain.
    iwxxm_version :
        Requested IWXXM release line.
    profile :
        ``annex3`` or ``iwxxm_us``.
    issues :
        Ordered list of findings (may include non-blocking warnings).
    """

    ok: bool
    iwxxm_version: str
    profile: str
    issues: list[Issue]


__all__ = ["Issue", "ValidationReport"]
