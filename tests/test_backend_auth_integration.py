"""Integration tests for backend and auth services.

Tests the integration between the authentication service and the METAR conversion backend,
ensuring that JWT tokens from auth can be used to access backend endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import from auth service
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'auth', 'src'))

from auth.database import Base as AuthBase
from auth.models import User
from auth.security import hash_password, create_access_token
from auth.__main__ import app as auth_app

# Import from backend service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))
# Backend uses Supabase auth, but we can test the pattern


@pytest.fixture
def auth_db_engine():
    """Create a test database engine for auth service."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    AuthBase.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def auth_db_session(auth_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(bind=auth_db_engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def auth_client(auth_db_engine, monkeypatch):
    """Create a test client for the auth service."""
    from auth.database import SessionLocal
    
    TestingSessionLocal = sessionmaker(bind=auth_db_engine, autoflush=False, autocommit=False)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Patch the SessionLocal
    monkeypatch.setattr("auth.database.SessionLocal", TestingSessionLocal)
    
    client = TestClient(auth_app)
    return client


@pytest.fixture
def test_user(auth_db_session):
    """Create a test user in the auth database."""
    user = User(
        name="Test User",
        email="test@example.com",
        address="123 Test St",
        username="testuser",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    auth_db_session.add(user)
    auth_db_session.commit()
    auth_db_session.refresh(user)
    return user


class TestAuthServiceIntegration:
    """Test the auth service in isolation."""
    
    def test_health_check(self, auth_client):
        """Test that the auth service health endpoint works."""
        response = auth_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth"
        assert data["version"] == "0.1.0"
    
    def test_register_user(self, auth_client):
        """Test user registration flow."""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "address": "456 New St",
            "username": "newuser",
            "password": "securepass123"
        }
        
        response = auth_client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data
        assert "password_hash" not in data
    
    def test_login_returns_token(self, auth_client, test_user):
        """Test that login returns a valid JWT token."""
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = auth_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
    
    def test_authenticated_endpoint_requires_token(self, auth_client):
        """Test that /auth/me requires authentication."""
        # Without token
        response = auth_client.get("/auth/me")
        assert response.status_code == 401
        
    def test_authenticated_endpoint_with_valid_token(self, auth_client, test_user):
        """Test that /auth/me works with valid token."""
        # Get token
        token = create_access_token(sub=test_user.username)
        
        # Use token
        headers = {"Authorization": f"Bearer {token}"}
        response = auth_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"


class TestAuthTokenGeneration:
    """Test JWT token generation and validation."""
    
    def test_create_and_validate_token(self):
        """Test that we can create and validate a JWT token."""
        from auth.security import create_access_token, decode_access_token
        
        username = "testuser"
        token = create_access_token(sub=username)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Decode and verify
        decoded = decode_access_token(token)
        assert decoded == username
    
    def test_invalid_token_returns_none(self):
        """Test that invalid tokens are rejected."""
        from auth.security import decode_access_token
        
        invalid_token = "invalid.token.here"
        result = decode_access_token(invalid_token)
        assert result is None
    
    def test_expired_token_returns_none(self):
        """Test that expired tokens are rejected."""
        import datetime as dt
        from jose import jwt
        from auth.security import JWT_SECRET, JWT_ALGO, decode_access_token
        
        # Create expired token
        expire = dt.datetime.now(dt.UTC) - dt.timedelta(minutes=1)
        payload = {"sub": "testuser", "exp": expire}
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        
        result = decode_access_token(expired_token)
        assert result is None


class TestAPIKeyManagement:
    """Test API key generation and management."""
    
    def test_create_api_key(self, auth_client, test_user):
        """Test creating an API key for a user."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = auth_client.post("/auth/apikeys", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "raw_key" in data
        assert len(data["raw_key"]) > 20  # Should be a substantial key
    
    def test_list_api_keys(self, auth_client, test_user):
        """Test listing API keys for a user."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a key first
        auth_client.post("/auth/apikeys", headers=headers)
        
        # List keys
        response = auth_client.get("/auth/apikeys", headers=headers)
        assert response.status_code == 200
        keys = response.json()
        
        assert isinstance(keys, list)
        assert len(keys) >= 1
        assert "id" in keys[0]
        assert "created_at" in keys[0]
        assert "revoked" in keys[0]
    
    def test_revoke_api_key(self, auth_client, test_user):
        """Test revoking an API key."""
        token = create_access_token(sub=test_user.username)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a key
        create_response = auth_client.post("/auth/apikeys", headers=headers)
        key_id = create_response.json()["id"]
        
        # Revoke it
        response = auth_client.delete(f"/auth/apikeys/{key_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify it's revoked
        list_response = auth_client.get("/auth/apikeys", headers=headers)
        keys = list_response.json()
        revoked_key = next(k for k in keys if k["id"] == key_id)
        assert revoked_key["revoked"] is True


class TestPasswordReset:
    """Test password reset functionality."""
    
    def test_request_password_reset(self, auth_client, test_user):
        """Test requesting a password reset."""
        response = auth_client.post(
            "/auth/password-reset/request",
            json={"email": test_user.email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_request_reset_for_nonexistent_email(self, auth_client):
        """Test that requesting reset for non-existent email doesn't reveal that."""
        response = auth_client.post(
            "/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        # Should return success to prevent email enumeration
        assert response.status_code == 200


class TestBackendAuthIntegration:
    """Test integration patterns between backend and auth.
    
    Note: The actual backend uses Supabase auth, but these tests demonstrate
    the integration pattern that could be used if backend consumed auth service tokens.
    """
    
    def test_jwt_token_structure(self):
        """Test that auth tokens have the expected structure for backend consumption."""
        from auth.security import create_access_token, decode_access_token
        import jwt as pyjwt
        
        username = "testuser"
        token = create_access_token(sub=username)
        
        # Decode without verification to inspect structure
        unverified = pyjwt.decode(token, options={"verify_signature": False})
        
        assert "sub" in unverified
        assert "exp" in unverified
        assert unverified["sub"] == username
    
    def test_token_can_be_shared_across_services(self):
        """Test that a token created by auth can be validated elsewhere."""
        from auth.security import create_access_token, decode_access_token, JWT_SECRET, JWT_ALGO
        import jwt as pyjwt
        
        # Auth service creates token
        token = create_access_token(sub="testuser")
        
        # Backend service validates it (using same secret)
        try:
            payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            username = payload.get("sub")
            assert username == "testuser"
        except Exception as e:
            pytest.fail(f"Token validation failed: {e}")


class TestDatabaseCompatibility:
    """Test database configuration for different environments."""
    
    def test_sqlite_connection(self):
        """Test that SQLite connection works for development."""
        from sqlalchemy import create_engine
        from auth.database import Base
        
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        assert "users" in tables
        assert "api_keys" in tables
        assert "password_reset_tokens" in tables
    
    def test_model_relationships(self, auth_db_session):
        """Test that model relationships work correctly."""
        from auth.models import User, APIKey
        
        # Create user
        user = User(
            name="Rel Test",
            email="rel@test.com",
            address="123 St",
            username="reltest",
            password_hash="hash",
        )
        auth_db_session.add(user)
        auth_db_session.commit()
        
        # Create API key
        api_key = APIKey(
            key_hash="test_hash",
            user_id=user.id
        )
        auth_db_session.add(api_key)
        auth_db_session.commit()
        
        # Test relationship
        auth_db_session.refresh(user)
        assert len(user.api_keys) == 1
        assert user.api_keys[0].key_hash == "test_hash"
        assert api_key.user.username == "reltest"


class TestSecurityUtilities:
    """Test security utility functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        from auth.security import hash_password, verify_password
        
        password = "mysecurepassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_api_key_hashing(self):
        """Test API key hashing."""
        from auth.security import hash_api_key
        
        raw_key = "test_api_key_12345"
        hashed = hash_api_key(raw_key)
        
        assert hashed != raw_key
        assert len(hashed) == 64  # SHA-256 produces 64 hex chars
        
        # Same input produces same hash
        hashed2 = hash_api_key(raw_key)
        assert hashed == hashed2
    
    def test_reset_expiry_creation(self):
        """Test that reset expiry is set correctly."""
        from auth.security import create_reset_expiry
        import datetime as dt
        
        expiry = create_reset_expiry()
        now = dt.datetime.now(dt.UTC)
        
        assert expiry > now
        # Should be roughly 30 minutes in the future
        delta = expiry - now
        assert delta.total_seconds() > 1500  # At least 25 minutes
        assert delta.total_seconds() < 2100  # At most 35 minutes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
