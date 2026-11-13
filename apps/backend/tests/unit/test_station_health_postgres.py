"""Unit coverage for Postgres station-health URL helpers and store routing."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
from src.services.station_health_postgres import PostgresStationHealthStore, sync_database_url
from src.services.station_health_store import (
    StationHealthStore,
    get_station_health_store,
    set_station_health_store,
)


@pytest.mark.parametrize(
    ("raw", "expected_prefix"),
    [
        (None, None),
        ("", None),
        ("postgresql://user:pass@host/db", "postgresql+psycopg://"),
        ("postgresql+asyncpg://user:pass@host/db", "postgresql+psycopg://"),
        ("postgresql+psycopg2://user:pass@host/db?ssl=require", "postgresql+psycopg://"),
    ],
)
def test_sync_database_url_normalization(
    monkeypatch: pytest.MonkeyPatch,
    raw: str | None,
    expected_prefix: str | None,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    result = sync_database_url(raw)
    if expected_prefix is None:
        assert result is None
    else:
        assert result is not None
        assert result.startswith(expected_prefix)
        if raw and "ssl=require" in raw:
            assert "sslmode=require" in result


def test_get_store_prefers_override(monkeypatch: pytest.MonkeyPatch) -> None:
    memory = StationHealthStore()
    set_station_health_store(memory)
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/db")
    assert get_station_health_store() is memory
    set_station_health_store(None)


def test_postgres_record_observation_writes_sql() -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = conn
    store = PostgresStationHealthStore(engine)
    row = store.record_observation(
        icao="KJFK",
        product="METAR",
        tac_text="METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=",
        source="convert",
        convert_ok=True,
        observed_at=datetime(2026, 11, 13, 12, 0, tzinfo=UTC),
    )
    assert row is not None
    assert row.icao == "KJFK"
    assert conn.execute.call_count == 2


@pytest.mark.parametrize(
    ("stations", "records", "expect_icao"),
    [
        (
            [{"icao": "KJFK", "name": "JFK"}],
            [
                {
                    "icao": "KJFK",
                    "product": "metar",
                    "observed_at": datetime.now(UTC),
                    "ingested_at": datetime.now(UTC),
                    "tac_text": "METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=",
                    "source": "ingest",
                    "solidus_count": 1,
                    "missing_digit_count": 0,
                    "lint_error_count": 0,
                    "lint_warning_count": 0,
                    "convert_ok": True,
                }
            ],
            "KJFK",
        ),
        ([], [], None),
    ],
)
def test_postgres_list_stations_from_rows(
    stations: list[dict[str, Any]],
    records: list[dict[str, Any]],
    expect_icao: str | None,
) -> None:
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn

    station_result = MagicMock()
    station_result.mappings.return_value = stations
    record_result = MagicMock()
    record_result.mappings.return_value = records
    conn.execute.side_effect = [station_result, record_result]

    store = PostgresStationHealthStore(engine)
    payload = store.list_stations(window_key="6h")
    if expect_icao is None:
        assert payload["stations"] == []
        assert payload["summary"]["station_count"] == 0
    else:
        assert payload["stations"][0]["icao"] == expect_icao
        assert payload["summary"]["station_count"] == 1
