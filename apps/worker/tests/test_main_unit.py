"""Unit coverage for metar_worker.__main__ entrypoint (EV-047 T2.5.4)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
import respx
from metar_worker import __main__ as worker_main
from metar_worker.pipeline import PipelineResult
from metar_worker.settings import WorkerSettings
from metar_worker.store import RESULTS_TABLE

pytestmark = pytest.mark.unit


class MemoryStore:
    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = {
            RESULTS_TABLE: [],
            "iwxxm_ingest_quarantine": [],
        }

    def insert(self, table: str, row: dict[str, Any]) -> None:
        self.rows.setdefault(table, []).append(row)


def _fake_process(job: Any, **_kwargs: Any) -> PipelineResult:
    return PipelineResult(
        job_id=job.job_id,
        ok=True,
        product=job.product,
        profile="annex3",
        xml="<iwxxm:METAR/>",
        issues=[],
    )


def test_handle_sigterm_sets_shutdown_flag() -> None:
    worker_main._shutdown = False
    worker_main._handle_sigterm(15, None)
    assert worker_main._shutdown is True
    worker_main._shutdown = False


@respx.mock
def test_run_once_constructs_postgres_store_when_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_main._seen_job_ids.clear()
    url = "https://ingest.example.test/once.json"
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": "m1",
                        "product": "METAR",
                        "tac": "METAR KJFK 231751Z NIL=",
                    }
                ]
            },
        )
    )
    monkeypatch.setenv("INGEST_POLLER_URL", url)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/db")

    fake_store = MemoryStore()
    constructed: list[str] = []

    def fake_pg(database_url: str) -> MemoryStore:
        constructed.append(database_url)
        return fake_store

    monkeypatch.setattr(worker_main, "PostgresStore", fake_pg)
    monkeypatch.setattr(worker_main, "process_job", _fake_process)

    settings = WorkerSettings()
    assert worker_main.run_once(settings, store=None) == 1
    assert constructed == ["postgresql://u:p@localhost:5432/db"]
    assert len(fake_store.rows[RESULTS_TABLE]) == 1


def test_main_exits_2_on_invalid_poller_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INGEST_POLLER_URL", "REPLACE_ME_INGEST_POLLER_URL")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    with pytest.raises(SystemExit) as exc:
        worker_main.main()
    assert exc.value.code == 2


@respx.mock
def test_main_once_mode_runs_single_cycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_main._seen_job_ids.clear()
    worker_main._shutdown = False
    url = "https://ingest.example.test/main-once.json"
    respx.get(url).mock(return_value=httpx.Response(200, json={"items": []}))
    monkeypatch.setenv("INGEST_POLLER_URL", url)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("INGEST_ONCE", "true")

    fake_store = MemoryStore()
    monkeypatch.setattr(worker_main, "PostgresStore", lambda **_k: fake_store)
    monkeypatch.setattr(worker_main, "process_job", _fake_process)
    signal_mock = MagicMock()
    monkeypatch.setattr(worker_main.signal, "signal", signal_mock)

    worker_main.main()
    assert signal_mock.call_count == 2


@respx.mock
def test_main_loop_handles_exception_and_shutdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_main._seen_job_ids.clear()
    worker_main._shutdown = False
    url = "https://ingest.example.test/main-loop.json"
    monkeypatch.setenv("INGEST_POLLER_URL", url)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("INGEST_ONCE", "false")
    monkeypatch.setenv("INGEST_POLL_INTERVAL_SEC", "2")

    calls = {"n": 0}

    def flaky_once(*_a: Any, **_k: Any) -> int:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("transient poll failure")
        worker_main._shutdown = True
        return 0

    monkeypatch.setattr(worker_main, "run_once", flaky_once)
    monkeypatch.setattr(worker_main.signal, "signal", MagicMock())
    sleep_calls: list[float] = []

    def fake_sleep(sec: float) -> None:
        sleep_calls.append(sec)

    monkeypatch.setattr(worker_main.time, "sleep", fake_sleep)

    worker_main.main()
    assert calls["n"] == 2
    assert sleep_calls  # waited at least one second tick after first failure


@respx.mock
def test_main_loop_breaks_sleep_on_shutdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_main._seen_job_ids.clear()
    worker_main._shutdown = False
    url = "https://ingest.example.test/main-break.json"
    monkeypatch.setenv("INGEST_POLLER_URL", url)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("INGEST_ONCE", "0")
    monkeypatch.setenv("INGEST_POLL_INTERVAL_SEC", "3")

    def run_and_request_stop(*_a: Any, **_k: Any) -> int:
        worker_main._shutdown = True
        return 0

    monkeypatch.setattr(worker_main, "run_once", run_and_request_stop)
    monkeypatch.setattr(worker_main.signal, "signal", MagicMock())
    monkeypatch.setattr(worker_main.time, "sleep", MagicMock())

    worker_main.main()
    worker_main.time.sleep.assert_not_called()
