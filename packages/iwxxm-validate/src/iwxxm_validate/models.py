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
    start :
        Optional inclusive character / document offset when known.
    end :
        Optional exclusive character / document offset when known.
    """

    severity: str
    code: str
    message: str
    layer: str
    location: str | None = None
    start: int | None = None
    end: int | None = None


class StageResult(msgspec.Struct, frozen=True):
    """
    Per-stage outcome for layered ``ca_eccc`` validation (EV-068).

    Parameters
    ----------
    stage :
        Stage id aligned with ``catalog.yaml`` ``validation_stages`` (e.g. ``wmo_xsd``).
    label :
        Operator-readable stage label (EV-048 - no planning tokens).
    ok :
        ``True`` when the stage has no error-severity issues.
    issues :
        Findings for this stage only.
    """

    stage: str
    label: str
    ok: bool
    issues: list[Issue]


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
        ``annex3``, ``iwxxm_us``, or ``ca_eccc``.
    issues :
        Ordered list of findings (may include non-blocking warnings).
    stages :
        Per-stage breakdown when ``profile=ca_eccc`` layered validation runs.
    """

    ok: bool
    iwxxm_version: str
    profile: str
    issues: list[Issue]
    stages: list[StageResult] = []


__all__ = ["Issue", "StageResult", "ValidationReport"]
