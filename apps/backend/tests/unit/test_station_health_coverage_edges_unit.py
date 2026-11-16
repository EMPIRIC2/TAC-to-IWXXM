"""Additional station-health coverage edges (file-budget split)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from src.routers import station_health as router_mod
from src.services import station_health_aggregate as aggregate
from src.services.station_health_postgres import PostgresStationHealthStore
from src.services.station_health_store import StationHealthStore
from src.services.station_health_types import StationMeta, StationRecord


def test_issue_codes_json_and_detect_format_paths() -> None:
    assert aggregate._parse_issue_codes(None) == ()
    assert aggregate._parse_issue_codes("{bad") == ("{BAD",)
    assert aggregate._parse_issue_codes('["a","b"]') == ("A", "B")
    assert aggregate._parse_issue_codes('{"not":"list"}') == ()
    assert aggregate._parse_issue_codes(["x"]) == ("X",)
    assert aggregate._parse_issue_codes(("y",)) == ("Y",)
    assert aggregate._parse_issue_codes(123) == ()
    aware = datetime(2026, 11, 13, 12, 0, tzinfo=UTC)
    row = aggregate.row_to_station_record(
        {
            "icao": "KJFK",
            "product": "metar",
            "observed_at": aware,
            "ingested_at": aware,
            "tac_text": "METAR KJFK $=",
            "file_format": "  ",
            "maintenance_tags": ["$", "TSNO"],
        }
    )
    assert row.file_format in {"tac", "bulletin", "iwxxm_xml"}
    assert "$" in row.maintenance_tags
    row2 = aggregate.row_to_station_record(
        {
            "icao": "KJFK",
            "product": "metar",
            "observed_at": aware,
            "ingested_at": aware,
            "tac_text": "METAR KJFK=",
            "file_format": "",
            "maintenance_tags": "not-a-list",
        }
    )
    assert isinstance(row2.maintenance_tags, tuple)
    row3 = aggregate.row_to_station_record(
        {
            "icao": "KJFK",
            "product": "metar",
            "observed_at": aware,
            "ingested_at": aware,
            "tac_text": "METAR KJFK=",
            "file_format": "tac",
            "maintenance_tags": (),
        }
    )
    assert row3.file_format == "tac"


def test_centennial_edge_branches() -> None:
    from src.services import station_health_centennial as cen

    cont = cen.observing_continuity_metric(
        actual_count=2,
        expected_count=0,
        availability_score=None,
    )
    assert cont["status"] == "insufficient_data"
    assert cen.metadata_completeness_metric(None)["status"] == "insufficient_data"
    empty_meta = cen.metadata_completeness_metric(StationMeta(icao="KJFK"))
    assert empty_meta["status"] == "available"


def test_signals_cap_and_invalid_format_recount() -> None:
    from src.services.station_health_signals import (
        count_file_formats,
        normalize_issue_codes,
    )

    codes = normalize_issue_codes([f"C{i}" for i in range(80)])
    assert len(codes) == 64
    now = datetime.now(UTC)
    rows = [
        StationRecord(
            icao="KJFK",
            product="metar",
            observed_at=now,
            ingested_at=now,
            tac_text="METAR KJFK=",
            source="api",
            solidus_count=0,
            missing_digit_count=0,
            lint_error_count=0,
            lint_warning_count=0,
            convert_ok=True,
            character_count=10,
            file_format="nope",
        )
    ]
    formats = count_file_formats(rows)
    assert formats


def test_wmo_region_map_and_lookup_failures(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    import json as _json

    from src.services import station_health_wmo_region as wmo

    wmo._iso_to_region.cache_clear()
    bad = tmp_path / "bad.json"
    bad.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(wmo, "_DATA_PATH", bad)
    assert wmo._iso_to_region() == {}
    wmo._iso_to_region.cache_clear()

    good = tmp_path / "good.json"
    good.write_text(
        _json.dumps({"by_iso_country": {"US": "IV", "USA": "IV", "CA": 3, "": "IV"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(wmo, "_DATA_PATH", good)
    loaded = wmo._iso_to_region()
    assert loaded.get("US") == "IV"
    assert "USA" not in loaded
    wmo._iso_to_region.cache_clear()

    not_obj = tmp_path / "list.json"
    not_obj.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(wmo, "_DATA_PATH", not_obj)
    assert wmo._iso_to_region() == {}
    wmo._iso_to_region.cache_clear()

    no_map = tmp_path / "nomap.json"
    no_map.write_text(_json.dumps({"by_iso_country": "nope"}), encoding="utf-8")
    monkeypatch.setattr(wmo, "_DATA_PATH", no_map)
    assert wmo._iso_to_region() == {}
    wmo._iso_to_region.cache_clear()

    assert wmo.normalize_wmo_region(" ") is None
    assert wmo.normalize_wmo_region(123) is None
    assert wmo.wmo_region_for_icao("ABC") == "unknown"
    assert wmo.wmo_region_for_icao("") == "unknown"

    import src.schemas.airport as airport_mod

    def boom() -> None:
        raise RuntimeError("airport down")

    monkeypatch.setattr(airport_mod, "get_airport_validator", boom)
    assert wmo.wmo_region_for_icao("KJFK") == "unknown"


def test_postgres_old_observation_region_filter_and_purge() -> None:
    engine = MagicMock()
    store = PostgresStationHealthStore(engine)
    old = datetime.now(UTC) - timedelta(days=120)
    assert (
        store.record_observation(
            icao="KJFK",
            product="metar",
            tac_text="METAR KJFK=",
            source="t",
            observed_at=old,
        )
        is None
    )

    conn = MagicMock()
    connect_cm = MagicMock()
    connect_cm.__enter__.return_value = conn
    connect_cm.__exit__.return_value = None
    engine.connect.return_value = connect_cm
    station_result = MagicMock()
    station_result.mappings.return_value = [
        {"icao": "KJFK", "name": "JFK", "country": "US"},
        {"icao": "EGLL", "name": "LHR", "country": "GB"},
    ]
    record_result = MagicMock()
    record_result.mappings.return_value = []
    conn.execute.side_effect = [station_result, record_result]
    payload = store.list_stations(window_key="bad", region="unknown", grade="a", product=" METAR ", limit=10)
    assert payload["window"] == "6h"
    conn.execute.side_effect = [station_result, record_result]
    bare = store.list_stations(window_key="6h")
    assert bare["window"] == "6h"

    begin_cm = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm
    conn.execute.side_effect = None
    result = MagicMock()
    result.rowcount = 2
    conn.execute.return_value = result
    assert store.purge_expired() == 2
    begin_cm.__enter__.side_effect = RuntimeError("purge down")
    assert store.purge_expired() == 0


def test_memory_store_country_lookup_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    store = StationHealthStore()

    class _Airport:
        country = "USA"

    class _Validator:
        def get_airport(self, code: str) -> object:
            return _Airport()

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: _Validator())
    row = store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK=",
        source="t",
        name="JFK",
    )
    assert row is not None
    assert store._stations["KJFK"].country is None

    class _Airport2:
        country = "us"

    class _Validator2:
        def get_airport(self, code: str) -> object:
            return _Airport2()

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", lambda: _Validator2())
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK $=",
        source="t",
    )
    assert store._stations["KJFK"].country == "US"

    def boom() -> None:
        raise RuntimeError("lookup fail")

    monkeypatch.setattr("src.schemas.airport.get_airport_validator", boom)
    store.record_observation(
        icao="KLAX",
        product="metar",
        tac_text="METAR KLAX=",
        source="t",
    )
    assert "KLAX" in store._stations


def test_airport_validator_singleton_reuse() -> None:
    from src.schemas.airport import AirportValidator, get_airport_validator, reset_airport_validator_for_tests

    reset_airport_validator_for_tests()
    first = get_airport_validator()
    second = get_airport_validator()
    third = AirportValidator()
    assert first is second
    assert third is first
    reset_airport_validator_for_tests()
