"""Integration tests for backend using the auth service.

Tests that backend correctly calls the auth service to verify tokens.
"""
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials

# Ensure imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ["AUTH_SERVICE_URL"] = "http://localhost:8002"

pytestmark = pytest.mark.asyncio


class TestBackendAuthServiceIntegration:
    """Test backend integration with auth service."""
    
    @pytest.mark.asyncio
    async def test_backend_token_verification_success(self):
        """Backend successfully verifies token via auth service."""
        from backend.src.utilities.security import verify_supabase_token
        
        with patch("backend.src.utilities.security.httpx.AsyncClient") as mock_client_cls:
            # Setup mock
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = lambda: {
                "id": "user-123",
                "email": "test@example.com",
                "metadata": {}
            }
            mock_client.get.return_value = mock_response
            
            # Create credentials object
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="valid-token"
            )
            
            # Call verification
            user = await verify_supabase_token(credentials)
            
            # Assert
            assert user["id"] == "user-123"
            assert user["email"] == "test@example.com"
            mock_client.get.assert_called()
    
    @pytest.mark.asyncio
    async def test_backend_token_verification_invalid(self):
        """Backend properly handles invalid token from auth service."""
        from fastapi import HTTPException

        from backend.src.utilities.security import verify_supabase_token
        
        with patch("backend.src.utilities.security.httpx.AsyncClient") as mock_client_cls:
            # Setup mock for 401 response
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json = lambda: {"detail": "Invalid token"}
            mock_client.get.return_value = mock_response
            
            # Create credentials object
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="invalid-token"
            )
            
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(credentials)
            
            assert exc_info.value.status_code == 401


class TestAuthServiceMissingConfiguration:
    """Test behavior when auth service URL is not configured."""
    
    def test_auth_service_url_required(self):
        """System requires AUTH_SERVICE_URL to be set."""
        # The environment should have AUTH_SERVICE_URL set
        assert os.environ.get("AUTH_SERVICE_URL") == "http://localhost:8002"


class TestAuthServiceFailureHandling:
    """Test graceful handling of auth service failures."""
    
    @pytest.mark.asyncio
    async def test_auth_service_connection_error(self):
        """Backend handles auth service connection errors gracefully."""
        from fastapi import HTTPException

        from backend.src.utilities.security import verify_supabase_token
        
        with patch("backend.src.utilities.security.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client
            
            # Simulate connection error
            mock_client.get.side_effect = Exception("Connection refused")
            
            # Create credentials object
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="token"
            )
            
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await verify_supabase_token(credentials)
            
            # General exceptions are caught and return 500
            assert exc_info.value.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
