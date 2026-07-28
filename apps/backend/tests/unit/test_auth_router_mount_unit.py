"""Unit tests: Auth routers are not mounted (F21 / ADR-031 / T5.2)."""

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
def test_backend_does_not_mount_auth_routes() -> None:
    """Operator /auth/* routers are removed (F21)."""
    from src.api import app

    paths = set(_iter_route_paths(app.routes))

    assert "/auth/login" not in paths
    assert "/auth/register" not in paths
    assert "/auth/me" not in paths
    assert not any(p.startswith("/auth/") for p in paths)
