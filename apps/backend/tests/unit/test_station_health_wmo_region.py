"""WMO region assignment for station health grades."""

from __future__ import annotations

import pytest
from src.services.station_health_wmo_region import (
    UNKNOWN_WMO_REGION,
    normalize_wmo_region,
    wmo_region_for_icao,
    wmo_region_for_iso_country,
    wmo_region_label,
)


@pytest.mark.parametrize(
    ("iso", "expected"),
    [
        ("US", "IV"),
        ("CA", "IV"),
        ("BR", "III"),
        ("GB", "VI"),
        ("DE", "VI"),
        ("AU", "V"),
        ("JP", "II"),
        ("ZA", "I"),
        ("ID", "V"),
        ("TR", "VI"),
        ("AQ", UNKNOWN_WMO_REGION),
        ("ZZ", UNKNOWN_WMO_REGION),
        (None, UNKNOWN_WMO_REGION),
        ("", UNKNOWN_WMO_REGION),
        ("usa", UNKNOWN_WMO_REGION),
    ],
)
def test_wmo_region_for_iso_country(iso: str | None, expected: str) -> None:
    assert wmo_region_for_iso_country(iso) == expected


@pytest.mark.parametrize(
    ("icao", "country", "expected"),
    [
        ("KJFK", None, "IV"),
        ("EGLL", None, "VI"),
        ("SBGR", None, "III"),
        ("YSSY", None, "V"),
        ("FAOR", None, "I"),
        ("RJTT", None, "II"),
        ("KJFK", "US", "IV"),
        ("ZZZZ", None, UNKNOWN_WMO_REGION),
        ("ABCD", "AQ", UNKNOWN_WMO_REGION),
    ],
)
def test_wmo_region_for_known_stations(
    icao: str,
    country: str | None,
    expected: str,
) -> None:
    assert wmo_region_for_icao(icao, country=country) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, None),
        ("", None),
        ("  ", None),
        ("iv", "IV"),
        ("IV", "IV"),
        ("unknown", "unknown"),
        ("UNKNOWN", "unknown"),
    ],
)
def test_normalize_wmo_region_success(raw: str | None, expected: str | None) -> None:
    assert normalize_wmo_region(raw) == expected


@pytest.mark.parametrize("raw", ["VII", "0", "africa", "RA-IV"])
def test_normalize_wmo_region_rejects_invalid(raw: str) -> None:
    with pytest.raises(ValueError, match="Region must be"):
        normalize_wmo_region(raw)


def test_wmo_region_label_unknown_fail_closed() -> None:
    assert wmo_region_label("unknown") == "Unknown region"
    assert wmo_region_label("not-a-region") == "Unknown region"
    assert "Africa" in wmo_region_label("I")
