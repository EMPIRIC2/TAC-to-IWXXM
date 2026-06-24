"""BUG-2026-06-21 — admin panels call Supabase Edge Functions instead of merged API.

Repro: SystemSettingsPanel / MonitoringPanel must use VITE_API_BASE_URL/admin/*
not supabase.co/functions/v1/make-server-2e3cda33/admin/*.
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


def test_admin_routes_registered_on_merged_api() -> None:
    """Admin router must be mounted at /admin/* on the backend app."""
    client = TestClient(app)
    for path in (
        "/admin/settings",
        "/admin/all-users",
        "/admin/stats",
        "/admin/toggle-admin",
        "/admin/pending-users",
        "/admin/approve-user",
        "/admin/reject-user",
    ):
        response = (
            client.get(path)
            if path not in ("/admin/toggle-admin", "/admin/approve-user", "/admin/reject-user")
            else client.post(path, json={})
        )
        assert response.status_code in (401, 403, 422), (
            f"Expected admin route {path} on merged API, got {response.status_code}"
        )


def test_admin_settings_requires_authorization() -> None:
    """Unauthenticated GET /admin/settings returns 401."""
    from src.api import app

    client = TestClient(app)
    response = client.get("/admin/settings")
    assert response.status_code == 401


def test_admin_settings_rejects_missing_bearer_prefix() -> None:
    """Malformed Authorization header returns 401."""
    from src.api import app

    client = TestClient(app)
    response = client.get("/admin/settings", headers={"Authorization": "Token abc"})
    assert response.status_code == 401
