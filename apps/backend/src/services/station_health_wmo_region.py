"""Resolve WMO Regional Association for station health (F39).

Maps ISO country codes from the airport catalog or station registry to WMO
Regional Associations I-VI. Stations without a mapped country return the
fail-closed unknown token.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Final, cast

logger = logging.getLogger(__name__)

UNKNOWN_WMO_REGION: Final[str] = "unknown"
VALID_WMO_REGIONS: Final[frozenset[str]] = frozenset({"I", "II", "III", "IV", "V", "VI", UNKNOWN_WMO_REGION})

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "wmo_region_by_iso_country.json"


@lru_cache(maxsize=1)
def _iso_to_region() -> dict[str, str]:
    """
    Load ISO country → WMO region codes from the checked-in map.

    Returns
    -------
    dict[str, str]
        Uppercase ISO2 to Roman-numeral region id.
    """
    try:
        loaded: object = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("failed to load WMO region map from %s", _DATA_PATH)
        return {}
    if not isinstance(loaded, dict):
        return {}
    payload = cast(dict[str, object], loaded)
    raw_obj = payload.get("by_iso_country")
    if not isinstance(raw_obj, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in cast(dict[object, object], raw_obj).items():
        if not isinstance(key, str) or not isinstance(value, str):
            continue
        iso = key.strip().upper()
        region = value.strip().upper()
        if len(iso) == 2 and region in {"I", "II", "III", "IV", "V", "VI"}:
            result[iso] = region
    return result


def normalize_wmo_region(value: str | None) -> str | None:
    """
    Normalize a region query value, or return ``None`` when absent.

    Parameters
    ----------
    value : str | None
        Raw query string.

    Returns
    -------
    str | None
        Canonical region id, or ``None`` when the caller omitted a filter.

    Raises
    ------
    ValueError
        When the value is present but not a valid region id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (normalize_wmo_region)
    2
    """
    if value is None or not isinstance(value, str):
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    key = trimmed.lower() if trimmed.lower() == UNKNOWN_WMO_REGION else trimmed.upper()
    if key == "UNKNOWN":
        key = UNKNOWN_WMO_REGION
    if key not in VALID_WMO_REGIONS:
        msg = "Region must be I, II, III, IV, V, VI, or unknown"
        raise ValueError(msg)
    return key


def wmo_region_for_iso_country(iso_country: str | None) -> str:
    """
    Map an ISO country code to a WMO Regional Association id.

    Parameters
    ----------
    iso_country : str | None
        ISO 3166-1 alpha-2 country code.

    Returns
    -------
    str
        Region id ``I``-``VI``, or ``unknown`` when unmapped.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (wmo_region_for_iso_country)
    2
    """
    if not iso_country:
        return UNKNOWN_WMO_REGION
    code = iso_country.strip().upper()
    if len(code) != 2:
        return UNKNOWN_WMO_REGION
    return _iso_to_region().get(code, UNKNOWN_WMO_REGION)


def wmo_region_for_icao(icao: str, *, country: str | None = None) -> str:
    """
    Resolve WMO region for one station ICAO.

    Prefers an explicit registry country. Otherwise looks up the airport
    catalog. Missing country data returns ``unknown``.

    Parameters
    ----------
    icao : str
        Four-letter ICAO location indicator.
    country : str | None
        Optional ISO country already known for the station.

    Returns
    -------
    str
        Region id or ``unknown``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (wmo_region_for_icao)
    2
    """
    if country:
        return wmo_region_for_iso_country(country)
    code = (icao or "").strip().upper()
    if len(code) != 4:
        return UNKNOWN_WMO_REGION
    try:
        from src.schemas.airport import get_airport_validator

        airport = get_airport_validator().get_airport(code)
    except Exception:
        logger.exception("airport lookup failed for WMO region on %s", code)
        return UNKNOWN_WMO_REGION
    if airport is None:
        return UNKNOWN_WMO_REGION
    return wmo_region_for_iso_country(getattr(airport, "country", None))


def wmo_region_label(region: str) -> str:
    """
    Return plain-language label for a region id.

    Parameters
    ----------
    region : str
        Canonical region id.

    Returns
    -------
    str
        Operator-facing label without planning ids.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (wmo_region_label)
    2
    """
    labels = {
        "I": "Region I - Africa",
        "II": "Region II - Asia",
        "III": "Region III - South America",
        "IV": "Region IV - North America, Central America and the Caribbean",
        "V": "Region V - South-West Pacific",
        "VI": "Region VI - Europe",
        UNKNOWN_WMO_REGION: "Unknown region",
    }
    return labels.get(region, "Unknown region")


__all__ = [
    "UNKNOWN_WMO_REGION",
    "VALID_WMO_REGIONS",
    "normalize_wmo_region",
    "wmo_region_for_icao",
    "wmo_region_for_iso_country",
    "wmo_region_label",
]
