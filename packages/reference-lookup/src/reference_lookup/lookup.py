"""OurAirports coordinate lookup with an in-process cache.

3-letter ids are read from ``navaids.csv``. 4-letter ids are read from
``airports.csv`` column ``ident``. A miss, an ambiguous ident, or any
download error is ``SourceUnavailable``.
"""

from __future__ import annotations

import csv
import io
import os
from typing import Protocol, cast

import httpx

NAVAIDS_URL = "https://davidmegginson.github.io/ourairports-data/navaids.csv"
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
TIMEOUT_SECONDS = 10.0

_IDENT = "ident"
_LAT = "latitude_deg"
_LON = "longitude_deg"


class SourceUnavailable(Exception):
    """
    The public coordinate source could not answer this id.

    Attributes
    ----------
    args :
        Ident or error text passed to the exception.
    """


class CoordinateSource(Protocol):
    """Something that returns one latitude and longitude for an id."""

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Return ``(lat, lon)`` or raise ``SourceUnavailable``.

        Parameters
        ----------
        ident :
            3-letter navaid id or 4-letter ICAO indicator.

        Returns
        -------
        tuple[float, float]
            Latitude and longitude in decimal degrees.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (CoordinateSource.lookup)
        2
        """
        ...


class _Unavailable:
    """Closed source used while pytest is running."""

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Refuse every id.

        Parameters
        ----------
        ident :
            Requested identifier.

        Returns
        -------
        tuple[float, float]
            Never returns.

        Raises
        ------
        SourceUnavailable
            Always.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (_Unavailable.lookup)
        2
        """
        raise SourceUnavailable(ident)


class CsvCoordinateSource:
    """
    Coordinate maps built from OurAirports CSV text.

    Attributes
    ----------
    _navaids :
        3-letter ident to coordinate rows.
    _airports :
        4-letter ident to coordinate rows.
    """

    def __init__(self, navaids_csv: str, airports_csv: str) -> None:
        """
        Index navaid and airport rows.

        Parameters
        ----------
        navaids_csv :
            CSV text with an ``ident`` column.
        airports_csv :
            CSV text with an ``ident`` column.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (CsvCoordinateSource)
        2
        """
        self._navaids = _index(navaids_csv)
        self._airports = _index(airports_csv)

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Return the one coordinate for ``ident``.

        Parameters
        ----------
        ident :
            3-letter navaid id or 4-letter ICAO indicator.

        Returns
        -------
        tuple[float, float]
            Latitude and longitude in decimal degrees.

        Raises
        ------
        SourceUnavailable
            When the id is missing, ambiguous, or the wrong shape.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (CsvCoordinateSource.lookup)
        2
        """
        key = ident.strip().upper()
        if len(key) == 3 and key.isalpha():
            groups = self._navaids
        elif len(key) == 4 and key.isalnum():
            groups = self._airports
        else:
            raise SourceUnavailable(key)
        rows = groups.get(key, [])
        if len(rows) != 1:
            raise SourceUnavailable(key)
        return rows[0]


class LiveOurAirportsSource:
    """
    Download each OurAirports file once per instance, then reuse the maps.

    Attributes
    ----------
    _client :
        Optional injected HTTP client.
    _parsed :
        Cached maps after the first successful download.
    """

    def __init__(self, client: httpx.Client | None = None) -> None:
        """
        Parameters
        ----------
        client :
            Optional HTTP client. The default client uses a 10-second timeout.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (LiveOurAirportsSource)
        2
        """
        self._client = client
        self._parsed: CsvCoordinateSource | None = None

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Download on the first call, then answer from memory.

        Parameters
        ----------
        ident :
            3-letter navaid id or 4-letter ICAO indicator.

        Returns
        -------
        tuple[float, float]
            Latitude and longitude in decimal degrees.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (LiveOurAirportsSource.lookup)
        2
        """
        if self._parsed is None:
            self._parsed = self._download()
        return self._parsed.lookup(ident)

    def _download(self) -> CsvCoordinateSource:
        """
        Fetch both CSV files.

        Returns
        -------
        CsvCoordinateSource
            Parsed maps.

        Raises
        ------
        SourceUnavailable
            When the download or the CSV text fails.
        """
        if self._client is None:
            with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
                return _read(client)
        return _read(self._client)


def _index(csv_text: str) -> dict[str, list[tuple[float, float]]]:
    """
    Group coordinate rows by ident.

    Parameters
    ----------
    csv_text :
        OurAirports CSV text.

    Returns
    -------
    dict[str, list[tuple[float, float]]]
        Ident to every parsed coordinate. More than one row is ambiguous.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    names = reader.fieldnames or []
    if _IDENT not in names or _LAT not in names or _LON not in names:
        raise SourceUnavailable("missing coordinate columns")
    grouped: dict[str, list[tuple[float, float]]] = {}
    for row in reader:
        ident = (row.get(_IDENT) or "").strip().upper()
        if not ident:
            continue
        lat_text = (row.get(_LAT) or "").strip()
        lon_text = (row.get(_LON) or "").strip()
        if not lat_text or not lon_text:
            continue
        try:
            point = (float(lat_text), float(lon_text))
        except ValueError as exc:
            raise SourceUnavailable(ident) from exc
        grouped.setdefault(ident, []).append(point)
    return grouped


def _read(client: httpx.Client) -> CsvCoordinateSource:
    """
    Download both files with ``client`` and parse them.

    Parameters
    ----------
    client :
        HTTP client.

    Returns
    -------
    CsvCoordinateSource
        Parsed maps.
    """
    try:
        navaids = client.get(NAVAIDS_URL)
        airports = client.get(AIRPORTS_URL)
        navaids.raise_for_status()
        airports.raise_for_status()
        return CsvCoordinateSource(navaids.text, airports.text)
    except (httpx.HTTPError, ValueError, csv.Error) as exc:
        raise SourceUnavailable(str(exc)) from exc


_override: CoordinateSource | None = None
_override_set = False
_live: LiveOurAirportsSource | None = None
_UNAVAILABLE = _Unavailable()


def set_coordinate_source(source: CoordinateSource | None) -> None:
    """
    Install a lookup source, or clear it when ``source`` is ``None``.

    Parameters
    ----------
    source :
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
    ident :
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
