"""msgspec models for TAC lint issues and fixes (ADR-016 / Q9=C)."""

from __future__ import annotations

import msgspec


class Issue(msgspec.Struct, frozen=True):
    """
    Structured TAC lint finding.

    Parameters
    ----------
    severity : str
        ``error``, ``warning``, or ``info``.
    code : str
        Machine-readable rule id.
    message : str
        Human-readable description.
    location : str or None, optional
        Token or field hint (for example ``wind``). By default ``None``.
    start : int or None, optional
        Inclusive character offset into the TAC string. By default ``None``.
    end : int or None, optional
        Exclusive character offset into the TAC string. By default ``None``.
    """

    severity: str
    code: str
    message: str
    location: str | None = None
    start: int | None = None
    end: int | None = None


class Fix(msgspec.Struct, frozen=True):
    """
    Optional repair suggestion for a lint finding.

    Parameters
    ----------
    code : str
        Fix identifier (e.g. ``add_terminator``).
    message : str
        Human-readable description.
    replacement : str
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
    ok : bool
        ``True`` when no error-severity issues.
    product : str
        Product id used for rule selection.
    issues : list[Issue]
        Structured findings.
    fixes : list[Fix], optional
        Repair suggestions. By default an empty list.
    profile : str, optional
        Semantic profile the findings were judged under. By default ``"annex3"``.
    """

    ok: bool
    product: str
    issues: list[Issue]
    fixes: list[Fix] = msgspec.field(default_factory=list)
    profile: str = "annex3"


__all__ = ["Fix", "Issue", "LintReport"]
