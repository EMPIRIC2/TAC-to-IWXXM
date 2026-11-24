"""Drop-guard: dissemination HTTP surface removed (FR-052..056 / DI-008 / M1).

[Corpus: fr] epic #1688
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
    ],
)
def test_dissemination_routes_return_404(client: TestClient, method: str, path: str) -> None:
    """Public and ops dissemination routes are not registered."""
    response = client.request(method, path)
    assert response.status_code == 404, response.text[:400]
