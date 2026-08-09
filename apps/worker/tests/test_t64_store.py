"""T6.4: store vs quarantine routing (service JWT writers — mocked PostgREST)."""

from __future__ import annotations

from typing import Any

import pytest
from metar_worker.pipeline import PipelineResult
from metar_worker.poller import IngestJob
from metar_worker.store import QUARANTINE_TABLE, RESULTS_TABLE, write_result

pytestmark = pytest.mark.unit


class MemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = {
            RESULTS_TABLE: [],
            QUARANTINE_TABLE: [],
        }

    def insert(self, table: str, row: dict[str, Any]) -> None:
        self.rows[table].append(row)


def _job() -> IngestJob:
    return IngestJob(
        job_id="s1",
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://example.test/feed",
    )


def test_t64_pass_writes_results_table() -> None:
    store = MemoryStore()
    result = PipelineResult(
        job_id="s1",
        ok=True,
        product="METAR",
        profile="annex3",
        xml="<iwxxm:METAR/>",
        issues=[],
    )
    table = write_result(store, _job(), result)
    assert table == RESULTS_TABLE
    assert len(store.rows[RESULTS_TABLE]) == 1
    assert store.rows[RESULTS_TABLE][0]["iwxxm_xml"] == "<iwxxm:METAR/>"
    assert store.rows[QUARANTINE_TABLE] == []


def test_t64_fail_writes_quarantine_table() -> None:
    store = MemoryStore()
    result = PipelineResult(
        job_id="s1",
        ok=False,
        product="METAR",
        profile="annex3",
        xml=None,
        issues=[{"stage": "lint", "code": "x", "message": "bad", "severity": "error"}],
        stage_failed="lint",
    )
    table = write_result(store, _job(), result)
    assert table == QUARANTINE_TABLE
    assert len(store.rows[QUARANTINE_TABLE]) == 1
    assert store.rows[QUARANTINE_TABLE][0]["stage_failed"] == "lint"
    assert store.rows[RESULTS_TABLE] == []


def test_t64_source_url_strips_query_tokens() -> None:
    store = MemoryStore()
    job = IngestJob(
        job_id="s2",
        product="METAR",
        tac="METAR KJFK 231751Z NIL=",
        source_url="https://user:tok@ingest.example.test/feed.json?token=secret",
    )
    result = PipelineResult(
        job_id="s2",
        ok=True,
        product="METAR",
        profile="annex3",
        xml="<iwxxm:METAR/>",
        issues=[],
    )
    write_result(store, job, result)
    assert store.rows[RESULTS_TABLE][0]["source_url"] == (
        "https://ingest.example.test/feed.json"
    )
