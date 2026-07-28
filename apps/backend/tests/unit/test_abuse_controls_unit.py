"""T3.1 / ADR-031 — rate-limit (429) and max-body (413) unit tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from utilities.abuse_controls import (
    MaxBodySizeMiddleware,
    create_limiter,
    dissemination_limit,
    get_max_request_body_bytes,
    get_rate_limit_dissemination_per_min,
    get_rate_limit_public_per_min,
    install_abuse_controls,
)


def test_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RATE_LIMIT_PUBLIC_PER_MIN", raising=False)
    monkeypatch.delenv("RATE_LIMIT_DISSEMINATION_PER_MIN", raising=False)
    monkeypatch.delenv("MAX_REQUEST_BODY_BYTES", raising=False)
    assert get_rate_limit_public_per_min() == 60
    assert get_rate_limit_dissemination_per_min() == 10
    assert get_max_request_body_bytes() == 2_097_152


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_PUBLIC_PER_MIN", "5")
    monkeypatch.setenv("RATE_LIMIT_DISSEMINATION_PER_MIN", "2")
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "1024")
    assert get_rate_limit_public_per_min() == 5
    assert get_rate_limit_dissemination_per_min() == 2
    assert get_max_request_body_bytes() == 1024


def test_max_body_middleware_returns_413(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "100")
    app = FastAPI()
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=100)

    @app.post("/api/v1/echo")
    async def echo() -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    response = client.post(
        "/api/v1/echo",
        content=b"x" * 101,
        headers={"content-length": "101"},
    )
    assert response.status_code == 413
    assert "maximum" in response.json()["detail"].lower()


def test_public_rate_limit_returns_429(monkeypatch: pytest.MonkeyPatch) -> None:
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
    limited = client.get("/api/v1/ping")
    assert limited.status_code == 429


def test_dissemination_limit_stricter_than_public(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RATE_LIMIT_PUBLIC_PER_MIN", "60")
    monkeypatch.setenv("RATE_LIMIT_DISSEMINATION_PER_MIN", "1")
    app = FastAPI()
    limiter = create_limiter()
    install_abuse_controls(app, limiter=limiter)

    @app.post("/api/v1/dissemination/preflight")
    @dissemination_limit(limiter)
    async def preflight(request: Request) -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    assert client.post("/api/v1/dissemination/preflight").status_code == 200
    limited = client.post("/api/v1/dissemination/preflight")
    assert limited.status_code == 429
