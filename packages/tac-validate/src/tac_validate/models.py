"""msgspec models for TAC lint issues and fixes (ADR-016 / Q9=C)."""

from __future__ import annotations

import msgspec


class Issue(msgspec.Struct, frozen=True):
    """
    Structured TAC lint finding.

    Parameters
    ----------
    severity :
        ``error``, ``warning``, or ``info``.
    code :
        Machine-readable rule id.
    message :
        Human-readable description.
    location :
        Optional token / field hint (e.g. ``wind``).
    """

    severity: str
    code: str
    message: str
    location: str | None = None


class Fix(msgspec.Struct, frozen=True):
    """
    Optional repair suggestion for a lint finding.

    Parameters
    ----------
    code :
        Fix identifier (e.g. ``normalize_terminator``).
    message :
        Human-readable description.
    replacement :
        Suggested replacement fragment or full TAC.
    """

    code: str
    message: str
    replacement: str


class LintReport(msgspec.Struct, frozen=True):
    """
    Result of ``lint()``.

    Parameters
    ----------
    ok :
        ``True`` when no error-severity issues.
    product :
        Product id used for rule selection.
    issues :
        Structured findings.
    fixes :
        Optional repair suggestions.
    """

    ok: bool
    product: str
    issues: list[Issue]
    fixes: list[Fix] = msgspec.field(default_factory=list)


__all__ = ["Fix", "Issue", "LintReport"]
