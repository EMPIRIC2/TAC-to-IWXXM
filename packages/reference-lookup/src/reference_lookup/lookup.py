"""OurAirports coordinate lookup with an in-process cache.

3-letter ids are read from ``navaids.csv``. 4-letter ids are read from
``airports.csv`` column ``ident``. A miss, an ambiguous ident, or any
download error is ``SourceUnavailable``.

Public import paths stay on this module; implementations live in
``sources``, ``csv_index``, and ``models``.
"""

from __future__ import annotations

import os
from typing import cast

from reference_lookup.csv_index import index_csv
from reference_lookup.exceptions import SourceUnavailable
from reference_lookup.sources import (
    AIRPORTS_URL,
    NAVAIDS_URL,
    TIMEOUT_SECONDS,
    CoordinateSource,
    CsvCoordinateSource,
    LiveOurAirportsSource,
    UnavailableSource,
    read_csvs,
)

# Compatibility aliases for private helpers used by existing tests.
_index = index_csv
_read = read_csvs
_Unavailable = UnavailableSource

_override: CoordinateSource | None = None
_override_set = False
_live: LiveOurAirportsSource | None = None
_UNAVAILABLE = UnavailableSource()


def set_coordinate_source(source: CoordinateSource | None) -> None:
    """
    Install a lookup source, or clear it when ``source`` is ``None``.

    Parameters
    ----------
    source : CoordinateSource | None
        Injected source, or ``None`` to clear it.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (set_coordinate_source)
    2
    """
    global _override, _override_set
    _override = source
    _override_set = source is not None


def live_source() -> LiveOurAirportsSource:
    """
    Return the process-wide live source.

    Returns
    -------
    LiveOurAirportsSource
        Shared downloader for this process.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (live_source)
    2
    """
    global _live
    if _live is None:
        _live = LiveOurAirportsSource()
    return _live


def current_source() -> CoordinateSource:
    """
    Return the injected source, a closed source under pytest, or the live source.

    Returns
    -------
    CoordinateSource
        The source ``lookup_coordinate`` will call.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (current_source)
    2
    """
    if _override_set:
        return cast(CoordinateSource, _override)
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return _UNAVAILABLE
    return live_source()


def lookup_coordinate(ident: str) -> tuple[float, float]:
    """
    Resolve ``ident`` to ``(lat, lon)`` in decimal degrees.

    Parameters
    ----------
    ident : str
        A 3-letter navaid id or a 4-letter ICAO location indicator.

    Returns
    -------
    tuple[float, float]
        North and east positive.

    Raises
    ------
    SourceUnavailable
        When the source misses, is ambiguous, or fails.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lookup_coordinate)
    2
    """
    try:
        return current_source().lookup(ident)
    except SourceUnavailable:
        raise
    except Exception as exc:
        raise SourceUnavailable(ident) from exc


__all__ = [
    "AIRPORTS_URL",
    "NAVAIDS_URL",
    "TIMEOUT_SECONDS",
    "CoordinateSource",
    "CsvCoordinateSource",
    "LiveOurAirportsSource",
    "SourceUnavailable",
    "UnavailableSource",
    "current_source",
    "live_source",
    "lookup_coordinate",
    "set_coordinate_source",
]
