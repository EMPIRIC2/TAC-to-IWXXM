"""Worker main / run_once hard-fail paths (EV-stage coverage expansion).

[Corpus: tests]
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from metar_worker import __main__ as worker_main
from metar_worker.settings import WorkerSettings

pytestmark = pytest.mark.unit


def test_run_once_requires_database_url_when_store_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INGEST_POLLER_URL", "https://ingest.example.test/feed.json")
    monkeypatch.setenv("DATABASE_URL", "")
    settings = WorkerSettings()
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        worker_main.run_once(settings, store=None)


def test_main_exits_2_when_poller_url_is_placeholder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INGEST_POLLER_URL", "REPLACE_ME_INGEST_POLLER_URL")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setattr(worker_main.signal, "signal", MagicMock())
    with pytest.raises(SystemExit) as exc:
        worker_main.main()
    assert exc.value.code == 2


def test_main_loop_logs_and_continues_after_poll_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_main._shutdown = False
    monkeypatch.setenv("INGEST_POLLER_URL", "https://ingest.example.test/loop.json")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("INGEST_ONCE", "false")
    monkeypatch.setenv("INGEST_POLL_INTERVAL_SEC", "1")

    calls = {"n": 0}

    def flaky_once(*_a: Any, **_k: Any) -> int:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("poll boom")
        worker_main._shutdown = True
        return 0

    monkeypatch.setattr(worker_main, "run_once", flaky_once)
    monkeypatch.setattr(worker_main.signal, "signal", MagicMock())
    monkeypatch.setattr(worker_main.time, "sleep", MagicMock())

    worker_main.main()
    assert calls["n"] == 2
