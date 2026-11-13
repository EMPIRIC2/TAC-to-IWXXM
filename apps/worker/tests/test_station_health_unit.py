"""Worker station health helpers ([Corpus: tests] — no skips)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from metar_worker.station_health import (
    extract_icao,
    maybe_record_from_row,
    record_station_observation,
    solidus_counts,
)
from metar_worker.store import RESULTS_TABLE, PostgresStore
from sqlalchemy.exc import SQLAlchemyError

pytestmark = pytest.mark.unit


def test_extract_icao_metar_and_taf() -> None:
    """Parse ICAO from METAR and TAF; reject SIGMET."""
    assert extract_icao("METAR KJFK 010000Z 18008KT=", "METAR") == "KJFK"
    assert extract_icao("TAF KLAX 010000Z 0100/0206 25010KT=", "TAF") == "KLAX"
    assert extract_icao("SPECI EGLL 010000Z 18008KT=", "SPECI") == "EGLL"
    assert extract_icao("SIGMET ...", "SIGMET") is None


def test_solidus_counts() -> None:
    """Count solidus characters and missing-digit runs."""
    solidus, missing = solidus_counts("METAR KJFK 010000Z ////KT 15/07=")
    assert solidus == 5
    assert missing == 1


@pytest.mark.parametrize(
    ("mode", "tac", "product", "expect_icao"),
    [
        ("success", "METAR KJFK 010000Z 18008KT=", "METAR", "KJFK"),
        ("failure", "SIGMET NYC A1...", "SIGMET", None),
        ("validation", "METAR 010000Z 18008KT=", "METAR", None),
    ],
)
def test_extract_icao_modes(
    mode: str, tac: str, product: str, expect_icao: str | None
) -> None:
    """Success / failure / validation battery for ICAO extraction."""
    del mode
    assert extract_icao(tac, product) == expect_icao


def test_record_station_observation_writes_registry_and_tac() -> None:
    """Success: METAR observation inserts registry + TAC rows."""
    engine = MagicMock()
    conn = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm

    icao = record_station_observation(
        engine,
        tac_text="METAR KJFK 010000Z 18008KT=",
        product="METAR",
        convert_ok=True,
    )
    assert icao == "KJFK"
    assert conn.execute.call_count == 2


def test_record_station_observation_returns_none_without_icao() -> None:
    """Failure: non-station products do not write."""
    engine = MagicMock()
    assert (
        record_station_observation(
            engine, tac_text="SIGMET A1", product="SIGMET", convert_ok=False
        )
        is None
    )
    engine.begin.assert_not_called()


def test_record_station_observation_swallows_engine_errors() -> None:
    """Validation: engine errors return None without raising."""
    engine = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.side_effect = SQLAlchemyError("boom")
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm
    assert (
        record_station_observation(
            engine,
            tac_text="METAR KJFK 010000Z 18008KT=",
            product="METAR",
            convert_ok=True,
        )
        is None
    )


def test_maybe_record_from_row_noops_without_engine() -> None:
    """Validation: missing engine is a no-op."""
    maybe_record_from_row(
        None, {"tac_input": "METAR KJFK 010000Z=", "product": "METAR"}, convert_ok=True
    )


def test_postgres_store_insert_records_station_health_and_swallows_errors() -> None:
    """Insert still persists when station-health recording raises."""
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    engine = MagicMock()
    conn = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm

    with (
        patch("metar_worker.store.create_engine", return_value=engine),
        patch(
            "metar_worker.station_health.maybe_record_from_row",
            side_effect=RuntimeError("health down"),
        ) as record,
    ):
        store.insert(
            RESULTS_TABLE,
            {
                "job_id": "j-health",
                "product": "METAR",
                "tac_input": "METAR KJFK 010000Z 18008KT=",
                "issues": [],
            },
        )
    record.assert_called_once()
    assert conn.execute.call_count == 1
