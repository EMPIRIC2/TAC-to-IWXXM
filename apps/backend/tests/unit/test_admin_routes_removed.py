"""TC-F7-006: product ``/admin/*`` routes must be absent (S011 / ADR-021)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)

ADMIN_PATHS = (
    "/admin/settings",
    "/admin/all-users",
    "/admin/stats",
    "/admin/work-sessions",
)


def test_admin_product_routes_return_404() -> None:
    """Admin product surface is removed — callers get not-found, not auth challenges."""
    for path in ADMIN_PATHS:
        response = client.get(path)
        assert response.status_code == 404, f"{path} expected 404, got {response.status_code}"
