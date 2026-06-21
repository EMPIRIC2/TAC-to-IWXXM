"""Unit tests for merged API admin routes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException, status
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


def test_require_admin_returns_403_when_profile_missing() -> None:
    """Missing user_profiles row returns 403 instead of 500."""
    mock_proxy = MagicMock()
    mock_proxy.get_user.return_value = {"id": "orphan-user", "email": "orphan@example.com"}
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = None

    with patch("admin_api._get_service_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            require_admin(token="test-token", proxy=mock_proxy)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_save_settings_rejects_empty_payload(admin_client: TestClient) -> None:
    """Empty settings object must not wipe stored configuration."""
    admin_client.app.dependency_overrides[require_admin] = lambda: {
        "id": "admin-id",
        "email": "admin@metar.local",
    }
    try:
        response = admin_client.post(
            "/admin/settings",
            headers={"Authorization": "Bearer test-token"},
            json={"settings": {}},
        )
    finally:
        admin_client.app.dependency_overrides.clear()

    assert response.status_code == 422


def test_save_settings_merges_with_defaults(admin_client: TestClient) -> None:
    """Partial settings update preserves default keys."""
    admin_client.app.dependency_overrides[require_admin] = lambda: {
        "id": "admin-id",
        "email": "admin@metar.local",
    }
    try:
        response = admin_client.post(
            "/admin/settings",
            headers={"Authorization": "Bearer test-token"},
            json={"settings": {"defaultLogLevel": "DEBUG"}},
        )
    finally:
        admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    settings = response.json()["settings"]
    assert settings["defaultLogLevel"] == "DEBUG"
    assert settings["defaultBulletinId"] == "SAAA00"
