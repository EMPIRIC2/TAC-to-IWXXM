"""Live OpenAIP station-name checks.

[Corpus: product §F3] [Corpus: product §F9] [Corpus: tests]

A few known stations must resolve, and an unknown code must stay empty.
GitHub Actions fails this job when OPENAIP_API_KEY is missing.
Upstream OpenAIP 5xx / transport failures skip (vendor outage) so CI/CD is
not blocked when the live API is down — missing key still fails closed.
"""

from __future__ import annotations

import os

import httpx
import pytest
from src.services.airport_name_lookup import clear_airport_name_cache, lookup_airport_name

_KNOWN = (
    ("KJFK", "KENNEDY"),
    ("EGLL", "HEATHROW"),
    ("YSSY", "SYDNEY"),
)
_OPENAIP_AIRPORTS_URL = "https://api.core.openaip.net/api/airports"


@pytest.fixture(autouse=True)
def _fresh_cache() -> None:
    clear_airport_name_cache()


def _openaip_upstream_ok(api_key: str) -> bool:
    """True when OpenAIP answers without a 5xx / transport error."""
    headers = {"x-openaip-api-key": api_key, "Accept": "application/json"}
    for _ in range(3):
        try:
            response = httpx.get(
                _OPENAIP_AIRPORTS_URL,
                params={"search": "KJFK", "limit": 1},
                headers=headers,
                timeout=20.0,
            )
        except httpx.HTTPError:
            continue
        if response.status_code >= 500:
            continue
        return True
    return False


@pytest.mark.live_api
def test_openaip_resolves_known_stations_and_misses_unknown() -> None:
    key = os.environ.get("OPENAIP_API_KEY", "").strip()
    if not key:
        if os.environ.get("CI"):
            pytest.fail("OPENAIP_API_KEY is required in CI")
        pytest.skip("OPENAIP_API_KEY is not set")
    if not _openaip_upstream_ok(key):
        pytest.skip("OpenAIP API unavailable (upstream 5xx or transport error)")
    for icao, needle in _KNOWN:
        name = lookup_airport_name(icao)
        assert name is not None, icao
        assert needle in name.upper(), (icao, name)
    assert lookup_airport_name("ZZ99") is None
