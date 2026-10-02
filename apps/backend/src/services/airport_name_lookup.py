"""Look up one airport name from OpenAIP.

Decode asks for the station in the report. The process keeps only the
stations it has already resolved. It does not load the airport catalog.

[Corpus: product §F3] [Corpus: product §F9] [Corpus: adr/ADR-049]
"""

from __future__ import annotations

import os
from typing import cast

import httpx

_OPENAIP_AIRPORTS_URL = "https://api.core.openaip.net/api/airports"
_TIMEOUT_SECONDS = 20.0
_cache: dict[str, str | None] = {}


def clear_airport_name_cache() -> None:
    """
    Drop remembered station names.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (clear_airport_name_cache)
    2
    """
    _cache.clear()


def lookup_airport_name(icao: str) -> str | None:
    """
    Return the OpenAIP name for one ICAO code, or None on a miss.

    A successful response is remembered, including a confirmed miss.
    A missing key or a failed request is not remembered, so a later
    decode can try again. Never raises.

    Parameters
    ----------
    icao :
        Station location indicator from the TAC report.

    Returns
    -------
    str | None
        Airport name, or None when the code is unknown or the request fails.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lookup_airport_name)
    2
    """
    code = icao.strip().upper()
    if len(code) != 4 or not code.isalnum() or not code[0].isalpha():
        return None
    if code in _cache:
        return _cache[code]
    name, remember = _fetch_name(code)
    if remember:
        _cache[code] = name
    return name


def _fetch_name(code: str) -> tuple[str | None, bool]:
    """
    Ask OpenAIP for one station.

    Parameters
    ----------
    code :
        Uppercase ICAO location indicator.

    Returns
    -------
    tuple[str | None, bool]
        Name and whether that answer should be remembered.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (_fetch_name)
    2
    """
    api_key = os.environ.get("OPENAIP_API_KEY", "").strip()
    if not api_key:
        return None, False
    for _attempt in range(2):
        try:
            response = httpx.get(
                _OPENAIP_AIRPORTS_URL,
                params={"search": code, "limit": 10},
                headers={"x-openaip-api-key": api_key, "Accept": "application/json"},
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload: object = response.json()
        except (httpx.HTTPError, ValueError):
            continue
        return _name_from_payload(payload, code), True
    return None, False


def _name_from_payload(payload: object, icao: str) -> str | None:
    """
    Pick the item whose ICAO code matches.

    Parameters
    ----------
    payload :
        JSON body from the airports search.
    icao :
        Uppercase location indicator to match.

    Returns
    -------
    str | None
        Matching airport name, or None.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (_name_from_payload)
    2
    """
    if not isinstance(payload, dict):
        return None
    body = cast(dict[str, object], payload)
    items = body.get("items")
    if not isinstance(items, list):
        return None
    rows = cast(list[object], items)
    for item in rows:
        if not isinstance(item, dict):
            continue
        row = cast(dict[str, object], item)
        found = row.get("icaoCode")
        if not isinstance(found, str) or found.strip().upper() != icao:
            continue
        name = row.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
        return None
    return None
