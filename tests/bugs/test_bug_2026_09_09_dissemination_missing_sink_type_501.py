"""BUG-2026-09-09 — missing/null dissemination sink_type must be 422, not 501."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from dissemination.handles import default_handle_store
from dissemination.rate_limit import DisseminationRateLimiter
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src import api as api_module  # noqa: E402
from src.routers import dissemination as diss_router  # noqa: E402
from src.utilities.abuse_controls import get_limiter  # noqa: E402


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    lim = DisseminationRateLimiter(max_per_minute=1000)
    monkeypatch.setattr(diss_router, "default_rate_limiter", lim)
    default_handle_store.clear()
    get_limiter().reset()
    with TestClient(api_module.app) as c:
        yield c
    api_module.app.dependency_overrides.clear()
    default_handle_store.clear()
    get_limiter().reset()


@pytest.mark.parametrize(
    ("path", "body"),
    [
        ("/api/v1/dissemination/preflight", {}),
        ("/api/v1/dissemination/preflight", {"uri": "http://127.0.0.1:5432/postgres"}),
        ("/api/v1/dissemination/send", {}),
        ("/api/v1/dissemination/send", {"sink_type": None, "iwxxm_xml": "<x/>"}),
        (
            "/api/v1/dissemination/send",
            {"uri": "http://127.0.0.1:5432/postgres", "iwxxm_xml": "<x/>"},
        ),
    ],
)
def test_bug_2026_09_09_missing_sink_type_is_422(
    client: TestClient,
    path: str,
    body: dict,
) -> None:
    """F-ADV-01: omit/null sink_type without handle/template → 422 (not 501)."""
    resp = client.post(
        path,
        content=json.dumps(body),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 422, resp.text
    detail = resp.json().get("detail", "")
    assert "sink_type" in str(detail).lower()


def test_bug_2026_09_09_unimplemented_sink_still_501(client: TestClient) -> None:
    """Known drawer sinks that are not live on this route remain 501."""
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "wis2", "uri": "mqtt://example.com"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 501, resp.text
