"""Comprehensive unit tests for auth.api module.

Tests all API endpoints with various scenarios.
Target: 95%+ coverage.

NOTE: These tests are SKIPPED because the application uses Supabase authentication.
The custom auth API endpoints are not used in production.
Keeping for reference/documentation purposes.
"""
import pytest
import datetime as dt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest import mock

pytestmark = pytest.mark.skip(reason="Custom auth API unused - application uses Supabase auth")

from auth.database import Base
from auth.models import User, APIKey, PasswordResetToken
from auth.security import hash_password, create_access_token, hash_api_key, create_reset_expiry
from auth.__main__ import app


@pytest.fixture(scope="function")
def test_db():
    """Create a test database with tables."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_db: Session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    from auth.api import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db: Session):
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        address="123 Test St",
        username="testuser",
        password_hash=hash_password("testpass123"),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns correct response."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth"
        assert data["version"] == "0.1.0"


class TestRegisterEndpoint:
    """Test user registration endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "address": "456 New St",
            "username": "newuser",
            "password": "securepass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["address"] == "456 New St"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username fails."""
        user_data = {
            "name": "Another User",
            "email": "another@example.com",
            "address": "789 St",
            "username": "testuser",  # Same as test_user
            "password": "securepass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        user_data = {
            "name": "Another User",
            "email": "test@example.com",  # Same as test_user
            "address": "789 St",
            "username": "anotheruser",
            "password": "securepass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_short_username(self, client):
        """Test registration with too short username fails."""
        user_data = {
            "name": "User",
            "email": "user@example.com",
            "address": "123 St",
            "username": "ab",  # Too short (min 3)
            "password": "securepass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password(self, client):
        """Test registration with too short password fails."""
        user_data = {
            "name": "User",
            "email": "user@example.com",
            "address": "123 St",
            "username": "username",
            "password": "short"  # Too short (min 8)
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        user_data = {
            "name": "User",
            "email": "not-an-email",
            "address": "123 St",
            "username": "username",
            "password": "securepass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestLoginEndpoint:
    """Test user login endpoint."""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
        assert isinstance(data["api_keys"], list)
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_returns_api_keys(self, client, test_user, db_session):
        """Test that login returns user's API key IDs."""
        # Create API keys for user
        key1 = APIKey(key_hash=hash_api_key("key1"), user_id=test_user.id)
        key2 = APIKey(key_hash=hash_api_key("key2"), user_id=test_user.id, revoked=True)
        db_session.add_all([key1, key2])
        db_session.commit()
        
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = client.post("/auth/login", json=login_data)
        data = response.json()
        
        # Should only return non-revoked keys
        assert len(data["api_keys"]) == 1


class TestMeEndpoint:
    """Test the /me endpoint for getting current user."""
    
    def test_me_success(self, client, test_user):
        """Test getting current user info."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_me_no_token(self, client):
        """Test /me without token fails."""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_me_invalid_token(self, client):
        """Test /me with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_me_no_bearer_prefix(self, client, test_user):
        """Test /me without Bearer prefix fails."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": token}  # Missing "Bearer "
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_me_nonexistent_user(self, client):
        """Test /me with token for nonexistent user fails."""
        token = create_access_token(sub="nonexistent")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401


class TestAPIKeyEndpoints:
    """Test API key management endpoints."""
    
    def test_create_api_key(self, client, test_user):
        """Test creating an API key."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/auth/apikeys", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "raw_key" in data
        assert len(data["raw_key"]) > 20
    
    def test_create_api_key_unauthorized(self, client):
        """Test creating API key without auth fails."""
        response = client.post("/auth/apikeys")
        
        assert response.status_code == 401
    
    def test_list_api_keys(self, client, test_user, db_session):
        """Test listing API keys."""
        # Create API keys
        key1 = APIKey(key_hash=hash_api_key("key1"), user_id=test_user.id)
        key2 = APIKey(key_hash=hash_api_key("key2"), user_id=test_user.id)
        db_session.add_all([key1, key2])
        db_session.commit()
        
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/auth/apikeys", headers=headers)
        
        assert response.status_code == 200
        keys = response.json()
        assert len(keys) >= 2
        assert all("id" in k for k in keys)
        assert all("created_at" in k for k in keys)
        assert all("revoked" in k for k in keys)
    
    def test_list_api_keys_unauthorized(self, client):
        """Test listing API keys without auth fails."""
        response = client.get("/auth/apikeys")
        
        assert response.status_code == 401
    
    def test_revoke_api_key(self, client, test_user, db_session):
        """Test revoking an API key."""
        key = APIKey(key_hash=hash_api_key("key"), user_id=test_user.id)
        db_session.add(key)
        db_session.commit()
        db_session.refresh(key)
        
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/auth/apikeys/{key.id}", headers=headers)
        
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify it's revoked
        db_session.refresh(key)
        assert key.revoked is True
    
    def test_revoke_api_key_not_found(self, client, test_user):
        """Test revoking nonexistent API key fails."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete("/auth/apikeys/99999", headers=headers)
        
        assert response.status_code == 404
    
    def test_revoke_api_key_unauthorized(self, client, db_session):
        """Test revoking API key without auth fails."""
        # Create a user and key
        user = User(
            name="User",
            email="user@test.com",
            address="123 St",
            username="user",
            password_hash=hash_password("pass"),
        )
        db_session.add(user)
        db_session.commit()
        
        key = APIKey(key_hash=hash_api_key("key"), user_id=user.id)
        db_session.add(key)
        db_session.commit()
        
        response = client.delete(f"/auth/apikeys/{key.id}")
        
        assert response.status_code == 401
    
    def test_revoke_other_users_key(self, client, test_user, db_session):
        """Test that users cannot revoke other users' keys."""
        # Create another user
        other_user = User(
            name="Other",
            email="other@test.com",
            address="456 St",
            username="other",
            password_hash=hash_password("pass"),
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create key for other user
        key = APIKey(key_hash=hash_api_key("key"), user_id=other_user.id)
        db_session.add(key)
        db_session.commit()
        db_session.refresh(key)
        
        # Try to revoke as test_user
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/auth/apikeys/{key.id}", headers=headers)
        
        assert response.status_code == 404  # Not found (filtered by user_id)


class TestPasswordResetEndpoints:
    """Test password reset endpoints."""
    
    def test_request_reset(self, client, test_user):
        """Test requesting a password reset."""
        response = client.post(
            "/auth/password-reset/request",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_request_reset_nonexistent_email(self, client):
        """Test requesting reset for nonexistent email."""
        response = client.post(
            "/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        
        # Should still return success (prevent email enumeration)
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_confirm_reset_success(self, client, test_user, db_session):
        """Test confirming password reset with valid token."""
        # Create reset token
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=test_user.id,
            expires_at=create_reset_expiry(),
        )
        db_session.add(reset_token)
        db_session.commit()
        
        new_password = "newpassword123"
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": new_password}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify token is marked as used
        db_session.refresh(reset_token)
        assert reset_token.used is True
        
        # Verify password was changed
        db_session.refresh(test_user)
        from auth.security import verify_password
        assert verify_password(new_password, test_user.password_hash)
    
    def test_confirm_reset_invalid_token(self, client):
        """Test confirming reset with invalid token."""
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": "invalid_token", "new_password": "newpass123"}
        )
        
        assert response.status_code == 400
        assert "invalid or expired" in response.json()["detail"].lower()
    
    def test_confirm_reset_expired_token(self, client, test_user, db_session):
        """Test confirming reset with expired token."""
        # Create expired token
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=test_user.id,
            expires_at=dt.datetime.now(dt.UTC) - dt.timedelta(hours=1),
        )
        db_session.add(reset_token)
        db_session.commit()
        
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "newpass123"}
        )
        
        assert response.status_code == 400
        assert "invalid or expired" in response.json()["detail"].lower()
    
    def test_confirm_reset_used_token(self, client, test_user, db_session):
        """Test confirming reset with already used token."""
        # Create used token
        token_value = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token_value,
            user_id=test_user.id,
            expires_at=create_reset_expiry(),
            used=True,
        )
        db_session.add(reset_token)
        db_session.commit()
        
        response = client.post(
            "/auth/password-reset/confirm",
            json={"token": token_value, "new_password": "newpass123"}
        )
        
        assert response.status_code == 400
        assert "invalid or expired" in response.json()["detail"].lower()
    
    def test_confirm_reset_short_password(self, client, test_user, db_session):
        """Test confirming reset with too short password."""
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
            json={"token": token_value, "new_password": "short"}
        )
        
        assert response.status_code == 422  # Validation error


class TestSendResetEmail:
    """Test the send_reset_email function."""
    
    def test_send_reset_email_called(self, client, test_user, monkeypatch):
        """Test that send_reset_email is called during request."""
        called = []
        
        def mock_send(email, token):
            called.append((email, token))
        
        monkeypatch.setattr("auth.api.send_reset_email", mock_send)
        
        response = client.post(
            "/auth/password-reset/request",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        assert len(called) == 1
        assert called[0][0] == test_user.email


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
