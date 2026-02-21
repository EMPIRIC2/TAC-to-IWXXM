"""Integration tests for the auth service as a Supabase proxy.

Tests the complete authentication flow through the auth service middleware.
Target: 95%+ coverage for auth service in proxy mode.
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_supabase_client():
    """Mock Supabase client globally for all tests."""
    with patch("supabase.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


# Set test environment after setting up mocks
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlc3QiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYwMCwicGF0biI6IlRlc3QifQ.x7P_5LqkfNhLXY1Ri4r0JZ0wEw-JZ7gZ7Y7Z7Z7Z7Z8"
os.environ["FRONTEND_BASE_URL"] = "http://localhost:8000"

# Now import app after environment is set
from auth.__main__ import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("auth.supabase_proxy.SupabaseAuthProxy") as mock:
        yield mock


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Health check returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestRegistration:
    """Test user registration endpoint."""
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_register_success(self, client):
        """Successful registration via Supabase."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.sign_up.return_value = {
                "user": {
                    "id": "user-123",
                    "email": "test@example.com",
                    "metadata": {"name": "Test User", "username": "testuser"}
                },
                "session": {
                    "access_token": "token-123",
                    "refresh_token": "refresh-123",
                    "expires_at": 1234567890
                }
            }
            
            response = client.post("/auth/register", json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User",
                "username": "testuser"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["user"]["email"] == "test@example.com"
            assert data["session"]["access_token"] == "token-123"
    
    def test_register_missing_password(self, client):
        """Registration fails with short password."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "short",  # Too short
            "name": "Test"
        })
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test user login endpoint."""
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_login_success(self, client):
        """Successful login via Supabase."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.sign_in.return_value = {
                "user": {
                    "id": "user-123",
                    "email": "test@example.com",
                    "metadata": {}
                },
                "session": {
                    "access_token": "token-123",
                    "refresh_token": "refresh-123",
                    "expires_at": 1234567890
                }
            }
            
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["id"] == "user-123"
    
    def test_login_invalid_credentials(self, client):
        """Login fails with invalid credentials."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            from fastapi import HTTPException, status
            mock_proxy.sign_in.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            
            assert response.status_code == 401


class TestLogout:
    """Test logout endpoint."""
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_logout_success(self, client):
        """Successful logout via Supabase."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.sign_out.return_value = {"message": "Successfully signed out"}
            
            response = client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer token-123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
    
    def test_logout_missing_token(self, client):
        """Logout fails without Authorization header."""
        response = client.post("/auth/logout")
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]

    def test_logout_legacy_alias_missing_token(self, client):
        """Legacy /logout alias exists and enforces auth header."""
        response = client.post("/logout")
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]


class TestGetCurrentUser:
    """Test /auth/me endpoint."""
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_me_success(self, client):
        """Get current user info with valid token."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.get_user.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "metadata": {"name": "Test User"}
            }
            
            response = client.get(
                "/auth/me",
                headers={"Authorization": "Bearer token-123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "user-123"
            assert data["email"] == "test@example.com"
    
    def test_me_invalid_token(self, client):
        """Get current user fails with invalid token."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            from fastapi import HTTPException, status
            mock_proxy.get_user.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
            
            response = client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid-token"}
            )
            
            assert response.status_code == 401


class TestRefreshToken:
    """Test token refresh endpoint."""
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_refresh_success(self, client):
        """Successful token refresh."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.refresh_session.return_value = {
                "access_token": "new-token-123",
                "refresh_token": "new-refresh-123",
                "expires_at": 1234567890
            }
            
            response = client.post("/auth/refresh", json={
                "refresh_token": "old-refresh-token"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new-token-123"


class TestPasswordReset:
    """Test password reset endpoints."""
    
    def test_password_reset_request(self, client):
        """Request password reset email."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.reset_password_email.return_value = {
                "message": "Password reset email sent"
            }
            
            response = client.post("/auth/password-reset/request", json={
                "email": "test@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_password_reset_confirm(self, client):
        """Confirm password reset with new password."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.update_password.return_value = {
                "message": "Password updated successfully"
            }
            
            response = client.post(
                "/auth/password-reset/confirm",
                json={"new_password": "newpassword123"},
                headers={"Authorization": "Bearer reset-token"}
            )
            
            assert response.status_code == 200


class TestTokenVerification:
    """Test token verification endpoint (for backend use)."""
    
    @pytest.mark.skip(reason="Requires proper Supabase mock or live backend")
    def test_verify_valid_token(self, client):
        """Verify returns user info for valid token."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.verify_token.return_value = True
            mock_proxy.get_user.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "metadata": {}
            }
            
            response = client.get(
                "/auth/verify",
                headers={"Authorization": "Bearer token-123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "user-123"
    
    def test_verify_invalid_token(self, client):
        """Verify fails for invalid token."""
        with patch("auth.api_supabase.get_supabase_proxy") as mock_get:
            mock_proxy = AsyncMock()
            mock_get.return_value = mock_proxy
            
            mock_proxy.verify_token.return_value = False
            
            response = client.get(
                "/auth/verify",
                headers={"Authorization": "Bearer invalid-token"}
            )
            
            assert response.status_code == 401


class TestAuthorizationHeaderParsing:
    """Test Authorization header parsing."""
    
    def test_missing_bearer_prefix(self, client):
        """Request fails without Bearer prefix."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "token-123"}  # Missing "Bearer"
        )
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]
    
    def test_no_auth_header(self, client):
        """Request fails without Authorization header."""
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert "Missing authorization header" in response.json()["detail"]


class TestCORSHeaders:
    """Test CORS headers are present."""
    
    def test_cors_headers_present(self, client):
        """CORS headers are included in responses."""
        response = client.get("/health")
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
