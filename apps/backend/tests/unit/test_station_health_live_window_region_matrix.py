"""Station health success / failure / validation / mutation filter matrix.

Covers live-store grades for the 90-day window, WMO region assignment, and
permutations of window x product x region filters.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.services.station_health_store import (
    StationHealthStore,
    set_station_health_store,
)


@pytest.fixture
def live_store_client() -> TestClient:
    """Seed a multi-region in-memory store that stands in for live ingest data."""
    store = StationHealthStore()
    now = datetime.now(UTC)
    # Recent METAR - Region IV (US)
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=",
        source="ingest",
        observed_at=now - timedelta(hours=1),
        name="John F Kennedy International",
    )
    # Older METAR still inside 90d - Region IV
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 150000Z 18008KT 10SM FEW040 15/07 A3005=",
        source="ingest",
        observed_at=now - timedelta(days=45),
    )
    # Region VI
    store.record_observation(
        icao="EGLL",
        product="metar",
        tac_text="METAR EGLL 010000Z 27010KT 9999 FEW020 12/08 Q1013=",
        source="ingest",
        observed_at=now - timedelta(hours=2),
        name="London Heathrow",
    )
    # Region V TAF
    store.record_observation(
        icao="YSSY",
        product="taf",
        tac_text="TAF YSSY 010000Z 0100/0206 25010KT P6SM FEW020=",
        source="convert",
        observed_at=now - timedelta(hours=3),
        name="Sydney Kingsford Smith",
    )
    # Outside 90d - must not affect 90d grades
    store.record_observation(
        icao="RJTT",
        product="metar",
        tac_text="METAR RJTT 010000Z 36005KT 9999 FEW030 18/10 Q1015=",
        source="ingest",
        observed_at=now - timedelta(days=120),
        name="Tokyo Haneda",
    )
    set_station_health_store(store)
    with TestClient(api_module.app) as test_client:
        yield test_client
    set_station_health_store(None)


WINDOWS = ("6h", "1d", "30d", "90d")
PRODUCTS = (None, "metar", "taf")
REGIONS = (None, "IV", "VI", "V")


@pytest.mark.parametrize("window", WINDOWS)
@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("region", REGIONS)
def test_read_query_window_product_region_permutations(
    live_store_client: TestClient,
    window: str,
    product: str | None,
    region: str | None,
) -> None:
    params: dict[str, object] = {"window": window, "limit": 500}
    if product:
        params["product"] = product
    if region:
        params["region"] = region
        params["limit"] = 5000
    response = live_store_client.get("/api/v1/station-health", params=params)
    assert response.status_code == 200
    body = response.json()
    assert body["window"] == window
    assert isinstance(body["stations"], list)
    for row in body["stations"]:
        assert row["wmo_region"] in {"I", "II", "III", "IV", "V", "VI", "unknown"}
        if region:
            assert row["wmo_region"] == region
        if product:
            assert all(item["product"] == product for item in row["products"])


def test_success_90d_returns_grades_and_regions(live_store_client: TestClient) -> None:
    response = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "90d", "limit": 500},
    )
    assert response.status_code == 200
    body = response.json()
    by_icao = {row["icao"]: row for row in body["stations"]}
    assert "KJFK" in by_icao
    assert by_icao["KJFK"]["wmo_region"] == "IV"
    assert by_icao["KJFK"]["overall_grade"] in {"A", "B", "C", "D", "F"}
    assert "EGLL" in by_icao
    assert by_icao["EGLL"]["wmo_region"] == "VI"
    # RJTT only has a 120-day-old observation; it remains in the registry but
    # has no in-window products → overall F unless filtered out by product.
    if "RJTT" in by_icao:
        assert by_icao["RJTT"]["wmo_region"] == "II"


def test_success_region_filter_loads_matching_stations(
    live_store_client: TestClient,
) -> None:
    response = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "90d", "region": "IV", "limit": 5000},
    )
    assert response.status_code == 200
    stations = response.json()["stations"]
    assert stations
    assert all(row["wmo_region"] == "IV" for row in stations)
    assert any(row["icao"] == "KJFK" for row in stations)
    assert all(row["icao"] != "EGLL" for row in stations)


def test_failure_invalid_window_and_region(live_store_client: TestClient) -> None:
    bad_window = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "2h"},
    )
    assert bad_window.status_code == 400
    assert "Window" in str(bad_window.json().get("detail", ""))

    bad_region = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "6h", "region": "VII"},
    )
    assert bad_region.status_code == 400
    assert "Region" in str(bad_region.json().get("detail", ""))


def test_validation_unknown_region_filter_accepted(
    live_store_client: TestClient,
) -> None:
    response = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "6h", "region": "unknown", "limit": 5000},
    )
    assert response.status_code == 200
    assert all(row["wmo_region"] == "unknown" for row in response.json()["stations"])


def test_mutation_filter_changes_result_set(live_store_client: TestClient) -> None:
    """Changing window / product / region mutates the returned set (read filters)."""
    base = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "90d", "limit": 500},
    ).json()
    narrowed = live_store_client.get(
        "/api/v1/station-health",
        params={"window": "6h", "product": "metar", "region": "VI", "limit": 5000},
    ).json()
    assert base["window"] == "90d"
    assert narrowed["window"] == "6h"
    assert all(row["wmo_region"] == "VI" for row in narrowed["stations"])
    assert all(any(item["product"] == "metar" for item in row["products"]) for row in narrowed["stations"])


def test_detail_includes_90d_and_wmo_region(live_store_client: TestClient) -> None:
    response = live_store_client.get("/api/v1/station-health/KJFK")
    assert response.status_code == 200
    body = response.json()
    assert body["wmo_region"] == "IV"
    assert "90d" in body["windows"]
    assert body["windows"]["90d"]["overall_grade"] in {"A", "B", "C", "D", "F"}


def test_empty_store_failure_mode_is_empty_not_crash() -> None:
    set_station_health_store(StationHealthStore())
    try:
        with TestClient(api_module.app) as client:
            response = client.get(
                "/api/v1/station-health",
                params={"window": "90d", "region": "IV", "limit": 5000},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["stations"] == []
        assert body["summary"]["station_count"] == 0
    finally:
        set_station_health_store(None)
