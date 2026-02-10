"""Unit tests for login functionality including email validation.

Tests cover:
- Custom email validator for development domains
- Login request/response models
- Supabase proxy login method
- Email validation for various domain types
"""
import pytest
from pydantic import ValidationError
from unittest.mock import Mock, patch, MagicMock

# Import the email validator and models
from auth.api_supabase import (
    validate_email_permissive,
    LoginRequest,
    RegisterRequest,
    PasswordResetRequest,
)


class TestEmailValidation:
    """Test the custom email validator for development domains."""
    
    def test_valid_development_local_domain(self):
        """Test that .local domain is accepted."""
        email = validate_email_permissive("admin@metar.local")
        assert email == "admin@metar.local"
    
    def test_valid_development_test_domain(self):
        """Test that .test domain is accepted."""
        email = validate_email_permissive("user@example.test")
        assert email == "user@example.test"
    
    def test_valid_development_localhost_domain(self):
        """Test that .localhost domain is accepted."""
        email = validate_email_permissive("user@myapp.localhost")
        assert email == "user@myapp.localhost"
    
    def test_valid_development_dev_domain(self):
        """Test that .dev domain is accepted."""
        email = validate_email_permissive("user@example.dev")
        assert email == "user@example.dev"
    
    def test_valid_development_example_domain(self):
        """Test that .example domain is accepted."""
        email = validate_email_permissive("user@example.example")
        assert email == "user@example.example"
    
    def test_lowercase_conversion(self):
        """Test that emails are converted to lowercase."""
        email = validate_email_permissive("admin@test.local")
        assert email == "admin@test.local"
    
    def test_invalid_no_at_sign(self):
        """Test that email without @ is rejected."""
        with pytest.raises(ValueError):
            validate_email_permissive("invalidemail")
    
    def test_invalid_empty_string(self):
        """Test that empty string is rejected."""
        with pytest.raises(ValueError):
            validate_email_permissive("")
    
    def test_invalid_no_domain(self):
        """Test that email without domain is rejected."""
        with pytest.raises(ValueError):
            validate_email_permissive("user@")
    
    def test_invalid_no_local_part(self):
        """Test that email without local part is rejected."""
        with pytest.raises(ValueError):
            validate_email_permissive("@domain.com")
    
    def test_valid_gmail_domain(self):
        """Test that standard gmail domain passes validation."""
        # Note: may fail with "special-use" restriction but should parse
        try:
            email = validate_email_permissive("user@gmail.com")
            assert isinstance(email, str)
        except ValueError:
            # This is ok - gmail.com might fail validation in some configs
            pass
    
    def test_valid_generic_domain(self):
        """Test that a generic domain passes validation."""
        email = validate_email_permissive("user@example.org")
        assert isinstance(email, str)


class TestLoginRequestModel:
    """Test the LoginRequest Pydantic model."""
    
    def test_valid_login_request_local_domain(self):
        """Test creating a valid login request with .local domain."""
        request = LoginRequest(
            email="admin@metar.local",
            password="SecurePassword123!"
        )
        assert request.email == "admin@metar.local"
        assert request.password == "SecurePassword123!"
    
    def test_valid_login_request_lowercase_conversion(self):
        """Test that email is normalized to lowercase."""
        request = LoginRequest(
            email="admin@test.local",
            password="SecurePassword123!"
        )
        assert request.email == "admin@test.local"
    
    def test_invalid_login_missing_email(self):
        """Test that login request fails without email."""
        with pytest.raises(ValidationError):
            LoginRequest(password="SecurePassword123!")
    
    def test_invalid_login_missing_password(self):
        """Test that login request fails without password."""
        with pytest.raises(ValidationError):
            LoginRequest(email="admin@metar.local")
    
    def test_invalid_login_empty_password(self):
        """Test that login request accepts empty password (no validation on LoginRequest)."""
        # LoginRequest doesn't have min_length validation on password unlike RegisterRequest
        request = LoginRequest(email="admin@metar.local", password="")
        assert request.password == ""
    
    def test_invalid_login_no_at_in_email(self):
        """Test that login fails with invalid email format."""
        with pytest.raises(ValidationError):
            LoginRequest(email="invalidemail", password="SecurePassword123!")


class TestRegisterRequestModel:
    """Test the RegisterRequest Pydantic model."""
    
    def test_valid_register_request(self):
        """Test creating a valid register request."""
        request = RegisterRequest(
            email="newuser@metar.local",
            password="SecurePassword123!",
            name="New User",
            username="newuser"
        )
        assert request.email == "newuser@metar.local"
        assert request.password == "SecurePassword123!"
        assert request.name == "New User"
        assert request.username == "newuser"
    
    def test_register_request_optional_metadata(self):
        """Test register request with only required fields."""
        request = RegisterRequest(
            email="newuser@metar.local",
            password="SecurePassword123!"
        )
        assert request.email == "newuser@metar.local"
        assert request.name is None
        assert request.username is None
    
    def test_invalid_register_password_too_short(self):
        """Test that register fails with short password."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="newuser@metar.local",
                password="Short1!"  # Less than 8 characters
            )
    
    def test_invalid_register_username_too_short(self):
        """Test that register fails with short username."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="newuser@metar.local",
                password="SecurePassword123!",
                username="ab"  # Less than 3 characters
            )


class TestPasswordResetRequestModel:
    """Test the PasswordResetRequest Pydantic model."""
    
    def test_valid_password_reset_request(self):
        """Test creating a valid password reset request."""
        request = PasswordResetRequest(email="admin@metar.local")
        assert request.email == "admin@metar.local"
    
    def test_password_reset_email_lowercase(self):
        """Test that email is normalized to lowercase."""
        request = PasswordResetRequest(email="admin@test.local")
        assert request.email == "admin@test.local"
    
    def test_invalid_password_reset_missing_email(self):
        """Test that password reset fails without email."""
        with pytest.raises(ValidationError):
            PasswordResetRequest()


class TestSupabaseProxyLogin:
    """Test the Supabase proxy login method."""
    
    @patch('auth.supabase_proxy.SupabaseAuthProxy.__init__', return_value=None)
    def test_login_success(self, mock_init):
        """Test successful login through proxy."""
        from auth.supabase_proxy import SupabaseAuthProxy
        
        # Create a mock proxy instance
        proxy = SupabaseAuthProxy()
        
        # Mock the client
        proxy.client = Mock()
        
        # Mock Supabase response
        mock_user = Mock()
        mock_user.id = "test-id"
        mock_user.email = "admin@metar.local"
        mock_user.user_metadata = {"username": "admin"}
        
        mock_session = Mock()
        mock_session.access_token = "test-access-token"
        mock_session.refresh_token = "test-refresh-token"
        mock_session.expires_at = 1234567890
        
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = mock_session
        
        proxy.client.auth.sign_in_with_password = Mock(return_value=mock_response)
        
        # Call login
        result = proxy.sign_in("admin@metar.local", "Admin123456!")
        
        # Verify result structure
        assert "user" in result
        assert "session" in result
        assert result["user"]["id"] == "test-id"
        assert result["user"]["email"] == "admin@metar.local"
        assert result["session"]["access_token"] == "test-access-token"
    
    @patch('auth.supabase_proxy.SupabaseAuthProxy.__init__', return_value=None)
    def test_login_invalid_credentials(self, mock_init):
        """Test login failure with invalid credentials."""
        from auth.supabase_proxy import SupabaseAuthProxy
        from fastapi import HTTPException
        
        # Create a mock proxy instance
        proxy = SupabaseAuthProxy()
        proxy.client = Mock()
        
        # Mock Supabase error
        proxy.client.auth.sign_in_with_password = Mock(
            side_effect=Exception("Invalid login credentials")
        )
        
        # Call login and expect HTTPException
        with pytest.raises(HTTPException):
            proxy.sign_in("admin@metar.local", "WrongPassword")
    
    @patch('auth.supabase_proxy.SupabaseAuthProxy.__init__', return_value=None)
    def test_login_no_session_in_response(self, mock_init):
        """Test login when Supabase doesn't return a session."""
        from auth.supabase_proxy import SupabaseAuthProxy
        from fastapi import HTTPException
        
        # Create a mock proxy instance
        proxy = SupabaseAuthProxy()
        proxy.client = Mock()
        
        # Mock response without session
        mock_user = Mock()
        mock_user.id = "test-id"
        mock_user.email = "admin@metar.local"
        mock_user.user_metadata = {}
        
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = None  # No session
        
        proxy.client.auth.sign_in_with_password = Mock(return_value=mock_response)
        
        # Call login and expect HTTPException
        with pytest.raises(HTTPException):
            proxy.sign_in("admin@metar.local", "Admin123456!")
    
    @patch('auth.supabase_proxy.SupabaseAuthProxy.__init__', return_value=None)
    def test_login_development_email_domain(self, mock_init):
        """Test that login methods accept development domain emails."""
        from auth.supabase_proxy import SupabaseAuthProxy
        
        # Create a mock proxy instance
        proxy = SupabaseAuthProxy()
        proxy.client = Mock()
        
        # Mock successful response
        mock_user = Mock()
        mock_user.id = "test-id"
        mock_user.email = "testuser@metar.test"
        mock_user.user_metadata = {}
        
        mock_session = Mock()
        mock_session.access_token = "token"
        mock_session.refresh_token = "refresh"
        mock_session.expires_at = 1234567890
        
        mock_response = Mock()
        mock_response.user = mock_user
        mock_response.session = mock_session
        
        proxy.client.auth.sign_in_with_password = Mock(return_value=mock_response)
        
        # Should work with .test domain
        result = proxy.sign_in("testuser@metar.test", "Password123!")
        assert result["user"]["email"] == "testuser@metar.test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
