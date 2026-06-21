"""Unit tests for merged API admin routes."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from admin_api import require_admin, router


@pytest.fixture
def admin_client() -> TestClient:
    """Minimal app exposing only the admin router."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_get_settings_returns_defaults_for_admin(admin_client: TestClient) -> None:
    """Admin user receives default system settings."""
    admin_client.app.dependency_overrides[require_admin] = lambda: {
        "id": "admin-id",
        "email": "admin@metar.local",
    }
    try:
        response = admin_client.get(
            "/admin/settings",
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["settings"]["defaultBulletinId"] == "SAAA00"
    assert body["settings"]["defaultIwxxmVersion"] == "2025-2"


def test_non_admin_receives_403(admin_client: TestClient) -> None:
    """Non-admin user is forbidden from admin settings."""

    def _deny_admin() -> None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    admin_client.app.dependency_overrides[require_admin] = _deny_admin
    try:
        response = admin_client.get(
            "/admin/settings",
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        admin_client.app.dependency_overrides.clear()

    assert response.status_code == 403
