"""TC-EV052-006 — worker Sentry optional init."""

from __future__ import annotations

from typing import Any

import pytest
from metar_worker import sentry_init


@pytest.mark.unit
def test_worker_sentry_noop_without_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    called: list[Any] = []
    monkeypatch.setattr(
        sentry_init.sentry_sdk, "init", lambda **kwargs: called.append(kwargs)
    )
    assert sentry_init.init_sentry() is False
    assert called == []


@pytest.mark.unit
def test_worker_sentry_init_with_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTRY_DSN", "https://public@example.ingest.sentry.io/1")
    called: list[dict[str, Any]] = []
    monkeypatch.setattr(
        sentry_init.sentry_sdk, "init", lambda **kwargs: called.append(kwargs)
    )
    monkeypatch.setattr(sentry_init.sentry_sdk, "set_tag", lambda *_a, **_k: None)
    assert sentry_init.init_sentry() is True
    assert called[0]["dsn"].startswith("https://")
    assert called[0]["traces_sample_rate"] == 0.0
