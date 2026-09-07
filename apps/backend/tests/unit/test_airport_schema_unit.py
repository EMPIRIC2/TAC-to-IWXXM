"""Unit tests for src.schemas.airport."""

from __future__ import annotations

import json

import pytest
from src.schemas import airport as airport_schema


def test_airport_model_normalizes_icao_and_iata():
    airport = airport_schema.Airport(
        icao="kjfk",
        iata="jfk",
        name="John F Kennedy International Airport",
        type="large_airport",
    )

    assert airport.icao == "KJFK"
    assert airport.iata == "JFK"


def test_airport_model_rejects_invalid_icao_and_iata():
    with pytest.raises(ValueError, match=r".*"):
        airport_schema.Airport(icao="bad", iata="JFK", name="X", type="large_airport")

    with pytest.raises(ValueError, match=r".*"):
        airport_schema.Airport(icao="KJFK", iata="TOOLONG", name="X", type="large_airport")


def test_airport_model_rejects_invalid_icao_pattern_with_length_four():
    with pytest.raises(ValueError, match=r".*"):
        airport_schema.Airport(icao="KJ$%", iata="JFK", name="X", type="large_airport")


def test_airport_model_accepts_explicit_none_iata():
    airport = airport_schema.Airport(
        icao="KJFK",
        iata=None,
        name="John F Kennedy International Airport",
        type="large_airport",
    )

    assert airport.iata is None


def test_airport_model_rejects_invalid_iata_pattern_with_length_three():
    with pytest.raises(ValueError, match=r".*"):
        airport_schema.Airport(icao="KJFK", iata="J$K", name="X", type="large_airport")


def test_airport_validator_load_and_lookup(tmp_path, monkeypatch):
    airports_path = tmp_path / "backend" / "src" / "data"
    airports_path.mkdir(parents=True)
    (airports_path / "airports.json").write_text(
        json.dumps(
            [
                {
                    "icao": "KJFK",
                    "iata": "JFK",
                    "name": "John F Kennedy International Airport",
                    "city": "New York",
                    "country": "United States",
                    "type": "large_airport",
                    "coordinates": {
                        "latitude": 40.6397,
                        "longitude": -73.7789,
                        "elevation_ft": 13,
                    },
                },
                {
                    "icao": "EGLL",
                    "name": "Heathrow",
                    "city": "London",
                    "country": "United Kingdom",
                    "type": "large_airport",
                },
            ]
        ),
        encoding="utf-8",
    )

    fake_file = tmp_path / "backend" / "src" / "schemas" / "airport.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# test")
    monkeypatch.setattr(airport_schema, "__file__", str(fake_file))

    validator = airport_schema.AirportValidator()
    validator._loaded = False
    validator.load_airports()

    assert validator.count() == 2
    assert validator.validate_icao("KJFK") is True
    assert validator.validate_icao("kjfk") is True
    assert validator.validate_icao("KJ1K") is False
    assert validator.validate_icao("ABCDE") is False
    assert validator.get_airport("EGLL") is not None
    assert validator.get_airport("") is None


def test_airport_validator_search_helpers_and_all_airports(tmp_path, monkeypatch):
    airports_path = tmp_path / "backend" / "src" / "data"
    airports_path.mkdir(parents=True)
    (airports_path / "airports.json").write_text(
        json.dumps(
            [
                {
                    "icao": "KJFK",
                    "name": "John F Kennedy International Airport",
                    "city": "New York",
                    "type": "large_airport",
                },
                {
                    "icao": "KLAX",
                    "name": "Los Angeles International Airport",
                    "city": "Los Angeles",
                    "type": "large_airport",
                },
                {
                    "icao": "EGLL",
                    "name": "Heathrow",
                    "city": "London",
                    "type": "large_airport",
                },
            ]
        ),
        encoding="utf-8",
    )

    fake_file = tmp_path / "backend" / "src" / "schemas" / "airport.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# test")
    monkeypatch.setattr(airport_schema, "__file__", str(fake_file))

    validator = airport_schema.AirportValidator()
    validator._loaded = False
    validator.load_airports()

    assert [a.icao for a in validator.search_by_prefix("K")] == ["KJFK", "KLAX"]
    assert validator.search_by_prefix("") == []

    by_name = validator.search_by_name("international")
    assert {a.icao for a in by_name} == {"KJFK", "KLAX"}
    assert validator.search_by_name("") == []

    all_airports = validator.get_all_airports()
    assert len(all_airports) == 3


def test_get_airport_validator_singleton(monkeypatch):
    original = airport_schema._validator_instance
    try:
        airport_schema._validator_instance = None
        first = airport_schema.get_airport_validator()
        second = airport_schema.get_airport_validator()
        assert first is second
    finally:
        airport_schema._validator_instance = original


def test_airport_coordinates_defaults_and_bounds():
    coords = airport_schema.AirportCoordinates(latitude=10.0, longitude=20.0)
    assert coords.vertical_datum == "EGM_96"

    coords_negative = airport_schema.AirportCoordinates(
        latitude=-10.0,
        longitude=-20.0,
        elevation_ft=-1500,
    )
    assert coords_negative.elevation_ft == -1500

    with pytest.raises(ValueError, match=r".*"):
        airport_schema.AirportCoordinates(latitude=91.0, longitude=0.0)

    with pytest.raises(ValueError, match=r".*"):
        airport_schema.AirportCoordinates(latitude=0.0, longitude=181.0)


def test_airport_validator_skips_invalid_entries(tmp_path, monkeypatch):
    airports_path = tmp_path / "backend" / "src" / "data"
    airports_path.mkdir(parents=True)
    (airports_path / "airports.json").write_text(
        json.dumps(
            [
                {
                    "icao": "KJFK",
                    "name": "John F Kennedy International Airport",
                    "city": "New York",
                    "country": "United States",
                    "type": "large_airport",
                },
                {
                    "icao": "BAD",
                    "name": "Broken Airport",
                    "city": "Nowhere",
                    "country": "N/A",
                    "type": "small_airport",
                },
            ]
        ),
        encoding="utf-8",
    )

    fake_file = tmp_path / "backend" / "src" / "schemas" / "airport.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# test")
    monkeypatch.setattr(airport_schema, "__file__", str(fake_file))

    validator = airport_schema.AirportValidator()
    validator._loaded = False
    validator.load_airports()

    assert validator.count() == 1
    assert validator.get_airport("KJFK") is not None
    assert validator.get_airport("BAD") is None


def test_airport_validator_load_raises_when_airports_file_missing(tmp_path, monkeypatch):
    fake_file = tmp_path / "backend" / "src" / "schemas" / "airport.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.write_text("# test")
    monkeypatch.setattr(airport_schema, "__file__", str(fake_file))

    validator = airport_schema.AirportValidator()
    validator._loaded = True

    with pytest.raises(FileNotFoundError, match=r".*"):
        validator.load_airports()


def test_validate_icao_returns_false_for_empty_input():
    validator = airport_schema.AirportValidator()
    validator._airports = {"KJFK": airport_schema.Airport(icao="KJFK", name="JFK", type="large_airport")}

    assert validator.validate_icao("") is False
