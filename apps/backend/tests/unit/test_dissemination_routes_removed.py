"""Drop-guard: dissemination HTTP surface removed (FR-052..056 / DI-008 / M1).

[Corpus: fr] epic #1688 / #1696
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module


@pytest.fixture
def client() -> TestClient:
    with TestClient(api_module.app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/api/v1/dissemination/preflight"),
        ("POST", "/api/v1/dissemination/send"),
        ("GET", "/api/v1/dissemination/audit"),
        ("GET", "/api/v1/dissemination/plans/example-plan"),
        ("PUT", "/api/v1/dissemination/plans/example-plan"),
        ("GET", "/api/v1/dissemination/gateways/health"),
        ("POST", "/api/v1/dissemination/unknown"),
        ("DELETE", "/api/v1/dissemination/send"),
    ],
)
def test_dissemination_routes_return_404(client: TestClient, method: str, path: str) -> None:
    """Public and ops dissemination routes are not registered (drop_guard happy / not_found)."""
    response = client.request(method, path)
    assert response.status_code == 404, response.text[:400]


def test_dissemination_preflight_with_body_still_404(client: TestClient) -> None:
    """Validation-shaped body cannot revive unmounted routes (mutation x failure)."""
    response = client.post(
        "/api/v1/dissemination/preflight",
        json={"sink_type": "postgres", "uri": "postgresql://127.0.0.1/db"},
    )
    assert response.status_code == 404


def test_dissemination_send_with_body_still_404(client: TestClient) -> None:
    """Send mutation with payload is rejected as not found (delete-equivalent surface gone)."""
    response = client.post(
        "/api/v1/dissemination/send",
        json={"sink_type": "wis2", "payload": "<iwxxm/>"},
    )
    assert response.status_code == 404
