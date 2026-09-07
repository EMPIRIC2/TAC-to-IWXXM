"""TC-EV052-006 - optional Sentry init (no-op without DSN)."""

from __future__ import annotations

from typing import Any

import pytest
from utilities import sentry_init


@pytest.mark.unit
def test_init_sentry_noop_when_dsn_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    called: list[dict[str, Any]] = []

    def _fake_init(**kwargs: Any) -> None:
        called.append(kwargs)

    monkeypatch.setattr(sentry_init.sentry_sdk, "init", _fake_init)
    assert sentry_init.init_sentry(service_name="backend") is False
    assert called == []


@pytest.mark.unit
def test_init_sentry_calls_sdk_when_dsn_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTRY_DSN", "https://public@example.ingest.sentry.io/1")
    called: list[dict[str, Any]] = []

    def _fake_init(**kwargs: Any) -> None:
        called.append(kwargs)

    monkeypatch.setattr(sentry_init.sentry_sdk, "init", _fake_init)
    assert sentry_init.init_sentry(service_name="backend") is True
    assert len(called) == 1
    assert called[0]["dsn"].startswith("https://")
    assert called[0]["traces_sample_rate"] <= 0.05
    assert called[0].get("profiles_sample_rate", 0) <= 0.05


@pytest.mark.unit
def test_init_sentry_explicit_dsn_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTRY_DSN", "https://env@example.ingest.sentry.io/1")
    called: list[dict[str, Any]] = []
    monkeypatch.setattr(sentry_init.sentry_sdk, "init", lambda **kwargs: called.append(kwargs))
    assert (
        sentry_init.init_sentry(
            service_name="worker",
            dsn="https://explicit@example.ingest.sentry.io/2",
        )
        is True
    )
    assert called[0]["dsn"] == "https://explicit@example.ingest.sentry.io/2"
