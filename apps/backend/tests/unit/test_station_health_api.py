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
    set_station_health_store(store)
    with TestClient(api_module.app) as test_client:
        yield test_client
    set_station_health_store(StationHealthStore())


def test_tc_sh_001_list_and_metrics(client: TestClient) -> None:
    metrics = client.get("/api/v1/station-health/metrics")
    assert metrics.status_code == 200
    body = metrics.json()
    assert any(row["id"] == "availability" for row in body["metrics"])

    listed = client.get("/api/v1/station-health", params={"window": "6h"})
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["window"] == "6h"
    assert payload["summary"]["station_count"] >= 1
    assert payload["stations"][0]["icao"] == "KJFK"
    assert payload["stations"][0]["overall_grade"] in {"A", "B", "C", "D", "F"}
    assert payload["stations"][0]["products"]

    bad = client.get("/api/v1/station-health", params={"window": "2h"})
    assert bad.status_code == 400


def test_tc_sh_002_detail_and_unknown(client: TestClient) -> None:
    ok = client.get("/api/v1/station-health/KJFK")
    assert ok.status_code == 200
    detail = ok.json()
    assert detail["icao"] == "KJFK"
    assert "6h" in detail["windows"]
    assert detail["record_count"] >= 2

    missing = client.get("/api/v1/station-health/ZZZZ")
    assert missing.status_code == 404
    assert "Unknown" in missing.json()["detail"]
