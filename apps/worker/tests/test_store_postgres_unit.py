"""Unit coverage for PostgresStore URL normalize + insert/select (mocked engine)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from metar_worker.store import (
    QUARANTINE_TABLE,
    RESULTS_TABLE,
    PostgresStore,
    _to_psycopg_url,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "postgresql+asyncpg://u:p@h/db",
            "postgresql+psycopg://u:p@h/db",
        ),
        (
            "postgresql+psycopg2://u:p@h/db",
            "postgresql+psycopg://u:p@h/db",
        ),
        (
            "postgresql://u:p@h/db",
            "postgresql+psycopg://u:p@h/db",
        ),
        (
            "postgresql+psycopg://u:p@h/db",
            "postgresql+psycopg://u:p@h/db",
        ),
        ("sqlite:///:memory:", "sqlite:///:memory:"),
    ],
)
def test_to_psycopg_url_rewrites_known_schemes(raw: str, expected: str) -> None:
    assert _to_psycopg_url(raw) == expected


def test_postgres_store_insert_rejects_unknown_table() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    with pytest.raises(ValueError, match="unexpected table"):
        store.insert("not_a_table", {"job_id": "x"})


def test_postgres_store_fetch_rejects_unknown_table() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    with pytest.raises(ValueError, match="unexpected table"):
        store.fetch_by_job_id("not_a_table", "x")


def test_postgres_store_insert_executes_against_engine() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    engine = MagicMock()
    conn = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm

    with patch("metar_worker.store.create_engine", return_value=engine) as create:
        store.insert(
            RESULTS_TABLE,
            {
                "job_id": "j1",
                "product": "METAR",
                "profile": "annex3",
                "source_url": "https://example.test/feed",
                "tac_input": "METAR KJFK 231751Z NIL=",
                "iwxxm_xml": "<iwxxm:METAR/>",
                "issues": [{"stage": "lint"}],
                "stage_failed": None,
            },
        )
        # Second insert reuses cached engine.
        store.insert(
            QUARANTINE_TABLE,
            {
                "job_id": "j2",
                "product": "METAR",
                "tac_input": "BAD",
                "issues": [],
                "stage_failed": "lint",
            },
        )

    create.assert_called_once()
    assert engine.begin.call_count == 2
    assert conn.execute.call_count == 2
    first_params = conn.execute.call_args_list[0].args[1]
    assert first_params["job_id"] == "j1"
    assert '"stage"' in first_params["issues"] or "lint" in first_params["issues"]


def test_postgres_store_fetch_by_job_id_maps_rows() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    engine = MagicMock()
    conn = MagicMock()
    connect_cm = MagicMock()
    connect_cm.__enter__.return_value = conn
    connect_cm.__exit__.return_value = None
    engine.connect.return_value = connect_cm

    row = MagicMock()
    row._mapping = {
        "job_id": "j1",
        "product": "METAR",
        "profile": "annex3",
        "source_url": "https://example.test/feed",
        "tac_input": "METAR KJFK 231751Z NIL=",
        "iwxxm_xml": "<iwxxm:METAR/>",
        "issues": [],
        "stage_failed": None,
    }
    conn.execute.return_value = [row]

    with patch("metar_worker.store.create_engine", return_value=engine):
        rows = store.fetch_by_job_id(RESULTS_TABLE, "j1")

    assert rows == [dict(row._mapping)]
    assert isinstance(rows[0], dict)
    assert rows[0]["job_id"] == "j1"


def test_postgres_store_insert_defaults_optional_fields() -> None:
    store = PostgresStore(database_url="postgresql+asyncpg://u:p@h/db")
    engine = MagicMock()
    conn = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.return_value = conn
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm

    with patch("metar_worker.store.create_engine", return_value=engine) as create:
        store.insert(RESULTS_TABLE, {"job_id": "j3", "product": "SPECI"})

    create.assert_called_once()
    assert create.call_args.args[0].startswith("postgresql+psycopg://")
    params: dict[str, Any] = conn.execute.call_args.args[1]
    assert params["profile"] == "annex3"
    assert params["source_url"] == ""
    assert params["tac_input"] == ""
    assert params["issues"] == "[]"
    assert params["iwxxm_xml"] is None
