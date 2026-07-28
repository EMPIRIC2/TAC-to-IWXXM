"""T5.1 / TC-F21-auth-gone — Auth and work-sessions gone; convert is public."""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient


def _iter_route_paths(routes) -> list[str]:
    paths: list[str] = []
    for route in routes:
        if isinstance(route, APIRoute):
            paths.append(route.path)
        elif type(route).__name__ == "_IncludedRouter":
            paths.extend(_iter_route_paths(route.original_router.routes))
        elif hasattr(route, "routes") and route.routes:
            paths.extend(_iter_route_paths(route.routes))
    return paths


@pytest.mark.unit
def test_auth_routes_absent_from_app() -> None:
    from src.api import app

    paths = set(_iter_route_paths(app.routes))
    assert "/auth/login" not in paths
    assert "/auth/register" not in paths
    assert "/auth/me" not in paths
    assert not any(p.startswith("/auth/") for p in paths)


@pytest.mark.unit
def test_work_sessions_routes_absent_from_app() -> None:
    from src.api import app

    paths = set(_iter_route_paths(app.routes))
    assert not any("/work-sessions" in p for p in paths)


@pytest.mark.unit
def test_auth_login_http_404() -> None:
    from src.api import app

    client = TestClient(app)
    response = client.post(
        "/auth/login",
        json={"email": "a@b.co", "password": "x"},
    )
    assert response.status_code == 404


@pytest.mark.unit
def test_work_sessions_list_http_404() -> None:
    from src.api import app

    client = TestClient(app)
    response = client.get("/api/v1/work-sessions")
    assert response.status_code == 404


@pytest.mark.unit
def test_convert_succeeds_without_authorization() -> None:
    """Public convert must not require Authorization (F21)."""
    from src import api as api_module

    api_module.app.dependency_overrides.clear()

    client = TestClient(api_module.app)
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 121851Z 09014KT 10SM FEW250",
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "validate_output": "false",
        },
    )
    # Must not be 401/403 — public surface after F21.
    assert response.status_code != 401
    assert response.status_code != 403
    assert response.status_code == 200, response.text
