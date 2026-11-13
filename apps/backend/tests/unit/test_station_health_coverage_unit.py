"""Fill station-health unit coverage gaps (no skips)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from src.routers import station_health as router_mod
from src.services import station_health_aggregate as aggregate
from src.services import station_health_metrics as metrics
from src.services import station_health_recorder as recorder
from src.services.station_health_postgres import PostgresStationHealthStore, sync_database_url
from src.services.station_health_store import (
    StationHealthStore,
    get_station_health_store,
    set_station_health_store,
)
from src.services.station_health_types import StationRecord


def test_router_coercion_helpers_cover_branches() -> None:
    assert router_mod._as_str(None, "d") == "d"
    assert router_mod._as_str(7) == "7"
    assert router_mod._as_float(None) == 0.0
    assert router_mod._as_float(True) == 0.0
    assert router_mod._as_float(1.5) == 1.5
    assert router_mod._as_float("2.5") == 2.5
    assert router_mod._as_float("nope") == 0.0
    assert router_mod._as_float(object()) == 0.0
    assert router_mod._as_int(None) == 0
    assert router_mod._as_int(True) == 0
    assert router_mod._as_int(3) == 3
    assert router_mod._as_int(4.9) == 4
    assert router_mod._as_int("9") == 9
    assert router_mod._as_int("x") == 0
    assert router_mod._as_int(object()) == 0
    assert router_mod._as_optional_str(None) is None
    assert router_mod._as_optional_str(1) == "1"
    assert router_mod._product_dict("x") is None
    assert router_mod._product_dict({"product": "METAR"})["product"] == "METAR"
    assert router_mod._products_from_raw("nope") == []
    assert router_mod._products_from_raw([{"product": "METAR"}, "skip"]) == [{"product": "METAR"}]
    models = router_mod._product_models([{"product": "metar", "grade": "A"}])
    assert models[0].product == "metar"


def test_router_list_and_detail_tolerate_malformed_payloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _WeirdStore:
        def list_metrics(self) -> list[dict[str, Any]]:
            return [{"id": "availability", "label": "A", "description": "d"}]

        def list_stations(self, **_kwargs: Any) -> dict[str, Any]:
            return {
                "window": "6h",
                "computed_at": "t",
                "stations": ["bad", {"icao": "KJFK", "products": "bad"}],
                "summary": "bad",
            }

        def get_station(self, icao: str) -> dict[str, Any] | None:
            return {
                "icao": icao,
                "name": None,
                "windows": {"6h": "bad", "1d": {"overall_grade": "A", "products": []}},
                "record_count": 1,
            }

    monkeypatch.setattr(router_mod, "get_station_health_store", lambda: _WeirdStore())
    listed = router_mod.list_station_health(window="6h", product=None, grade=None, limit=100)
    assert listed.stations[0].icao == "KJFK"
    assert listed.summary.station_count == 0
    detail = router_mod.get_station_health("KJFK")
    assert "1d" in detail.windows
    assert "6h" not in detail.windows

    class _NonCollectionStore:
        def list_metrics(self) -> list[dict[str, Any]]:
            return []

        def list_stations(self, **_kwargs: Any) -> dict[str, Any]:
            return {
                "window": "6h",
                "computed_at": "t",
                "stations": "not-a-list",
                "summary": {"station_count": 0, "grade_counts": "bad"},
            }

        def get_station(self, icao: str) -> dict[str, Any] | None:
            return {
                "icao": icao,
                "name": None,
                "windows": "not-a-dict",
                "record_count": 0,
            }

    monkeypatch.setattr(router_mod, "get_station_health_store", lambda: _NonCollectionStore())
    empty_list = router_mod.list_station_health(window="6h", product=None, grade=None, limit=100)
    assert empty_list.stations == []
    empty_detail = router_mod.get_station_health("KJFK")
    assert empty_detail.windows == {}


def test_aggregate_naive_timestamps_and_empty_overall() -> None:
    naive = datetime(2026, 11, 13, 12, 0)
    row = aggregate.row_to_station_record(
        {
            "icao": "kjfk",
            "product": "METAR",
            "observed_at": naive,
            "ingested_at": naive,
            "tac_text": "METAR KJFK=",
            "source": "ingest",
        }
    )
    assert row.observed_at.tzinfo is UTC
    assert row.ingested_at.tzinfo is UTC
    assert aggregate.overall_from_products([])["overall_grade"] == "F"


def test_metrics_expected_availability_lint_and_window_errors() -> None:
    assert metrics.expected_count_for_window("metar", "nope") == 0
    assert metrics.expected_count_for_window("unknown", "6h") == 0
    assert metrics.availability_score(0, 0, irregular=True) == 0.0
    assert metrics.availability_score(1, 0, irregular=True) == 70.0
    assert metrics.availability_score(2, 0, irregular=True) == 85.0
    assert metrics.availability_score(3, 0, irregular=True) == 100.0
    assert metrics.availability_score(0, 0, irregular=False) == 0.0
    assert metrics.availability_score(1, 0, irregular=False) == 100.0
    assert metrics.lint_severity_score(0, 0, 0) == 100.0
    with pytest.raises(ValueError, match="unknown window"):
        metrics.window_timedelta("nope")


def test_recorder_extract_and_invalid_icao(monkeypatch: pytest.MonkeyPatch) -> None:
    set_station_health_store(StationHealthStore())
    monkeypatch.setattr(recorder, "extract_station_icao", lambda *_a, **_k: "KJFK")
    out = recorder.record_tac_observation(
        tac_text="METAR KJFK 010000Z=",
        product="METAR",
        source="convert",
    )
    assert out is not None
    assert out["icao"] == "KJFK"

    def _boom(*_a: Any, **_k: Any) -> str:
        raise RuntimeError("parse fail")

    monkeypatch.setattr(recorder, "extract_station_icao", _boom)
    assert (
        recorder.record_tac_observation(
            tac_text="METAR BAD",
            product="METAR",
            source="convert",
        )
        is None
    )

    store = StationHealthStore()
    set_station_health_store(store)
    monkeypatch.setattr(store, "record_observation", lambda **_k: None)
    monkeypatch.setattr(recorder, "extract_station_icao", lambda *_a, **_k: "KJFK")
    assert (
        recorder.record_tac_observation(
            tac_text="METAR KJFK=",
            product="METAR",
            source="convert",
            icao="KJFK",
        )
        is None
    )
    set_station_health_store(None)


def test_memory_store_invalid_icao_and_filters() -> None:
    store = StationHealthStore()
    store.reset()
    assert store.record_observation(icao="BAD", product="metar", tac_text="x", source="t") is None
    assert store.record_observation(icao="", product="metar", tac_text="x", source="t") is None
    later = datetime.now(UTC)
    earlier = later - timedelta(hours=1)
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010000Z 18008KT=",
        source="ingest",
        observed_at=later.replace(tzinfo=None),
        name=None,
    )
    store.record_observation(
        icao="KJFK",
        product="metar",
        tac_text="METAR KJFK 010100Z 18008KT=",
        source="ingest",
        observed_at=earlier,
        name="JFK",
    )
    payload = store.list_stations(window_key="bogus", product="speci")
    assert payload["stations"] == []
    payload = store.list_stations(window_key="6h", grade="Z")
    assert payload["stations"] == []
    assert store.get_station("ZZZZ") is None
    assert store.get_station("KJFK") is not None


def test_get_store_falls_back_without_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sys

    import src.services.station_health_store as store_mod

    set_station_health_store(None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    store = get_station_health_store()
    assert isinstance(store, StationHealthStore)

    # Import failure path returns memory store.
    set_station_health_store(None)
    real_pg_mod = sys.modules.get("src.services.station_health_postgres")
    monkeypatch.setitem(sys.modules, "src.services.station_health_postgres", None)
    assert isinstance(get_station_health_store(), StationHealthStore)
    if real_pg_mod is not None:
        monkeypatch.setitem(sys.modules, "src.services.station_health_postgres", real_pg_mod)
    else:
        monkeypatch.delitem(sys.modules, "src.services.station_health_postgres", raising=False)

    # Postgres URL path constructs a store via from_url/create_engine.
    set_station_health_store(None)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setattr(
        "src.services.station_health_postgres.create_engine",
        lambda *_a, **_k: MagicMock(name="engine"),
    )
    store_mod._pg_store = None
    store_mod._pg_url = None
    pg = get_station_health_store()
    assert type(pg).__name__ == "PostgresStationHealthStore"
    # Cache hit with same URL.
    assert get_station_health_store() is pg
    store_mod._pg_store = None
    store_mod._pg_url = None
    set_station_health_store(None)


def test_postgres_store_paths_and_exceptions() -> None:
    assert sync_database_url("postgresql+asyncpg://u:p@h/db") is not None
    assert sync_database_url("postgresql+psycopg2://u:p@h/db") is not None
    assert sync_database_url("mysql://u:p@h/db") == "mysql://u:p@h/db"
    assert "sslmode=require" in (sync_database_url("postgresql://u:p@h/db?ssl=require") or "")

    engine = MagicMock()
    # Avoid opening a real DB pool from from_url during unit tests.
    from src.services import station_health_postgres as pg_mod

    original_create = pg_mod.create_engine
    pg_mod.create_engine = lambda *_a, **_k: engine  # type: ignore[assignment]
    try:
        store_from_url = PostgresStationHealthStore.from_url(
            "postgresql+psycopg://u:p@h/db"
        )
    finally:
        pg_mod.create_engine = original_create  # type: ignore[assignment]
    assert isinstance(store_from_url, PostgresStationHealthStore)
    store = PostgresStationHealthStore(engine)
    store.reset()
    assert store.record_observation(icao="BAD", product="metar", tac_text="x", source="t") is None

    conn = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm
    begin_cm.__enter__.side_effect = RuntimeError("write fail")
    assert (
        store.record_observation(
            icao="KJFK",
            product="metar",
            tac_text="METAR KJFK=",
            source="t",
            observed_at=datetime(2026, 11, 13, tzinfo=UTC),
        )
        is None
    )

    begin_cm.__enter__.side_effect = None
    begin_cm.__enter__.return_value = conn
    connect_cm = MagicMock()
    connect_cm.__enter__.return_value = conn
    connect_cm.__exit__.return_value = None
    engine.connect.return_value = connect_cm

    # Successful write with naive observed_at.
    row = store.record_observation(
        icao="KJFK",
        product="",
        tac_text="METAR KJFK=",
        source="",
        observed_at=datetime(2026, 11, 13, 12, 0),
        name="JFK",
    )
    assert row is not None
    assert conn.execute.call_count >= 2

    # list_metrics success + empty fallback + exception fallback
    metrics_rows = MagicMock()
    metrics_rows.mappings.return_value = [
        {
            "id": "availability",
            "label": "Availability",
            "description": "d",
            "unit": "percent",
            "higher_is_better": True,
            "enabled": True,
            "sort_order": 1,
        }
    ]
    conn.execute.return_value = metrics_rows
    assert store.list_metrics()[0]["id"] == "availability"
    metrics_rows.mappings.return_value = []
    assert store.list_metrics()
    conn.execute.side_effect = RuntimeError("metrics down")
    assert store.list_metrics()

    # list_stations with product filter + get_station
    conn.execute.side_effect = None
    station_result = MagicMock()
    station_result.mappings.return_value = [{"icao": "KJFK", "name": "JFK"}]
    record_result = MagicMock()
    now = datetime.now(UTC)
    record_result.mappings.return_value = [
        {
            "icao": "KJFK",
            "product": "metar",
            "observed_at": now,
            "ingested_at": now,
            "tac_text": "METAR KJFK=",
            "source": "ingest",
            "solidus_count": 0,
            "missing_digit_count": 0,
            "lint_error_count": 0,
            "lint_warning_count": 0,
            "convert_ok": True,
        }
    ]
    conn.execute.side_effect = [station_result, record_result]
    listed = store.list_stations(window_key="bogus", product="metar", grade="Z", limit=1)
    assert listed["stations"] == []
    # Product filter with matching rows, then grade pass.
    conn.execute.side_effect = [station_result, record_result]
    listed = store.list_stations(window_key="6h", product="metar", limit=1)
    assert listed["summary"]["station_count"] >= 0
    # Product filter with no matching product rows skips the station.
    empty_records = MagicMock()
    empty_records.mappings.return_value = []
    conn.execute.side_effect = [station_result, empty_records]
    listed = store.list_stations(window_key="6h", product="speci")
    assert listed["stations"] == []

    meta = MagicMock()
    meta.mappings.return_value.first.return_value = {"icao": "KJFK", "name": "JFK"}
    detail_records = MagicMock()
    detail_records.mappings.return_value = record_result.mappings.return_value
    conn.execute.side_effect = [meta, detail_records]
    detail = store.get_station("kjfk")
    assert detail is not None
    assert detail["icao"] == "KJFK"

    meta.mappings.return_value.first.return_value = None
    conn.execute.side_effect = [meta]
    assert store.get_station("ZZZZ") is None

    conn.execute.side_effect = RuntimeError("detail down")
    assert store.get_station("KJFK") is None

    # _load_window exception path
    conn.execute.side_effect = RuntimeError("list down")
    stations, rows = store._load_window(cutoff=now - timedelta(hours=1), product_filter=None)
    assert stations == {}
    assert rows == []

    # product filter query path
    station_result = MagicMock()
    station_result.mappings.return_value = [{"icao": "KJFK", "name": None}]
    record_result = MagicMock()
    record_result.mappings.return_value = []
    conn.execute.side_effect = [station_result, record_result]
    stations, rows = store._load_window(cutoff=now - timedelta(hours=1), product_filter="metar")
    assert "KJFK" in stations


def test_sync_database_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    assert sync_database_url().startswith("postgresql+psycopg://")


def test_row_to_station_record_aware_timestamps() -> None:
    aware = datetime(2026, 11, 13, 12, 0, tzinfo=UTC)
    row = aggregate.row_to_station_record(
        {
            "icao": "KJFK",
            "product": "metar",
            "observed_at": aware,
            "ingested_at": aware,
            "tac_text": "x",
        }
    )
    assert isinstance(row, StationRecord)
