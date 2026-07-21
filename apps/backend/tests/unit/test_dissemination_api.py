"""API tests for dissemination preflight/send (T2.3 / ADR-029 / api-contract)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dissemination.handles import default_handle_store
from dissemination.rate_limit import DisseminationRateLimiter
from src import api as api_module
from src.routers import dissemination as diss_router
from src.utilities.security import verify_supabase_token


async def _auth_user() -> dict:
    return {"sub": "user-dissemination-test", "user_id": "user-dissemination-test"}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISABLE_AUTH", "true")
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    lim = DisseminationRateLimiter(max_per_minute=1000)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    default_handle_store.clear()
    api_module.app.dependency_overrides[verify_supabase_token] = _auth_user
    with TestClient(api_module.app) as c:
        yield c
    api_module.app.dependency_overrides.clear()
    default_handle_store.clear()


def _sqlite_uri(tmp_path: Path) -> str:
    db = tmp_path / "dissem.db"
    return f"sqlite+aiosqlite:///{db}"


def test_preflight_msgspec_shape_and_handle_memory_only(client: TestClient, tmp_path: Path) -> None:
    uri = _sqlite_uri(tmp_path)
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True, "product": "metar"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["ok"] is True
    assert body["connectivity_ok"] is True
    assert body["diffs"] == []
    assert body["handle"]
    assert "password" not in resp.text.lower()
    assert uri not in resp.text


def test_preflight_redacts_secret_in_error_detail(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "db.example.com")
    secret_uri = "postgresql://op:SuperSecretPass@db.example.com:5432/wx"
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "postgres", "uri": secret_uri, "ddl": False}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code in {400, 403, 500}
    assert "SuperSecretPass" not in resp.text


def test_preflight_fail_closed_remote_host_when_allowlist_empty(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps(
            {
                "sink_type": "postgres",
                "uri": "postgresql://u:p@db.example.com/wx",
                "ddl": False,
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 403
    assert "fail-closed" in resp.text or "allowlist" in resp.text.lower()
    assert ":p@" not in resp.text


def test_rate_limit_denies_after_budget(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lim = DisseminationRateLimiter(max_per_minute=3)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    uri = _sqlite_uri(tmp_path)
    payload = json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True})
    headers = {"Content-Type": "application/json", "Authorization": "Bearer t"}
    codes = [
        client.post("/api/v1/dissemination/preflight", content=payload, headers=headers).status_code for _ in range(4)
    ]
    assert 429 in codes


def test_send_with_handle_uploads_sqlite(client: TestClient, tmp_path: Path) -> None:
    uri = _sqlite_uri(tmp_path)
    pre = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": uri, "ddl": True}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert pre.status_code == 200, pre.text
    handle = pre.json()["handle"]
    send = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "handle": handle,
                "iwxxm_xml": "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>",
                "product": "metar",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert send.status_code == 200, send.text
    body = send.json()
    assert body["ok"] is True
    assert body["kv_upload_key"]
    assert "password" not in send.text.lower()


def test_send_invalid_handle_rejected(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps({"handle": "not-a-real-handle", "iwxxm_xml": "<x/>", "product": "metar"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 400
    assert "handle" in resp.text.lower()
