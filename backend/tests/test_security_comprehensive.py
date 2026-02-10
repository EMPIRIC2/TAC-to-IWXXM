"""Comprehensive tests for security and authentication."""
import pathlib
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import httpx

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from utilities.security import verify_supabase_token


class TestVerifySupabaseToken:
    """Test token verification via auth service proxy."""

    @pytest.mark.asyncio
    async def test_verify_token_success(self):
        """Test successful token verification via auth service."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token.here"
        )
        
        expected_response = {
            "sub": "user123",
            "email": "test@example.com",
            "aud": "authenticated"
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=expected_response)
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await verify_supabase_token(mock_credentials)
            assert result["sub"] == "user123"
            assert result["email"] == "test@example.com"
            
            # Verify the auth service was called with correct token
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert "Bearer valid.token.here" in str(call_args)

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )
        
        mock_response = AsyncMock()
        mock_response.status_code = 401
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(mock_credentials)
            assert exc_info.value.status_code == 401
            assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_auth_service_error(self):
        """Test token verification when auth service returns error."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )
        
        mock_response = AsyncMock()
        mock_response.status_code = 500
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(mock_credentials)
            assert exc_info.value.status_code == 500
            assert "Auth service error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_timeout(self):
        """Test token verification when auth service times out."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(mock_credentials)
            assert exc_info.value.status_code == 503
            assert "Auth service timeout" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_connection_error(self):
        """Test token verification when cannot connect to auth service."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(mock_credentials)
            assert exc_info.value.status_code == 503
            assert "Cannot connect to auth service" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_token_unexpected_error(self):
        """Test token verification handles unexpected errors."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test.token.here"
        )
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=RuntimeError("Unexpected error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(mock_credentials)
            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_verify_token_user_not_found(self):
        """Test token verification when user is not found."""
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token.here"
        )
        
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
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
        
        expected_response = {
            "id": "user-id-123",
            "sub": "user123",
            "email": "test@example.com",
            "aud": "authenticated",
            "iss": "https://xyz.supabase.co/auth/v1",
            "exp": 1234567890
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=expected_response)
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            result = await verify_supabase_token(mock_credentials)
            assert result == expected_response


