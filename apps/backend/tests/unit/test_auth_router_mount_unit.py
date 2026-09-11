"""Unit tests: Auth routers mounted JWKS-only (F31 / ADR-033 / T1.2)."""

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
def test_backend_mounts_auth_login_logout_and_me() -> None:
    """Operator /auth/register, /auth/login, /auth/logout, /auth/me are mounted; no admin.

    Spec: [Corpus: api] POST /auth/register; EV-beta-ux-export-auth; EV-060 logout.
    """
    from src.api import app

    paths = set(_iter_route_paths(app.routes))

    assert "/auth/register" in paths
    assert "/auth/login" in paths
    assert "/auth/logout" in paths
    assert "/auth/me" in paths
    assert not any("/admin" in p for p in paths)
