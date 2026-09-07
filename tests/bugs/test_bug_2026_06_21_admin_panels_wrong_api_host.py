"""BUG-2026-06-21 - admin panels called wrong API host (historical).

S011 / ADR-021 (#697): product ``/admin/*`` surface is removed. Regression now
asserts routes are absent (404), not auth-gated on a mounted admin router.
"""

from __future__ import annotations

import pathlib
import sys

from fastapi.testclient import TestClient

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.api import app  # noqa: E402

ADMIN_PATHS = (
    "/admin/settings",
    "/admin/all-users",
    "/admin/stats",
    "/admin/toggle-admin",
    "/admin/pending-users",
    "/admin/approve-user",
    "/admin/reject-user",
)


def test_admin_routes_registered_on_merged_api() -> None:
    """Admin product routes must be absent (404) after ADR-021 removal."""
    client = TestClient(app)
    for path in ADMIN_PATHS:
        response = (
            client.get(path)
            if path
            not in ("/admin/toggle-admin", "/admin/approve-user", "/admin/reject-user")
            else client.post(path, json={})
        )
        assert response.status_code == 404, (
            f"Expected admin route {path} removed (404), got {response.status_code}"
        )


def test_admin_settings_requires_authorization() -> None:
    """GET /admin/settings is gone - 404, not an auth challenge."""
    client = TestClient(app)
    response = client.get("/admin/settings")
    assert response.status_code == 404


def test_admin_settings_rejects_missing_bearer_prefix() -> None:
    """Malformed Authorization still yields 404 (route absent)."""
    client = TestClient(app)
    response = client.get("/admin/settings", headers={"Authorization": "Token abc"})
    assert response.status_code == 404
