"""PostgresStore insert / select failure paths (EV-stage coverage expansion).

[Corpus: tests] — unknown tables and engine-level insert errors.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from metar_worker.pipeline import PipelineResult
from metar_worker.poller import IngestJob
from metar_worker.store import (
    QUARANTINE_TABLE,
    RESULTS_TABLE,
    PostgresStore,
    write_result,
)

pytestmark = pytest.mark.unit


def test_insert_rejects_unexpected_table() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    with pytest.raises(ValueError, match="unexpected table"):
        store.insert("iwxxm_ingest_other", {"job_id": "x", "product": "METAR"})


def test_fetch_rejects_unexpected_table() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    with pytest.raises(ValueError, match="unexpected table"):
        store.fetch_by_job_id("public.secrets", "job-1")


def test_insert_propagates_engine_errors() -> None:
    store = PostgresStore(database_url="postgresql://u:p@localhost/db")
    engine = MagicMock()
    begin_cm = MagicMock()
    begin_cm.__enter__.side_effect = RuntimeError("connection refused")
    begin_cm.__exit__.return_value = None
    engine.begin.return_value = begin_cm

    with (
        patch("metar_worker.store.create_engine", return_value=engine),
        pytest.raises(RuntimeError, match="connection refused"),
    ):
        store.insert(
            RESULTS_TABLE,
            {
                "job_id": "j-fail",
                "product": "METAR",
                "tac_input": "METAR KJFK 231751Z NIL=",
            },
        )


def test_write_result_quarantines_when_ok_but_xml_missing() -> None:
    class BoomStore:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict]] = []

        def insert(self, table: str, row: dict) -> None:
            self.calls.append((table, row))

    job = IngestJob(
        job_id="q1",
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://example.test/feed?token=secret",
    )
    result = PipelineResult(
        job_id="q1",
        ok=True,
        product="METAR",
        profile="annex3",
        xml=None,
        issues=[{"stage": "convert", "code": "EMPTY_XML", "message": "no xml"}],
        stage_failed="convert",
    )
    store = BoomStore()
    table = write_result(store, job, result)
    assert table == QUARANTINE_TABLE
    assert store.calls[0][0] == QUARANTINE_TABLE
    assert "token=secret" not in store.calls[0][1]["source_url"]
