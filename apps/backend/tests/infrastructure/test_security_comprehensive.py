"""Comprehensive tests for security and authentication."""
import pathlib
import sys
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from src.utilities.security import verify_supabase_token


class _FakeProxy:
    def __init__(
        self,
        *,
        verify: bool = True,
        user: dict | None = None,
        get_user_error: Exception | None = None,
    ) -> None:
        self._verify = verify
        self._user = user or {
            "id": "user123",
            "email": "test@example.com",
            "metadata": {},
        }
        self._get_user_error = get_user_error

    def verify_token(self, _token: str) -> bool:
        return self._verify

    def get_user(self, _token: str) -> dict:
        if self._get_user_error:
            raise self._get_user_error
        return self._user


class TestVerifySupabaseToken:
    """Test token verification via inlined auth package."""

    @pytest.mark.asyncio
    async def test_verify_token_success(self):
        """Test successful token verification via auth package."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token.here"
        )

        proxy = _FakeProxy(
            user={
                "id": "user123",
                "email": "test@example.com",
                "metadata": {},
            }
        )

        with patch.dict('os.environ', {'DISABLE_AUTH': 'false'}):
            with patch('src.utilities.security.get_supabase_proxy', return_value=proxy):
                result = await verify_supabase_token(mock_credentials)
                assert result["sub"] == "user123"
                assert result["email"] == "test@example.com"
                assert result["authenticated"] is True

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )

        proxy = _FakeProxy(verify=False)

        with patch.dict('os.environ', {'DISABLE_AUTH': 'false'}):
            with patch('src.utilities.security.get_supabase_proxy', return_value=proxy):
                with pytest.raises(HTTPException) as exc_info:
                    await verify_supabase_token(mock_credentials)
                assert exc_info.value.status_code == 401
                assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_auth_not_configured(self):
        """Test token verification when Supabase env is missing."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )

        with patch.dict('os.environ', {'DISABLE_AUTH': 'false'}):
            with patch(
                'src.utilities.security.get_supabase_proxy',
                side_effect=ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set"),
            ):
                with pytest.raises(HTTPException) as exc_info:
                    await verify_supabase_token(mock_credentials)
                assert exc_info.value.status_code == 503
                assert "not configured" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_verify_token_get_user_failure(self):
        """Test token verification when user lookup fails."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )

        proxy = _FakeProxy(
            get_user_error=HTTPException(status_code=401, detail="Failed to get user")
        )

        with patch.dict('os.environ', {'DISABLE_AUTH': 'false'}):
            with patch('src.utilities.security.get_supabase_proxy', return_value=proxy):
                with pytest.raises(HTTPException) as exc_info:
                    await verify_supabase_token(mock_credentials)
                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_token_unexpected_error(self):
        """Test token verification handles unexpected errors."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )

        proxy = _FakeProxy(get_user_error=RuntimeError("Unexpected error"))

        with patch.dict('os.environ', {'DISABLE_AUTH': 'false'}):
            with patch('src.utilities.security.get_supabase_proxy', return_value=proxy):
                with pytest.raises(HTTPException) as exc_info:
                    await verify_supabase_token(mock_credentials)
                assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_verify_token_return_user_data(self):
        """Test token verification returns complete user data."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token.here"
        )

        proxy = _FakeProxy(
            user={
                "id": "user-id-123",
                "email": "test@example.com",
                "metadata": {"role": "admin"},
            }
        )

        with patch.dict('os.environ', {'DISABLE_AUTH': 'false'}):
            with patch('src.utilities.security.get_supabase_proxy', return_value=proxy):
                result = await verify_supabase_token(mock_credentials)
                assert result["sub"] == "user-id-123"
                assert result["user_id"] == "user-id-123"
                assert result["email"] == "test@example.com"
                assert result["metadata"] == {"role": "admin"}
