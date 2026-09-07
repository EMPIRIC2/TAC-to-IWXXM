"""TC-EV052-007 / TC-EV052-008 - REDIS_URL slowapi storage + shared counters."""

from __future__ import annotations

import logging

import fakeredis
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from utilities import abuse_controls
from utilities.abuse_controls import create_limiter, install_abuse_controls


@pytest.fixture(autouse=True)
def _reset_limiter_singleton() -> None:
    abuse_controls._limiter = None
    yield
    abuse_controls._limiter = None


@pytest.mark.unit
def test_create_limiter_memory_when_redis_unset(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)
    with caplog.at_level(logging.WARNING, logger="utilities.abuse_controls"):
        lim = create_limiter()
    assert lim is not None
    storage_uri = lim._storage_uri
    assert storage_uri in (None, "memory://") or "memory" in str(storage_uri).lower()
    assert any("REDIS_URL" in r.message for r in caplog.records)


@pytest.mark.unit
def test_create_limiter_uses_redis_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REDIS_URL", "rediss://default:token@example.upstash.io:6379")
    lim = create_limiter()
    assert lim._storage_uri == "rediss://default:token@example.upstash.io:6379"


@pytest.mark.unit
def test_fakeredis_shared_counters_across_clients() -> None:
    """AC8 - two clients on one FakeServer share key state (multi-replica stand-in)."""
    server = fakeredis.FakeServer()
    client_a = fakeredis.FakeStrictRedis(server=server)
    client_b = fakeredis.FakeStrictRedis(server=server)
    key = "limits:ev052-shared"
    assert client_a.incr(key) == 1
    assert int(client_b.get(key) or 0) == 1
    assert client_b.incr(key) == 2
    assert int(client_a.get(key) or 0) == 2


@pytest.mark.unit
def test_rate_limit_still_enforced_with_memory_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("RATE_LIMIT_PUBLIC_PER_MIN", "2")
    app = FastAPI()
    limiter = create_limiter()
    install_abuse_controls(app, limiter=limiter)

    @app.get("/api/v1/ping")
    @limiter.limit("2/minute")
    async def ping(request: Request) -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    assert client.get("/api/v1/ping").status_code == 200
    assert client.get("/api/v1/ping").status_code == 200
    assert client.get("/api/v1/ping").status_code == 429
