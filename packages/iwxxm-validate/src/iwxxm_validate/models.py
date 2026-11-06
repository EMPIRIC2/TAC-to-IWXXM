"""msgspec models for IWXXM validation reports (ADR-016)."""

from __future__ import annotations

import msgspec


class Issue(msgspec.Struct, frozen=True):
    """
    Single validation finding.

    Parameters
    ----------
    severity : str
        ``error``, ``warning``, or ``info``.
    code : str
        Machine-readable issue code (e.g. ``XML_SYNTAX_ERROR``).
    message : str
        Human-readable description.
    layer : str
        Validation layer (``xsd``, ``schematron``, ``wellformed``).
    location : str or None, optional
        Document location hint. By default ``None``.
    start : int or None, optional
        Inclusive character or document offset. By default ``None``.
    end : int or None, optional
        Exclusive character or document offset. By default ``None``.
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
    stage : str
        Stage id aligned with ``catalog.yaml`` ``validation_stages`` (e.g. ``wmo_xsd``).
    label : str
        Operator-readable stage label (EV-048 - no planning tokens).
    ok : bool
        ``True`` when the stage has no error-severity issues.
    issues : list[Issue]
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
    ok : bool
        ``True`` when no blocking (error-severity) issues remain.
    iwxxm_version : str
        Requested IWXXM release line.
    profile : str
        ``annex3``, ``iwxxm_us``, or ``ca_eccc``.
    issues : list[Issue]
        Ordered list of findings (may include non-blocking warnings).
    stages : list[StageResult]
        Per-stage breakdown when ``profile=ca_eccc`` layered validation runs.
    """

    ok: bool
    iwxxm_version: str
    profile: str
    issues: list[Issue]
    stages: list[StageResult] = []


__all__ = ["Issue", "StageResult", "ValidationReport"]
