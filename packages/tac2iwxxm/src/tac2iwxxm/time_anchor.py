"""Year and month for TAC day-of-month stamps.

Example goldens keep a legacy prefix until a conversion passes ``bulletin_date``.
An operator date is ``YYYY-MM``. Each TAC day is placed in that month, or in the
previous month that contains the day.

[Corpus: product §F6]
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from contextvars import ContextVar, Token
from datetime import date
from typing import Any

_ANCHOR = re.compile(r"\d{4}-\d{2}")
_bulletin_anchor: ContextVar[str | None] = ContextVar("tac2iwxxm_bulletin_anchor", default=None)


def fit_year_month(year: int, month: int, day: int) -> tuple[int, int]:
    """
    Return a year and month that contain ``day``.

    Parameters
    ----------
    year : int
        Starting year.
    month : int
        Starting month.
    day : int
        Day of month from the TAC.

    Returns
    -------
    tuple[int, int]
        Year and month that can represent ``day``.

    Raises
    ------
    ValueError
        If ``day`` is outside 1..31.
    """
    if day < 1 or day > 31:
        raise ValueError(f"TAC day {day} is not a calendar day")
    for _ in range(48):
        try:
            date(year, month, day)
        except ValueError:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            continue
        return year, month
    raise ValueError(f"no month contains day {day}")


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
    """
    text = value.strip()
    if len(text) >= 10:
        text = text[:10]
    parsed = date.fromisoformat(text)
    return f"{parsed.year:04d}-{parsed.month:02d}"


def push_bulletin_anchor(value: str | None) -> Token[str | None]:
    """Set the anchor seen by parsers that stamp before the IR is copied."""
    return _bulletin_anchor.set(value)


def pop_bulletin_anchor(token: Token[str | None]) -> None:
    """Restore the previous bulletin anchor."""
    _bulletin_anchor.reset(token)


def anchored_prefix(ir: Mapping[str, Any], day: int) -> str | None:
    """
    Return ``YYYY-MM`` when this report has a bulletin anchor.

    Parameters
    ----------
    ir : Mapping[str, Any]
        Parsed report. ``time_anchor`` wins over the conversion-scoped anchor.
    day : int
        TAC day used to avoid an impossible civil date.

    Returns
    -------
    str | None
        Fitted year-month, or ``None`` when the caller should keep its example pin.
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
    """
    prefix = anchored_prefix(ir, day) or legacy
    return f"{prefix}-{int(day):02d}T{int(hour):02d}:{int(minute):02d}:00Z"
