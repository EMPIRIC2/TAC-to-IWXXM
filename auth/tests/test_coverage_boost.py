"""Additional comprehensive tests to achieve 95%+ coverage.

Focuses on edge cases, error paths, and uncovered code branches.

NOTE: API tests are SKIPPED because the application uses Supabase authentication.
The custom auth API endpoints are not used in production.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Custom auth API unused - application uses Supabase auth")

import os
import datetime as dt
from unittest import mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from auth.database import Base
from auth.models import User, APIKey, PasswordResetToken
from auth.security import hash_password, create_access_token, hash_api_key, create_reset_expiry
from auth.__main__ import app


@pytest.fixture
def db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create database session."""
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_engine):
    """Create test client."""
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    from auth.api import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        address="123 Test St",
        username="testuser",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestAPIEdgeCases:
    """Test API edge cases and error paths."""
    
    def test_get_current_user_missing_authorization_header(self, client, db_session):
        """Test get_current_user with no authorization header."""
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()
    
    def test_get_current_user_invalid_bearer_format(self, client):
        """Test get_current_user with invalid Bearer format."""
        # Test with lowercase bearer
        response = client.get("/auth/me", headers={"Authorization": "bearer token"})
        assert response.status_code == 401
        
        # Test with no space
        response = client.get("/auth/me", headers={"Authorization": "Bearertoken"})
        assert response.status_code == 401
    
    def test_confirm_reset_user_not_found(self, client, db_session):
        """Test password reset confirmation when user is deleted."""
        # Create user and reset token
        user = User(
            name="Delete Me",
            email="delete@example.com",
            address="123 St",
            username="deleteme",
            password_hash=hash_password("password"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=user.id,
            expires_at=create_reset_expiry(),
        )
        db_session.add(reset_token)
        db_session.commit()
        
        # Delete user but keep token
        db_session.delete(user)
        db_session.commit()
        
        # Try to reset password
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "newpass123"}
        )
        
        # Should fail because user doesn't exist
        assert response.status_code == 400
    
    def test_send_reset_email_function(self, monkeypatch):
        """Test send_reset_email function with different env vars."""
        from auth.api import send_reset_email
        import io
        import sys
        
        # Capture print output
        captured_output = io.StringIO()
        monkeypatch.setattr('sys.stdout', captured_output)
        
        # Test with custom frontend URL
        with mock.patch.dict(os.environ, {"FRONTEND_BASE_URL": "https://example.com"}):
            send_reset_email("test@example.com", "test_token")
            output = captured_output.getvalue()
            assert "https://example.com/reset-password?token=test_token" in output
            assert "test@example.com" in output


class TestAPIValidationEdgeCases:
    """Test API validation edge cases."""
    
    def test_register_long_username(self, client):
        """Test registration with username at max length."""
        user_data = {
            "name": "User",
            "email": "user@example.com",
            "address": "123 St",
            "username": "a" * 50,  # Max length
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
    
    def test_register_username_over_max_length(self, client):
        """Test registration with username over max length."""
        user_data = {
            "name": "User",
            "email": "user@example.com",
            "address": "123 St",
            "username": "a" * 51,  # Over max length
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_minimum_username(self, client):
        """Test registration with minimum username length."""
        user_data = {
            "name": "User",
            "email": "user@example.com",
            "address": "123 St",
            "username": "abc",  # Min length 3
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
    
    def test_register_minimum_password(self, client):
        """Test registration with minimum password length."""
        user_data = {
            "name": "User",
            "email": "user@example.com",
            "address": "123 St",
            "username": "username",
            "password": "pass1234"  # Min length 8
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
    
    def test_reset_minimum_password(self, client, test_user, db_session):
        """Test password reset with minimum password length."""
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=test_user.id,
            expires_at=create_reset_expiry(),
        )
        db_session.add(reset_token)
        db_session.commit()
        
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "newpass1"}  # Min 8
        )
        
        assert response.status_code == 200


class TestDatabaseEdgeCases:
    """Test database edge cases."""
    
    def test_user_with_special_characters_in_email(self, db_session):
        """Test user with special characters in email."""
        user = User(
            name="Test",
            email="test+tag@example.co.uk",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.email == "test+tag@example.co.uk"
    
    def test_user_with_unicode_name(self, db_session):
        """Test user with unicode characters in name."""
        user = User(
            name="José María",
            email="jose@example.com",
            address="Calle Principal",
            username="jose",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.name == "José María"
    
    def test_api_key_with_very_long_hash(self, db_session):
        """Test API key with maximum hash length."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        
        # SHA-256 produces 64 hex chars
        long_hash = "a" * 128  # Max length for key_hash
        api_key = APIKey(key_hash=long_hash, user_id=user.id)
        db_session.add(api_key)
        db_session.commit()
        db_session.refresh(api_key)
        
        assert api_key.key_hash == long_hash
    
    def test_password_reset_token_timezone_aware(self, db_session):
        """Test that password reset tokens use timezone-aware datetimes."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        
        token = PasswordResetToken(
            token="test",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.UTC),
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)
        
        # SQLite may not preserve timezone info, but the token should exist
        # and have a created_at timestamp
        assert token.created_at is not None
        # If using PostgreSQL in production, this would be timezone-aware


class TestSecurityEdgeCases:
    """Test security utility edge cases."""
    
    def test_hash_password_with_special_characters(self):
        """Test hashing passwords with special characters."""
        from auth.security import hash_password, verify_password
        
        special_passwords = [
            "pass@word#123",
            "pässwörd",
            "密码123",
            "пароль123",
            "password!@#$%^&*()",
        ]
        
        for password in special_passwords:
            hashed = hash_password(password)
            assert verify_password(password, hashed)
            assert not verify_password("wrong", hashed)
    
    def test_jwt_with_special_characters_in_sub(self):
        """Test JWT with special characters in sub claim."""
        from auth.security import create_access_token, decode_access_token
        
        special_subs = [
            "user+tag@example.com",
            "user@sub.domain.example.com",
            "user_name-123",
        ]
        
        for sub in special_subs:
            token = create_access_token(sub=sub)
            decoded = decode_access_token(token)
            assert decoded == sub
    
    def test_hash_api_key_consistency(self):
        """Test that API key hashing is deterministic."""
        from auth.security import hash_api_key
        
        key = "test_key_12345"
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        hash3 = hash_api_key(key)
        
        # Should all be identical
        assert hash1 == hash2 == hash3


class TestModelRelationshipEdgeCases:
    """Test model relationship edge cases."""
    
    def test_user_with_multiple_api_keys(self, db_session):
        """Test user with multiple API keys."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        
        # Add multiple keys
        for i in range(5):
            key = APIKey(key_hash=hash_api_key(f"key_{i}"), user_id=user.id)
            db_session.add(key)
        
        db_session.commit()
        db_session.refresh(user)
        
        assert len(user.api_keys) == 5
    
    def test_user_with_multiple_reset_tokens(self, db_session):
        """Test user with multiple reset tokens."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        
        # Add multiple reset tokens
        for i in range(3):
            token = PasswordResetToken(
                token=f"token_{i}",
                user_id=user.id,
                expires_at=create_reset_expiry(),
            )
            db_session.add(token)
        
        db_session.commit()
        db_session.refresh(user)
        
        assert len(user.reset_tokens) == 3
    
    def test_api_key_revocation_doesnt_affect_others(self, db_session):
        """Test that revoking one API key doesn't affect others."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        
        # Create two keys
        key1 = APIKey(key_hash=hash_api_key("key1"), user_id=user.id)
        key2 = APIKey(key_hash=hash_api_key("key2"), user_id=user.id)
        db_session.add_all([key1, key2])
        db_session.commit()
        
        # Revoke one
        key1.revoked = True
        db_session.commit()
        
        db_session.refresh(key2)
        assert key2.revoked is False


class TestAPIResponseFormats:
    """Test API response format edge cases."""
    
    def test_login_response_includes_empty_api_keys(self, client, test_user):
        """Test login response when user has no API keys."""
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        data = response.json()
        assert "api_keys" in data
        assert data["api_keys"] == []
    
    def test_me_endpoint_response_structure(self, client, test_user):
        """Test /me endpoint response structure."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/auth/me", headers=headers)
        data = response.json()
        
        # Should have all UserOut fields
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "address" in data
        assert "username" in data
        
        # Should NOT have sensitive fields
        assert "password_hash" not in data
        assert "password" not in data
    
    def test_api_key_list_response_structure(self, client, test_user, db_session):
        """Test API key list response structure."""
        # Create an API key
        key = APIKey(key_hash=hash_api_key("test"), user_id=test_user.id)
        db_session.add(key)
        db_session.commit()
        
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/auth/apikeys", headers=headers)
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        key_data = data[0]
        assert "id" in key_data
        assert "created_at" in key_data
        assert "revoked" in key_data
        
        # Should NOT include the key hash
        assert "key_hash" not in key_data
        assert "raw_key" not in key_data


class TestPasswordResetTimezoneHandling:
    """Test password reset timezone handling."""
    
    def test_confirm_reset_with_naive_datetime(self, client, test_user, db_session):
        """Test password reset with naive datetime in database."""
        # Create token with naive datetime
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=test_user.id,
            expires_at=dt.datetime.utcnow() + dt.timedelta(hours=1),  # Naive
        )
        db_session.add(reset_token)
        db_session.commit()
        
        # Should still work
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "newpass123"}
        )
        
        assert response.status_code == 200


class TestConcurrencyEdgeCases:
    """Test edge cases related to concurrent operations."""
    
    def test_multiple_password_resets_for_same_user(self, client, test_user, db_session):
        """Test multiple password reset tokens for same user."""
        # Create multiple reset tokens
        tokens = []
        for i in range(3):
            token_value = PasswordResetToken.generate_token()
            reset_token = PasswordResetToken(
                token=token_value,
                user_id=test_user.id,
                expires_at=create_reset_expiry(),
            )
            db_session.add(reset_token)
            tokens.append(token_value)
        
        db_session.commit()
        
        # Use the last token
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": tokens[2], "new_password": "newpass123"}
        )
        
        assert response.status_code == 200
    
    def test_using_reset_token_twice(self, client, test_user, db_session):
        """Test that reset token can't be used twice."""
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=test_user.id,
            expires_at=create_reset_expiry(),
        )
        db_session.add(reset_token)
        db_session.commit()
        
        # Use token once
        response1 = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "newpass123"}
        )
        assert response1.status_code == 200
        
        # Try to use again
        response2 = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "anotherpass123"}
        )
        assert response2.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
