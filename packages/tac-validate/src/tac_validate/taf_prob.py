"""Classify TAF probability tokens (PROB30/40) against TEMPO / period / INTER forms."""

from __future__ import annotations

import re
from enum import StrEnum

_PERIOD = re.compile(r"\d{4}/\d{4}")
_TEMPO_QUALIFIER = frozenset({"TEMPO", "EMPO"})
_FM = re.compile(r"^FM\d{6}$")


class ProbGroupKind(StrEnum):
    """How a ``PROBnn`` token relates to the following TAC tokens."""

    TEMPO_OK = "tempo_ok"
    """``PROB30|40 TEMPO|EMPO ddhh/ddhh`` — informational."""

    PERIOD_WITHOUT_TEMPO = "period_without_tempo"
    """``PROB30|40 ddhh/ddhh …`` — common national form; warning, not error."""

    INTER = "inter"
    """``PROB30|40 INTER ddhh/ddhh …`` — national INTER qualifier; warning until decided."""

    INVALID = "invalid"
    """True defect: bad percent, PROB on BECMG/FM, truncated, or unusable shape."""


def classify_probability_group(tokens: list[str], index: int) -> ProbGroupKind:
    """
    Classify the probability token at ``index``.

    Parameters
    ----------
    tokens : list[str]
        Uppercase TAC tokens.
    index : int
        Position of a ``PROBnn`` token.

    Returns
    -------
    ProbGroupKind
        Severity-driving class for lint emission.

    Examples
    --------
    >>> classify_probability_group(["PROB40", "TEMPO", "0818/0822"], 0)
    <ProbGroupKind.TEMPO_OK: 'tempo_ok'>
    >>> classify_probability_group(["PROB30", "0108/0112", "1SM", "BR"], 0)
    <ProbGroupKind.PERIOD_WITHOUT_TEMPO: 'period_without_tempo'>
    >>> classify_probability_group(["PROB30", "BECMG", "0814/0816"], 0)
    <ProbGroupKind.INVALID: 'invalid'>
    """
    if index < 0 or index >= len(tokens):
        return ProbGroupKind.INVALID
    match = re.fullmatch(r"PROB(\d{2})", tokens[index])
    if match is None or match.group(1) not in {"30", "40"}:
        return ProbGroupKind.INVALID
    if index + 1 >= len(tokens):
        return ProbGroupKind.INVALID
    nxt = tokens[index + 1]
    if nxt in {"BECMG"} or _FM.fullmatch(nxt):
        return ProbGroupKind.INVALID
    if nxt in _TEMPO_QUALIFIER:
        if index + 2 < len(tokens) and _PERIOD.fullmatch(tokens[index + 2]):
            return ProbGroupKind.TEMPO_OK
        return ProbGroupKind.INVALID
    if nxt == "INTER":
        if index + 2 < len(tokens) and _PERIOD.fullmatch(tokens[index + 2]):
            return ProbGroupKind.INTER
        return ProbGroupKind.INVALID
    if _PERIOD.fullmatch(nxt):
        return ProbGroupKind.PERIOD_WITHOUT_TEMPO
    return ProbGroupKind.INVALID


def probability_group_valid(tokens: list[str], index: int) -> bool:
    """
    Return whether the probability token at ``index`` is the TEMPO/EMPO info form.

    Kept for callers that only need the Annex-style TEMPO shape. Prefer
    ``classify_probability_group`` for lint emission.

    Parameters
    ----------
    tokens : list[str]
        Uppercase TAC tokens.
    index : int
        Position of a ``PROBnn`` token.

    Returns
    -------
    bool
        True only for ``PROB30`` or ``PROB40`` followed by ``TEMPO`` or ``EMPO``
        and a ``ddhh/ddhh`` period.

    Examples
    --------
    >>> probability_group_valid(["PROB40", "TEMPO", "0818/0822"], 0)
    True
    >>> probability_group_valid(["PROB30", "0108/0112", "1SM"], 0)
    False
    """
    return classify_probability_group(tokens, index) is ProbGroupKind.TEMPO_OK
