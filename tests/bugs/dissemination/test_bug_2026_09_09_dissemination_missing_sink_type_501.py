"""BUG-2026-09-09 — dissemination HTTP surface removed (FR-052..056 / M1).

Historically missing/null ``sink_type`` had to be 422 (not 501). After the M1
drop the routes are unmounted, so the regression is now fail-closed 404.

[Corpus: fr] epic #1688
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src import api as api_module  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    with TestClient(api_module.app) as c:
        yield c
    api_module.app.dependency_overrides.clear()


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
def test_bug_2026_09_09_dissemination_routes_unmounted(
    client: TestClient,
    path: str,
    body: dict,
) -> None:
    """FR-052..056 / M1: dissemination HTTP paths are absent (404)."""
    resp = client.post(
        path,
        content=json.dumps(body),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 404, resp.text


def test_bug_2026_09_09_wis2_route_unmounted(client: TestClient) -> None:
    """WIS2 preflight is unmounted with the rest of dissemination (404)."""
    resp = client.post(
        "/api/v1/dissemination/preflight",
        content=json.dumps({"sink_type": "wis2", "uri": "mqtt://example.com"}),
        headers={"Content-Type": "application/json", "Authorization": "Bearer t"},
    )
    assert resp.status_code == 404, resp.text
