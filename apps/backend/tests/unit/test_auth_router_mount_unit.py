"""Unit tests for auth router mounting on the backend API (T5.3 / ADR-002)."""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute


def _iter_route_paths(routes) -> list[str]:
    """Collect paths from app routes, including FastAPI _IncludedRouter wrappers."""
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
def test_backend_mounts_auth_routes() -> None:
    """Auth package routers must be available at /auth/* on the backend app."""
    from src.api import app

    paths = set(_iter_route_paths(app.routes))

    assert "/auth/login" in paths
    assert "/auth/register" in paths
    assert "/auth/me" in paths
    assert "/auth/verify" in paths
    assert "/auth/refresh" in paths
    assert "/logout" in paths
