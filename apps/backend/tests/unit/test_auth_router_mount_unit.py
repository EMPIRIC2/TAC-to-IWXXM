"""Unit tests: Auth HTTP proxy routes removed (F31 FE-direct / ADR-033 amend)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_auth_http_routes_not_mounted() -> None:
    """Operator login is FE-direct; API must not mount /auth/* helpers."""
    from src.api import app

    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/auth/register" not in paths
    assert "/auth/login" not in paths
    assert "/auth/confirm" not in paths
    assert "/auth/logout" not in paths
    assert "/auth/me" not in paths


@pytest.mark.unit
def test_auth_login_path_returns_404() -> None:
    from src.api import app

    client = TestClient(app)
    response = client.post("/auth/login", json={"email": "a@b.com", "password": "x"})
    assert response.status_code == 404
