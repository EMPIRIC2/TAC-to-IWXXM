"""Map point for one station ID (F3 / F7)."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient
from src import api as api_module


def test_station_point_returns_coordinates_for_a_known_icao(monkeypatch) -> None:
    # Other unit tests reload the shared airport catalog from a small fixture.
    airport = SimpleNamespace(
        icao="KJFK",
        name="John F Kennedy International Airport",
        coordinates=SimpleNamespace(latitude=40.64, longitude=-73.78),
    )
    monkeypatch.setattr(
        "src.routers.tac_quality.get_airport_validator",
        lambda: SimpleNamespace(get_airport=lambda _code: airport),
    )
    client = TestClient(api_module.app)
    response = client.get("/api/v1/stations/kjfk")
    assert response.status_code == 200
    body = response.json()
    assert body["icao"] == "KJFK"
    assert "Kennedy" in body["name"] or "KENNEDY" in body["name"].upper()
    assert 40 < body["latitude"] < 41
    assert -75 < body["longitude"] < -73


def test_station_point_misses_a_record_without_coordinates(monkeypatch) -> None:
    airport = SimpleNamespace(icao="ZZ99", name="Nowhere", coordinates=None)
    monkeypatch.setattr(
        "src.routers.tac_quality.get_airport_validator",
        lambda: SimpleNamespace(get_airport=lambda _code: airport),
    )
    client = TestClient(api_module.app)
    response = client.get("/api/v1/stations/ZZ99")
    assert response.status_code == 404


def test_station_point_misses_unknown_and_partial_codes() -> None:
    client = TestClient(api_module.app)
    assert client.get("/api/v1/stations/ZZ99").status_code == 404
    assert client.get("/api/v1/stations/T").status_code == 404
    assert client.get("/api/v1/stations/1JFK").status_code == 404
    assert client.get("/api/v1/stations/KJ-K").status_code == 404
    assert client.get("/api/v1/stations/ZZ99").json()["detail"] == "Station not found"
