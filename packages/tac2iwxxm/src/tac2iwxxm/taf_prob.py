"""Map a TAF probability token onto the temporary-forecast change indicator."""

from __future__ import annotations

import re

_PROB_TEMPO = re.compile(
    r"^PROB(?P<pct>30|40)\s+(?P<kind>TEMPO|EMPO)\s+(?P<from>\d{4})/(?P<to>\d{4})\s+(?P<body>.*)$",
    re.DOTALL,
)
_BARE_PROB = re.compile(r"^PROB(?:30|40)\b")


_INDICATORS = {
    "30": "PROBABILITY_30_TEMPORARY_FLUCTUATIONS",
    "40": "PROBABILITY_40_TEMPORARY_FLUCTUATIONS",
}


def temporary_probability_indicator(percent: str) -> str | None:
    """
    Return the IWXXM change indicator for a 30 or 40 percent temporary group.

    Parameters
    ----------
    percent :
        The two digits after ``PROB``.

    Returns
    -------
    str | None
        ``PROBABILITY_30_TEMPORARY_FLUCTUATIONS`` or ``PROBABILITY_40_TEMPORARY_FLUCTUATIONS``.
        ``None`` when the percent is neither 30 nor 40.

    Examples
    --------
    >>> temporary_probability_indicator("40")
    'PROBABILITY_40_TEMPORARY_FLUCTUATIONS'
    >>> temporary_probability_indicator("50") is None
    True
    """
    return _INDICATORS.get(percent)


def probability_tempo_parts(chunk: str) -> tuple[str, str, str, str, str] | None:
    """
    Split a ``PROB30 TEMPO`` or ``PROB40 TEMPO`` chunk into indicator, times, and body.

    Parameters
    ----------
    chunk :
        One change-group chunk, starting at the probability token.

    Returns
    -------
    tuple[str, str, str, str, str] | None
        ``(indicator, kind, from, to, body)`` or ``None`` when the chunk is not a
        probability temporary group with a time period.

    Examples
    --------
    >>> probability_tempo_parts("PROB40 TEMPO 0818/0822 4000 TSRA")
    ('PROBABILITY_40_TEMPORARY_FLUCTUATIONS', 'TEMPO', '0818', '0822', '4000 TSRA')
    """
    match = _PROB_TEMPO.match(chunk.strip())
    if match is None:
        return None
    indicator = _INDICATORS[match.group("pct")]
    return (indicator, match.group("kind"), match.group("from"), match.group("to"), match.group("body"))


def is_unqualified_probability(chunk: str) -> bool:
    """
    Return whether ``chunk`` opens with a probability token that does not qualify TEMPO.

    Parameters
    ----------
    chunk :
        One change-group chunk.

    Returns
    -------
    bool
        True when the chunk starts with ``PROB30`` or ``PROB40`` and is not a temporary group.

    Examples
    --------
    >>> is_unqualified_probability("PROB30 4000 TSRA")
    True
    >>> is_unqualified_probability("PROB40 TEMPO 0818/0822 4000 TSRA")
    False
    """
    text = chunk.strip()
    if probability_tempo_parts(text) is not None:
        return False
    return _BARE_PROB.match(text) is not None
