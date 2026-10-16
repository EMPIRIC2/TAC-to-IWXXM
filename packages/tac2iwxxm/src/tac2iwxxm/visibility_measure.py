"""Prevailing visibility for statute miles and the 9999 metre group."""

from __future__ import annotations

import re

# A slash is not a word character, so ``\\b`` matches ``2SM`` inside ``1 1/2SM``.
_MILES = r"\d{1,2}(?:\s+\d/\d)?|\d/\d"
METAR_STATUTE_MILE_GROUP = re.compile(rf"(?<![A-Z0-9/])(?P<vis>{_MILES})SM(?![A-Z0-9/])")
TAF_STATUTE_MILE_GROUP = re.compile(rf"(?<![A-Z0-9/])(?P<mod>P)?(?P<vis>{_MILES})SM(?![A-Z0-9/])")

_STATUTE_MILE_METRES = 1609.344


def prevailing_from_statute_miles(statute_miles: float) -> tuple[int, bool]:
    """
    Convert statute miles to prevailing metres.

    Ten statute miles or more is 10 km or more.

    Parameters
    ----------
    statute_miles :
        Parsed statute miles, including a mixed fraction such as 1.5.

    Returns
    -------
    tuple[int, bool]
        Metres, and whether the reading is 10 km or more.

    Examples
    --------
    >>> prevailing_from_statute_miles(10)
    (10000, True)
    >>> prevailing_from_statute_miles(1.5)
    (2414, False)
    """
    if statute_miles >= 10:
        return 10000, True
    return round(statute_miles * _STATUTE_MILE_METRES), False


def prevailing_from_metre_group(metres: int) -> tuple[int, bool]:
    """
    Convert a four-digit metre group to prevailing metres.

    ``9999`` is 10 km or more, the same convention as 10 statute miles.

    Parameters
    ----------
    metres :
        The four-digit visibility group.

    Returns
    -------
    tuple[int, bool]
        Metres, and whether the reading is 10 km or more.

    Examples
    --------
    >>> prevailing_from_metre_group(9999)
    (10000, True)
    >>> prevailing_from_metre_group(8000)
    (8000, False)
    """
    if metres >= 9999:
        return 10000, True
    return metres, False
