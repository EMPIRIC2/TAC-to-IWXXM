"""Unit tests for SupabaseAuthProxy – improves coverage from 58% target."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from auth.supabase_proxy import SupabaseAuthProxy
from supabase_proxy import _is_session_not_found_error


class TestIsSessionNotFoundError:
    def test_detects_session_not_found_string(self):
        assert _is_session_not_found_error(Exception("session_not_found")) is True

    def test_detects_full_message(self):
        assert _is_session_not_found_error(Exception("session from session_id claim in jwt does not exist")) is True

    def test_returns_false_for_other_errors(self):
        assert _is_session_not_found_error(Exception("invalid credentials")) is False

    def test_case_insensitive(self):
        assert _is_session_not_found_error(Exception("SESSION_NOT_FOUND")) is True


def _make_proxy():
    """Create a SupabaseAuthProxy with a mocked Supabase client."""
    with patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_PUBLISHABLE_KEY": "test-key"}):
        with patch("supabase_proxy.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            proxy = SupabaseAuthProxy()
            proxy.client = mock_client
    return proxy


class TestSupabaseAuthProxyInit:
    def test_raises_when_env_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((ValueError, Exception)):
                SupabaseAuthProxy()

    def test_creates_with_env_set(self):
        proxy = _make_proxy()
        assert proxy.supabase_url == "https://test.supabase.co"
        assert proxy.supabase_key == "test-key"


class TestSupabaseAuthProxySignUp:
    def test_sign_up_success(self):
        proxy = _make_proxy()
        mock_user = MagicMock()
        mock_user.id = "user-id-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"name": "Test"}
        mock_response = MagicMock()
        mock_response.user = mock_user
        mock_response.session = None
        proxy.client.auth.sign_up.return_value = mock_response

        result = proxy.sign_up("test@example.com", "password123")
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["id"] == "user-id-123"

    def test_sign_up_no_user_raises_400(self):
        proxy = _make_proxy()
        mock_response = MagicMock()
        mock_response.user = None
        proxy.client.auth.sign_up.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            proxy.sign_up("test@example.com", "password")
        assert exc_info.value.status_code == 400

    def test_sign_up_exception_raises_400(self):
        proxy = _make_proxy()
        proxy.client.auth.sign_up.side_effect = Exception("supabase error")

        with pytest.raises(HTTPException) as exc_info:
            proxy.sign_up("test@example.com", "password")
        assert exc_info.value.status_code == 400

    def test_sign_up_with_metadata(self):
        proxy = _make_proxy()
        mock_user = MagicMock()
        mock_user.id = "uid"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"name": "Alice"}
        mock_response = MagicMock()
        mock_response.user = mock_user
        mock_response.session = None
        proxy.client.auth.sign_up.return_value = mock_response

        result = proxy.sign_up("test@example.com", "pass", metadata={"name": "Alice"})
        call_args = proxy.client.auth.sign_up.call_args[0][0]
        assert call_args["options"]["data"]["name"] == "Alice"


class TestSupabaseAuthProxySignIn:
    def test_sign_in_success(self):
        proxy = _make_proxy()
        mock_user = MagicMock()
        mock_user.id = "uid"
        mock_user.email = "user@example.com"
        mock_user.user_metadata = {}
        mock_session = MagicMock()
        mock_session.access_token = "access-token"
        mock_session.refresh_token = "refresh-token"
        mock_session.expires_at = 9999999
        mock_response = MagicMock()
        mock_response.user = mock_user
        mock_response.session = mock_session
        proxy.client.auth.sign_in_with_password.return_value = mock_response

        result = proxy.sign_in("user@example.com", "password")
        assert result["session"]["access_token"] == "access-token"
        assert result["user"]["email"] == "user@example.com"

    def test_sign_in_no_user_raises_401(self):
        proxy = _make_proxy()
        mock_response = MagicMock()
        mock_response.user = None
        mock_response.session = None
        proxy.client.auth.sign_in_with_password.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            proxy.sign_in("user@example.com", "wrong-password")
        assert exc_info.value.status_code == 401

    def test_sign_in_exception_raises_401(self):
        proxy = _make_proxy()
        proxy.client.auth.sign_in_with_password.side_effect = Exception("auth failed")

        with pytest.raises(HTTPException) as exc_info:
            proxy.sign_in("user@example.com", "password")
        assert exc_info.value.status_code == 401


class TestSupabaseAuthProxySignOut:
    def test_sign_out_success(self):
        proxy = _make_proxy()
        proxy.client.auth.sign_out.return_value = None
        result = proxy.sign_out("access-token")
        assert "signed out" in result["message"].lower()

    def test_sign_out_session_not_found_returns_success(self):
        proxy = _make_proxy()
        proxy.client.auth.sign_out.side_effect = Exception("session_not_found")
        result = proxy.sign_out("stale-token")
        assert "signed out" in result["message"].lower()

    def test_sign_out_other_exception_raises_400(self):
        proxy = _make_proxy()
        proxy.client.auth.sign_out.side_effect = Exception("network error")
        with pytest.raises(HTTPException) as exc_info:
            proxy.sign_out("token")
        assert exc_info.value.status_code == 400


class TestSupabaseAuthProxyGetUser:
    def test_get_user_success(self):
        proxy = _make_proxy()
        mock_user = MagicMock()
        mock_user.id = "uid"
        mock_user.email = "user@example.com"
        mock_user.user_metadata = {"role": "user"}
        mock_response = MagicMock()
        mock_response.user = mock_user
        proxy.client.auth.get_user.return_value = mock_response

        result = proxy.get_user("access-token")
        assert result["id"] == "uid"
        assert result["email"] == "user@example.com"

    def test_get_user_none_response_raises_401(self):
        proxy = _make_proxy()
        proxy.client.auth.get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            proxy.get_user("bad-token")
        assert exc_info.value.status_code == 401

    def test_get_user_missing_user_raises_401(self):
        proxy = _make_proxy()
        mock_response = MagicMock()
        mock_response.user = None
        proxy.client.auth.get_user.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            proxy.get_user("bad-token")
        assert exc_info.value.status_code == 401

    def test_get_user_exception_raises_401(self):
        proxy = _make_proxy()
        proxy.client.auth.get_user.side_effect = Exception("network error")

        with pytest.raises(HTTPException) as exc_info:
            proxy.get_user("token")
        assert exc_info.value.status_code == 401


class TestSupabaseAuthProxyRefreshSession:
    def test_refresh_session_success(self):
        proxy = _make_proxy()
        mock_session = MagicMock()
        mock_session.access_token = "new-access"
        mock_session.refresh_token = "new-refresh"
        mock_session.expires_at = 123456
        mock_response = MagicMock()
        mock_response.session = mock_session
        proxy.client.auth.refresh_session.return_value = mock_response

        result = proxy.refresh_session("refresh-token")
        assert result["access_token"] == "new-access"
        assert result["refresh_token"] == "new-refresh"

    def test_refresh_session_no_session_raises_401(self):
        proxy = _make_proxy()
        mock_response = MagicMock()
        mock_response.session = None
        proxy.client.auth.refresh_session.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            proxy.refresh_session("bad-refresh")
        assert exc_info.value.status_code == 401

    def test_refresh_session_exception_raises_401(self):
        proxy = _make_proxy()
        proxy.client.auth.refresh_session.side_effect = Exception("refresh failed")

        with pytest.raises(HTTPException) as exc_info:
            proxy.refresh_session("refresh-token")
        assert exc_info.value.status_code == 401
