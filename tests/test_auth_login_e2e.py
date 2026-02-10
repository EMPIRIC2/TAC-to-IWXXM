"""End-to-end tests for authentication login functionality.

Tests the complete login flow including:
- Email validation for development domains (.local, .test, etc.)
- Successful authentication with valid credentials
- Session token generation
- CORS headers in responses
"""
import pytest
import requests
from typing import Dict, Any

# Configuration
AUTH_SERVICE_URL = "http://localhost:8002"
ADMIN_EMAIL = "admin@metar.local"
ADMIN_PASSWORD = "Admin123456!"


@pytest.fixture(scope="module")
def auth_service_available():
    """Check if auth service is running."""
    try:
        response = requests.get(f"{AUTH_SERVICE_URL}/health", timeout=5)
        assert response.status_code == 200
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.skip("Auth service not running on http://localhost:8002")


class TestAuthLoginE2E:
    """End-to-end tests for login functionality."""
    
    def test_health_check(self, auth_service_available):
        """Test that auth service is healthy."""
        response = requests.get(f"{AUTH_SERVICE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth"
    
    def test_cors_preflight_login(self, auth_service_available):
        """Test CORS preflight request for login endpoint."""
        response = requests.options(
            f"{AUTH_SERVICE_URL}/auth/login",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "POST" in response.headers.get("access-control-allow-methods", "")
    
    def test_login_with_valid_admin_credentials(self, auth_service_available):
        """Test successful login with admin credentials."""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:8000",
            },
            timeout=10,
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify user data structure
        assert "user" in data
        assert "session" in data
        
        user = data["user"]
        assert user["id"] == "27f7a37c-5575-4e19-a6d6-338755caec1d"
        assert user["email"] == ADMIN_EMAIL
        assert "metadata" in user
        
        # Verify session data structure
        session = data["session"]
        assert "access_token" in session
        assert "refresh_token" in session
        assert "expires_at" in session
        assert isinstance(session["expires_at"], int)
        assert session["expires_at"] > 0
        
        # Verify CORS headers
        assert response.headers.get("access-control-allow-origin") in ["*", "http://localhost:8000"]
        assert response.headers.get("access-control-allow-credentials") == "true"
    
    def test_login_with_invalid_credentials(self, auth_service_available):
        """Test login failure with wrong password."""
        payload = {
            "email": ADMIN_EMAIL,
            "password": "WrongPassword123!",
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data
    
    def test_login_with_nonexistent_email(self, auth_service_available):
        """Test login with non-existent email."""
        payload = {
            "email": "nonexistent@metar.local",
            "password": "Password123!",
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_response_includes_metadata(self, auth_service_available):
        """Test that login response includes user metadata."""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        metadata = data["user"]["metadata"]
        assert isinstance(metadata, dict)
        assert "email_verified" in metadata
        assert metadata["email_verified"] is True
        assert "username" in metadata
        assert metadata["username"] == "admin"
    
    def test_email_validation_allows_local_domain(self, auth_service_available):
        """Test that .local domain emails are accepted."""
        # This test verifies that the email validation passes .local domains
        payload = {
            "email": ADMIN_EMAIL,  # Uses .local domain
            "password": ADMIN_PASSWORD,
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        # Verify that it didn't fail due to email validation
        # (it may fail due to credentials, but not validation)
        assert response.status_code in [200, 401]
        assert response.status_code != 422  # 422 is validation error
    
    def test_multiple_login_requests(self, auth_service_available):
        """Test handling of multiple sequential login requests."""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        }
        
        for _ in range(3):
            response = requests.post(
                f"{AUTH_SERVICE_URL}/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "user" in data
            assert "session" in data
    
    def test_login_missing_email(self, auth_service_available):
        """Test that login fails when email is missing."""
        payload = {
            "password": ADMIN_PASSWORD,
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_password(self, auth_service_available):
        """Test that login fails when password is missing."""
        payload = {
            "email": ADMIN_EMAIL,
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_session_token_structure(self, auth_service_available):
        """Test that session tokens have expected structure."""
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        }
        
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        
        assert response.status_code == 200
        data = response.json()
        session = data["session"]
        
        # Access token should be a JWT (contains dots)
        assert session["access_token"].count(".") >= 2
        
        # Refresh token should be a string
        assert isinstance(session["refresh_token"], str)
        assert len(session["refresh_token"]) > 0
        
        # Expiry should be a future timestamp
        import time
        current_time = int(time.time())
        assert session["expires_at"] > current_time
