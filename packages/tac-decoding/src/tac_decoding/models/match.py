"""Match context and span models.

[Corpus: product §F9]
"""

from __future__ import annotations

from dataclasses import dataclass


class MatchBudgetError(ValueError):
    """
    The matcher stopped because it used its step budget.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class MatchContext:
    """
    Caller-owned version and profile. Packs do not select these.

    Attributes
    ----------
    iwxxm_version : str | None
        IWXXM release line. Default ``None``.
    profile : str | None
        Semantic profile id. Default ``None``.
    """

    iwxxm_version: str | None = None
    profile: str | None = None


@dataclass(frozen=True, slots=True)
class MatchSpan:
    """
    One matched or residual slice of the original TAC.

    Attributes
    ----------
    start : int
        Start.
    end : int
        End.
    code : str
        Machine-readable error code.
    explanation : str
        Explanation.
    rule_id : str
        Rule id.
    """

    start: int
    end: int
    code: str
    explanation: str
    rule_id: str


@dataclass(frozen=True, slots=True)
class MatchResult:
    """
    Spans, leftovers, and the version context the caller supplied.

    Attributes
    ----------
    spans : tuple[MatchSpan, ...]
        Spans.
    residuals : tuple[MatchSpan, ...]
        Residuals.
    steps : int
        Steps.
    iwxxm_version : str | None
        IWXXM release line.
    profile : str | None
        Semantic profile id.
    """

    spans: tuple[MatchSpan, ...]
    residuals: tuple[MatchSpan, ...]
    steps: int
    iwxxm_version: str | None
    profile: str | None


__all__ = ["MatchBudgetError", "MatchContext", "MatchResult", "MatchSpan"]
