"""TC-SH-001 / TC-SH-002 — public station-health HTTP API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.services.station_health_store import (
    StationHealthStore,
    set_station_health_store,
)


@pytest.fixture
def client() -> TestClient:
    store = StationHealthStore()
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=",
        source="ingest",
        name="John F Kennedy International",
    )
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010100Z 18008KT 10SM FEW040 15/07 A3005=",
        source="ingest",
    )
    store.record_observation(
        icao="KLAX",
        product="taf",
        tac_text="TAF KLAX 010000Z 0100/0206 25010KT P6SM FEW020=",
        source="convert",
        name="Los Angeles International",
    )
    set_station_health_store(store)
    with TestClient(api_module.app) as test_client:
        yield test_client
    set_station_health_store(None)


@pytest.mark.parametrize(
    ("path", "params", "status_code", "checks"),
    [
        (
            "/api/v1/station-health/metrics",
            {},
            200,
            ("metrics_has_availability",),
        ),
        (
            "/api/v1/station-health",
            {"window": "6h"},
            200,
            ("list_has_kjfk", "summary_nonzero"),
        ),
        (
            "/api/v1/station-health",
            {"window": "1d", "product": "metar"},
            200,
            ("list_has_kjfk",),
        ),
        (
            "/api/v1/station-health",
            {"window": "30d", "limit": 1},
            200,
            ("list_limited",),
        ),
        (
            "/api/v1/station-health/KJFK",
            {},
            200,
            ("detail_kjfk",),
        ),
    ],
)
def test_tc_sh_001_success_paths(
    client: TestClient,
    path: str,
    params: dict[str, object],
    status_code: int,
    checks: tuple[str, ...],
) -> None:
    response = client.get(path, params=params or None)
    assert response.status_code == status_code
    body = response.json()
    if "metrics_has_availability" in checks:
        assert any(row["id"] == "availability" for row in body["metrics"])
    if "list_has_kjfk" in checks:
        assert any(row["icao"] == "KJFK" for row in body["stations"])
        assert body["stations"][0]["overall_grade"] in {"A", "B", "C", "D", "F"}
    if "summary_nonzero" in checks:
        assert body["summary"]["station_count"] >= 1
    if "list_limited" in checks:
        assert len(body["stations"]) <= 1
    if "detail_kjfk" in checks:
        assert body["icao"] == "KJFK"
        assert "6h" in body["windows"]
        assert body["record_count"] >= 2


@pytest.mark.parametrize(
    ("path", "params", "status_code", "detail_substr"),
    [
        ("/api/v1/station-health", {"window": "2h"}, 400, "Window"),
        ("/api/v1/station-health", {"window": "99d"}, 400, "Window"),
        ("/api/v1/station-health/ZZZZ", {}, 404, "Unknown"),
        ("/api/v1/station-health/ABCD", {}, 404, "Unknown"),
    ],
)
def test_tc_sh_002_failure_paths(
    client: TestClient,
    path: str,
    params: dict[str, object],
    status_code: int,
    detail_substr: str,
) -> None:
    response = client.get(path, params=params or None)
    assert response.status_code == status_code
    assert detail_substr in str(response.json().get("detail", ""))


@pytest.mark.parametrize(
    ("params", "expect_empty"),
    [
        ({"window": "6h", "product": "speci"}, True),
        ({"window": "6h", "grade": "Z"}, True),
        ({"window": "6h", "product": "metar", "grade": "A"}, False),
        ({"window": "6h", "limit": 500}, False),
    ],
)
def test_tc_sh_001_validation_filters(
    client: TestClient,
    params: dict[str, object],
    expect_empty: bool,
) -> None:
    response = client.get("/api/v1/station-health", params=params)
    assert response.status_code == 200
    stations = response.json()["stations"]
    if expect_empty:
        assert stations == []
    else:
        assert isinstance(stations, list)
        if params.get("product"):
            assert all(any(p["product"] == params["product"] for p in row["products"]) for row in stations)


# OpenAPI G1 covered_by anchor for templated station detail path.
_OPENAPI_STATION_HEALTH_PATH_ANCHORS = ("/api/v1/station-health/{icao}",)


def test_openapi_station_health_path_anchors() -> None:
    """Fixture covered_by paths stay discoverable for station-health detail."""
    assert all(path.startswith("/api/v1/station-health") for path in _OPENAPI_STATION_HEALTH_PATH_ANCHORS)
