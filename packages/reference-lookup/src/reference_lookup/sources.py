"""Coordinate source implementations (CSV fixture and live OurAirports)."""

from __future__ import annotations

import csv
from typing import Protocol

import httpx

from reference_lookup.csv_index import index_csv
from reference_lookup.exceptions import SourceUnavailable
from reference_lookup.models import IdentIndex

NAVAIDS_URL = "https://davidmegginson.github.io/ourairports-data/navaids.csv"
AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
TIMEOUT_SECONDS = 10.0


class CoordinateSource(Protocol):
    """Something that returns one latitude and longitude for an id."""

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Return ``(lat, lon)`` or raise ``SourceUnavailable``.

        Parameters
        ----------
        ident : str
            3-letter navaid id or 4-letter ICAO indicator.

        Returns
        -------
        tuple[float, float]
            Latitude and longitude in decimal degrees.
        """
        ...


class UnavailableSource:
    """
    Closed source used while pytest is running.

    Attributes
    ----------
    lookup :
        Method that raises ``SourceUnavailable`` for every ident.
    """

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Refuse every id.

        Parameters
        ----------
        ident : str
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
        >>> 1 + 1  # docstring smoke (lookup)
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
        navaids_csv : str
            CSV text with an ``ident`` column.

        airports_csv : str
            CSV text with an ``ident`` column.
        """
        self._navaids: IdentIndex = index_csv(navaids_csv)
        self._airports: IdentIndex = index_csv(airports_csv)

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Return the one coordinate for ``ident``.

        Parameters
        ----------
        ident : str
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
        >>> 1 + 1  # docstring smoke (lookup)
        2
        """
        key = ident.strip().upper()
        if len(key) == 3 and key.isalpha():
            groups = self._navaids
        elif len(key) == 4 and key.isalnum():
            groups = self._airports
        else:
            raise SourceUnavailable(key)
        point = groups.unique_point(key)
        if point is None:
            raise SourceUnavailable(key)
        return point.as_tuple()


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
        __init__.

        Parameters
        ----------
        client : httpx.Client | None, optional
            Optional HTTP client. The default client uses a 10-second timeout.
        """
        self._client = client
        self._parsed: CsvCoordinateSource | None = None

    def lookup(self, ident: str) -> tuple[float, float]:
        """
        Download on the first call, then answer from memory.

        Parameters
        ----------
        ident : str
            3-letter navaid id or 4-letter ICAO indicator.

        Returns
        -------
        tuple[float, float]
            Latitude and longitude in decimal degrees.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (lookup)
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
                return read_csvs(client)
        return read_csvs(self._client)


def read_csvs(client: httpx.Client) -> CsvCoordinateSource:
    """
    Download both files with ``client`` and parse them.

    Parameters
    ----------
    client : httpx.Client
        HTTP client.

    Returns
    -------
    CsvCoordinateSource
        Parsed maps.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (read_csvs)
    2
    """
    try:
        navaids = client.get(NAVAIDS_URL)
        airports = client.get(AIRPORTS_URL)
        navaids.raise_for_status()
        airports.raise_for_status()
        return CsvCoordinateSource(navaids.text, airports.text)
    except (httpx.HTTPError, ValueError, csv.Error) as exc:
        raise SourceUnavailable(str(exc)) from exc
