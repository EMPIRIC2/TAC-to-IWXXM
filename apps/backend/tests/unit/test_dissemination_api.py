"""API tests for dissemination preflight/send (T2.3 / ADR-029 / api-contract)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from dissemination.handles import default_handle_store
from dissemination.rate_limit import DisseminationRateLimiter
from fastapi.testclient import TestClient

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


def test_preflight_rejects_invalid_json_body(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=b"{not-json",
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 422


def test_preflight_unimplemented_sink(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "wis2", "uri": "mqtt://example.com"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 501


def test_send_requires_iwxxm_xml(client: TestClient, tmp_path: Path) -> None:
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
        content=json.dumps({"handle": handle, "iwxxm_xml": "", "product": "metar"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert send.status_code == 400
    assert "iwxxm_xml" in send.text.lower()


def test_send_without_uri_or_handle_rejected(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps({"sink_type": "sqlite", "iwxxm_xml": "<x/>", "product": "metar"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 400


def test_preflight_value_error_becomes_400(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def _boom(_req):
        raise ValueError("uri is required for DB sink preflight")

    monkeypatch.setattr(diss_router, "run_db_preflight", _boom)
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": "sqlite+aiosqlite:///:memory:", "ddl": False}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 400


def test_send_rate_limit_denies(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    lim = DisseminationRateLimiter(max_per_minute=0)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps({"handle": "x", "iwxxm_xml": "<x/>", "product": "metar"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 429


def test_send_unimplemented_sink_inline(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "sink_type": "wis2",
                "uri": "mqtt://example.com",
                "iwxxm_xml": "<x/>",
                "product": "metar",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 501


def test_send_egress_denied(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from dissemination.allowlist import EgressDenied

    async def _deny(_req):
        raise EgressDenied("fail-closed: empty allowlist")

    monkeypatch.setattr(diss_router, "run_db_preflight", _deny)
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "sink_type": "sqlite",
                "uri": "sqlite+aiosqlite:///:memory:",
                "iwxxm_xml": "<x/>",
                "product": "metar",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 403


def test_send_writer_contract_conflict(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from dissemination.models import PreflightResponse

    async def _mismatch(_req):
        return PreflightResponse(ok=False, connectivity_ok=True, diffs=[], detail="mismatch")

    monkeypatch.setattr(diss_router, "run_db_preflight", _mismatch)
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "sink_type": "sqlite",
                "uri": "sqlite+aiosqlite:///:memory:",
                "iwxxm_xml": "<x/>",
                "product": "metar",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 409


def test_preflight_unexpected_error_becomes_500(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def _boom(_req):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(diss_router, "run_db_preflight", _boom)
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "sqlite", "uri": "sqlite+aiosqlite:///:memory:", "ddl": False}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 500


def test_send_value_error_becomes_400(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def _boom(_req):
        raise ValueError("bad sink")

    monkeypatch.setattr(diss_router, "run_db_preflight", _boom)
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "sink_type": "sqlite",
                "uri": "sqlite+aiosqlite:///:memory:",
                "iwxxm_xml": "<x/>",
                "product": "metar",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 400


def test_send_apply_failure_becomes_500(client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from dissemination.models import PreflightResponse

    async def _ok(_req):
        return PreflightResponse(ok=True, connectivity_ok=True, diffs=[], detail=None)

    async def _fail(*_a, **_k):
        raise RuntimeError("apply failed")

    monkeypatch.setattr(diss_router, "run_db_preflight", _ok)
    monkeypatch.setattr(diss_router, "apply_writer_contract", _fail)
    uri = _sqlite_uri(tmp_path)
    resp = client.post(
        "/api/v1/dissemination/send",
        content=json.dumps(
            {
                "sink_type": "sqlite",
                "uri": uri,
                "iwxxm_xml": "<x/>",
                "product": "metar",
            }
        ),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 500
