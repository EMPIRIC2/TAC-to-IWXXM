"""Decide whether a TAF probability token qualifies a temporary group."""

from __future__ import annotations

import re

_PERIOD = re.compile(r"\d{4}/\d{4}")
_QUALIFIER = {"TEMPO", "EMPO"}


def probability_group_valid(tokens: list[str], index: int) -> bool:
    """
    Return whether the probability token at ``index`` qualifies a timed TEMPO group.

    Parameters
    ----------
    tokens : list[str]
        Uppercase TAC tokens.
    index : int
        Position of a ``PROBnn`` token.

    Returns
    -------
    bool
        True only for ``PROB30`` or ``PROB40`` followed by ``TEMPO`` or ``EMPO`` and a ``ddhh/ddhh`` period.

    Examples
    --------
    >>> probability_group_valid(["PROB40", "TEMPO", "0818/0822"], 0)
    True
    >>> probability_group_valid(["PROB30", "4000"], 0)
    False
    """
    if index < 0:
        return False
    try:
        token = tokens[index]
        qualifier = tokens[index + 1]
        period = tokens[index + 2]
    except IndexError:
        return False
    match = re.fullmatch(r"PROB(\d{2})", token)
    if match is None or match.group(1) not in {"30", "40"}:
        return False
    if qualifier not in _QUALIFIER:
        return False
    return _PERIOD.fullmatch(period) is not None
