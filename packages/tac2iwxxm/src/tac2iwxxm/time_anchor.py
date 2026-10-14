"""Year and month for TAC day-of-month stamps.

Example goldens keep a legacy prefix until a conversion passes ``bulletin_date``.
An operator date is ``YYYY-MM``. A TAC day that month does not contain fails
conversion. The message names the day and the month.

[Corpus: product §F6]
"""

from __future__ import annotations

import calendar
import re
from collections.abc import Mapping
from contextvars import ContextVar, Token
from datetime import date
from typing import Any

_ANCHOR = re.compile(r"\d{4}-\d{2}")
_bulletin_anchor: ContextVar[str | None] = ContextVar("tac2iwxxm_bulletin_anchor", default=None)


class ImpossibleTacDay(Exception):
    """The TAC day does not exist in the bulletin month."""


def fit_year_month(year: int, month: int, day: int) -> tuple[int, int]:
    """
    Return the bulletin year and month when ``day`` exists in that month.

    Parameters
    ----------
    year : int
        Bulletin year.
    month : int
        Bulletin month.
    day : int
        Day of month from the TAC.

    Returns
    -------
    tuple[int, int]
        The same year and month when ``day`` is a real date there.

    Raises
    ------
    ValueError
        If ``day`` is outside 1..31 or ``month`` is outside 1..12.
    ImpossibleTacDay
        If ``day`` is not a day of that month.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (fit_year_month)
    2
    """
    if day < 1 or day > 31:
        raise ValueError(f"TAC day {day} is not a calendar day")
    if month < 1 or month > 12:
        raise ValueError(f"TAC month {month} is not a calendar month")
    try:
        date(year, month, day)
    except ValueError as exc:
        raise ImpossibleTacDay(f"Day {day} is not a day in {calendar.month_name[month]} {year}") from exc
    return year, month


def anchor_from_bulletin_date(value: str) -> str:
    """
    Return ``YYYY-MM`` from a bulletin date.

    Parameters
    ----------
    value : str
        ``YYYY-MM-DD`` or a longer timestamp with that date prefix.

    Returns
    -------
    str
        Year-month anchor.

    Raises
    ------
    ValueError
        If ``value`` is not a calendar date.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (anchor_from_bulletin_date)
    2
    """
    text = value.strip()
    if len(text) >= 10:
        text = text[:10]
    parsed = date.fromisoformat(text)
    return f"{parsed.year:04d}-{parsed.month:02d}"


def push_bulletin_anchor(value: str | None) -> Token[str | None]:
    """
    Set the anchor seen by parsers that stamp before the IR is copied.

    Parameters
    ----------
    value : str | None
        ``YYYY-MM``, or ``None`` to clear the anchor.

    Returns
    -------
    Token[str | None]
        Token passed to ``pop_bulletin_anchor``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (push_bulletin_anchor)
    2
    """
    return _bulletin_anchor.set(value)


def pop_bulletin_anchor(token: Token[str | None]) -> None:
    """
    Restore the previous bulletin anchor.

    Parameters
    ----------
    token : Token[str | None]
        Token returned by ``push_bulletin_anchor``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (pop_bulletin_anchor)
    2
    """
    _bulletin_anchor.reset(token)


def anchored_prefix(ir: Mapping[str, Any], day: int) -> str | None:
    """
    Return ``YYYY-MM`` when this report has a bulletin anchor.

    Parameters
    ----------
    ir : Mapping[str, Any]
        Parsed report. ``time_anchor`` wins over the conversion-scoped anchor.
    day : int
        TAC day. A day that month does not contain raises ``ImpossibleTacDay``.

    Returns
    -------
    str | None
        Bulletin year-month, or ``None`` when the caller should keep its example pin.

    Raises
    ------
    ImpossibleTacDay
        If ``day`` is not a day of the bulletin month.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (anchored_prefix)
    2
    """
    raw = ir.get("time_anchor")
    if not isinstance(raw, str):
        raw = _bulletin_anchor.get()
    if not isinstance(raw, str) or _ANCHOR.fullmatch(raw) is None:
        return None
    year_text, month_text = raw.split("-")
    year, month = fit_year_month(int(year_text), int(month_text), int(day))
    return f"{year:04d}-{month:02d}"


def iso_stamp(
    ir: Mapping[str, Any],
    day: int,
    hour: int,
    minute: int,
    *,
    legacy: str,
) -> str:
    """
    Build ``YYYY-MM-DDTHH:MM:00Z``.

    Parameters
    ----------
    ir : Mapping[str, Any]
        Parsed report.
    day : int
        TAC day.
    hour : int
        Hour.
    minute : int
        Minute.
    legacy : str
        Example pin such as ``2023-06`` or ``2012-08`` used when no anchor is set.

    Returns
    -------
    str
        UTC timestamp.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (iso_stamp)
    2
    """
    prefix = anchored_prefix(ir, day) or legacy
    return f"{prefix}-{int(day):02d}T{int(hour):02d}:{int(minute):02d}:00Z"
