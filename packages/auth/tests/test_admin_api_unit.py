"""Unit tests for merged API admin routes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from admin_api import (
    _get_authed_client,
    _profile_row,
    _profile_rows,
    require_admin,
    router,
)


def _admin_override() -> dict[str, str]:
    return {"id": "admin-id", "email": "admin@metar.local"}


def _mock_profile_table(
    *,
    maybe_single_data: object = None,
    select_data: list[dict[str, object]] | None = None,
    pending_select_data: list[dict[str, object]] | None = None,
    update_data: list[dict[str, object]] | None = None,
) -> MagicMock:
    """Build a chained Supabase table mock for admin route tests."""
    mock_client = MagicMock()
    table = mock_client.table.return_value

    maybe_single = table.select.return_value.eq.return_value.maybe_single.return_value
    maybe_single.execute.return_value = MagicMock(data=maybe_single_data)

    select_chain = table.select.return_value
    select_chain.order.return_value.execute.return_value = MagicMock(data=select_data or [])
    select_chain.execute.return_value = MagicMock(data=select_data or [])

    pending_chain = table.select.return_value.eq.return_value
    pending_chain.order.return_value.execute.return_value = MagicMock(
        data=pending_select_data if pending_select_data is not None else (select_data or [])
    )

    update_chain = table.update.return_value.eq.return_value
    update_chain.execute.return_value = MagicMock(data=update_data)

    return mock_client


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

    with patch("admin_api._get_authed_client", return_value=mock_client):
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


def test_save_settings_rejects_unknown_keys(admin_client: TestClient) -> None:
    """Unknown settings keys are rejected."""
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    try:
        response = admin_client.post(
            "/admin/settings",
            headers={"Authorization": "Bearer test-token"},
            json={"settings": {"notARealKey": True}},
        )
    finally:
        admin_client.app.dependency_overrides.clear()

    assert response.status_code == 422


def test_get_authed_client_requires_supabase_env() -> None:
    """Missing Supabase configuration returns 503."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(HTTPException) as exc_info:
            _get_authed_client("user-jwt")

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_require_admin_allows_admin_profile() -> None:
    """Valid admin profile passes require_admin."""
    mock_proxy = MagicMock()
    mock_proxy.get_user.return_value = {"id": "admin-id", "email": "admin@metar.local"}
    mock_client = _mock_profile_table(maybe_single_data={"is_admin": True})

    with patch("admin_api._get_authed_client", return_value=mock_client):
        user = require_admin(token="test-token", proxy=mock_proxy)

    assert user["id"] == "admin-id"


def test_require_admin_rejects_non_admin_profile() -> None:
    """Profile without admin flag is forbidden."""
    mock_proxy = MagicMock()
    mock_proxy.get_user.return_value = {"id": "user-id", "email": "user@example.com"}
    mock_client = _mock_profile_table(maybe_single_data={"is_admin": False})

    with patch("admin_api._get_authed_client", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            require_admin(token="test-token", proxy=mock_proxy)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_list_pending_users_returns_profiles(admin_client: TestClient) -> None:
    """Approval panel receives pending user profiles."""
    rows = [
        {
            "id": "user-pending",
            "email": "pending@example.com",
            "username": "pending1",
            "approval_status": "pending",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch(
        "admin_api._get_authed_client",
        return_value=_mock_profile_table(pending_select_data=rows),
    ):
        response = admin_client.get(
            "/admin/pending-users",
            headers={"Authorization": "Bearer test-token"},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    users = response.json()["users"]
    assert users[0]["id"] == "user-pending"
    assert users[0]["approval_status"] == "pending"


def test_approve_user_updates_profile(admin_client: TestClient) -> None:
    """Admin can approve a pending user."""
    updated = [
        {
            "id": "user-pending",
            "email": "pending@example.com",
            "username": "pending1",
            "approval_status": "approved",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(update_data=updated)):
        response = admin_client.post(
            "/admin/approve-user",
            headers={"Authorization": "Bearer test-token"},
            json={"userId": "user-pending"},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["profile"]["approval_status"] == "approved"


def test_reject_user_updates_profile(admin_client: TestClient) -> None:
    """Admin can reject a pending user."""
    updated = [
        {
            "id": "user-pending",
            "email": "pending@example.com",
            "username": "pending1",
            "approval_status": "rejected",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(update_data=updated)):
        response = admin_client.post(
            "/admin/reject-user",
            headers={"Authorization": "Bearer test-token"},
            json={"userId": "user-pending"},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["profile"]["approval_status"] == "rejected"


def test_list_all_users_returns_profiles(admin_client: TestClient) -> None:
    """Monitoring panel receives mapped user profiles."""
    rows = [
        {
            "id": "user-1",
            "email": "user@example.com",
            "username": "user1",
            "approval_status": "approved",
            "is_admin": False,
        }
    ]
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(select_data=rows)):
        response = admin_client.get(
            "/admin/all-users",
            headers={"Authorization": "Bearer test-token"},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    users = response.json()["users"]
    assert users[0]["email"] == "user@example.com"
    assert users[0]["is_admin"] is False


def test_get_stats_aggregates_user_counts(admin_client: TestClient) -> None:
    """Stats endpoint aggregates approval and admin counts."""
    rows = [
        {"approval_status": "pending", "is_admin": False},
        {"approval_status": "approved", "is_admin": True},
        {"approval_status": "rejected", "is_admin": False},
    ]
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(select_data=rows)):
        response = admin_client.get(
            "/admin/stats",
            headers={"Authorization": "Bearer test-token"},
        )
    admin_client.app.dependency_overrides.clear()

    stats = response.json()["stats"]
    assert stats["totalUsers"] == 3
    assert stats["pendingUsers"] == 1
    assert stats["approvedUsers"] == 1
    assert stats["rejectedUsers"] == 1
    assert stats["adminUsers"] == 1


def test_toggle_admin_updates_profile(admin_client: TestClient) -> None:
    """Admin can grant admin status to another user."""
    updated = [{"id": "user-2", "email": "user2@example.com", "is_admin": True}]
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(update_data=updated)):
        response = admin_client.post(
            "/admin/toggle-admin",
            headers={"Authorization": "Bearer test-token"},
            json={"userId": "user-2", "isAdmin": True},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["profile"]["is_admin"] is True


def test_toggle_admin_returns_404_when_user_missing(admin_client: TestClient) -> None:
    """Unknown user id returns 404."""
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(update_data=[])):
        response = admin_client.post(
            "/admin/toggle-admin",
            headers={"Authorization": "Bearer test-token"},
            json={"userId": "missing-user", "isAdmin": True},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 404


def test_profile_row_returns_none_for_non_dict() -> None:
    """Non-mapping Supabase payloads are ignored."""
    assert _profile_row("not-a-dict") is None
    assert _profile_row(None) is None


def test_profile_row_returns_dict() -> None:
    """Mapping payloads are returned as profile rows."""
    row = {"id": "user-1", "email": "user@example.com"}
    assert _profile_row(row) == row


def test_profile_rows_returns_empty_for_non_list() -> None:
    """Non-list Supabase payloads yield no profile rows."""
    assert _profile_rows({"id": "user-1"}) == []


def test_profile_rows_filters_non_dict_items() -> None:
    """Profile row helper keeps only mapping entries."""
    rows = _profile_rows([{"id": "1"}, "skip", {"id": "2"}])
    assert rows == [{"id": "1"}, {"id": "2"}]


def test_get_authed_client_success() -> None:
    """Authed client is created when Supabase env vars are set."""
    with patch.dict(
        "os.environ",
        {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_PUBLISHABLE_KEY": "publishable-key"},
        clear=True,
    ):
        with patch("admin_api.create_client", return_value=MagicMock()) as mock_create:
            client = _get_authed_client("user-jwt")
    mock_create.assert_called_once_with("https://test.supabase.co", "publishable-key")
    mock_create.return_value.postgrest.auth.assert_called_once_with("user-jwt")
    assert client is not None


def test_toggle_admin_returns_404_when_profile_row_invalid(admin_client: TestClient) -> None:
    """Non-dict update payload is treated as missing user."""
    admin_client.app.dependency_overrides[require_admin] = _admin_override
    with patch("admin_api._get_authed_client", return_value=_mock_profile_table(update_data=["bad-row"])):
        response = admin_client.post(
            "/admin/toggle-admin",
            headers={"Authorization": "Bearer test-token"},
            json={"userId": "user-2", "isAdmin": True},
        )
    admin_client.app.dependency_overrides.clear()

    assert response.status_code == 404


def test_auth_admin_api_compat_import() -> None:
    """Compatibility wrapper re-exports admin router."""
    from auth.admin_api import router as compat_router

    assert compat_router is router
