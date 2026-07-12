"""Advisory fix: in-process job_id dedup across poll cycles."""

from __future__ import annotations

import httpx
import pytest
import respx
from metar_worker import __main__ as worker_main
from metar_worker.settings import WorkerSettings
from metar_worker.store import RESULTS_TABLE


class MemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, list] = {RESULTS_TABLE: [], "iwxxm_ingest_quarantine": []}

    def insert(self, table: str, row: dict) -> None:
        self.rows.setdefault(table, []).append(row)


@respx.mock
def test_run_once_skips_already_seen_job_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_main._seen_job_ids.clear()
    feed = {
        "items": [
            {
                "id": "dedup-1",
                "product": "METAR",
                "tac": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
            }
        ]
    }
    url = "https://ingest.example.test/dedup.json"
    respx.get(url).mock(return_value=httpx.Response(200, json=feed))
    monkeypatch.setenv("INGEST_POLLER_URL", url)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")

    def fake_process(job, **kwargs):
        from metar_worker.pipeline import PipelineResult

        return PipelineResult(
            job_id=job.job_id,
            ok=True,
            product=job.product,
            profile="annex3",
            xml="<iwxxm:METAR/>",
            issues=[],
        )

    monkeypatch.setattr(worker_main, "process_job", fake_process)
    settings = WorkerSettings()
    store = MemoryStore()
    assert worker_main.run_once(settings, store=store) == 1
    assert worker_main.run_once(settings, store=store) == 0
    assert len(store.rows[RESULTS_TABLE]) == 1
