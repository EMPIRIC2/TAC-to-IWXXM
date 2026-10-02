"""Live OpenAIP station-name checks.

[Corpus: product §F3] [Corpus: product §F9] [Corpus: tests]

A few known stations must resolve, and an unknown code must stay empty.
GitHub Actions fails this job when OPENAIP_API_KEY is missing.
"""

from __future__ import annotations

import os

import pytest
from src.services.airport_name_lookup import clear_airport_name_cache, lookup_airport_name

_KNOWN = (
    ("KJFK", "KENNEDY"),
    ("EGLL", "HEATHROW"),
    ("YSSY", "SYDNEY"),
)


@pytest.fixture(autouse=True)
def _fresh_cache() -> None:
    clear_airport_name_cache()


@pytest.mark.live_api
def test_openaip_resolves_known_stations_and_misses_unknown() -> None:
    key = os.environ.get("OPENAIP_API_KEY", "").strip()
    if not key:
        if os.environ.get("CI"):
            pytest.fail("OPENAIP_API_KEY is required in CI")
        pytest.skip("OPENAIP_API_KEY is not set")
    for icao, needle in _KNOWN:
        name = lookup_airport_name(icao)
        assert name is not None, icao
        assert needle in name.upper(), (icao, name)
    assert lookup_airport_name("ZZ99") is None
