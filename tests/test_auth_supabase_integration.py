"""Integration tests between auth service and Supabase.

Tests the integration between the custom auth service and Supabase as an external
authorization provider, ensuring tokens can be validated across services.
"""
import os
from unittest import mock

import pytest
from jose import jwt

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


class TestSupabaseAuthIntegration:
    """Test integration with Supabase as external auth provider."""
    
    def test_jwt_token_format_compatible_with_supabase(self):
        """Test that auth service tokens use Supabase-compatible format."""
        from auth.security import JWT_ALGO, JWT_SECRET, create_access_token
        
        token = create_access_token(sub="testuser@example.com")
        
        # Decode to verify structure
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        
        # Should have standard JWT claims
        assert "sub" in payload
        assert "exp" in payload
        
        # Sub should be email or user identifier
        assert "@" in payload["sub"] or len(payload["sub"]) > 0
    
    def test_token_expiration_matches_supabase_patterns(self):
        """Test that token expiration follows standard patterns."""
        import time

        from auth.security import JWT_EXPIRE_MINUTES, create_access_token
        
        before = time.time()
        token = create_access_token(sub="user@example.com")
        after = time.time()
        
        # Decode without verification
        from jose import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Expiration should be in the future
        assert payload["exp"] > before
        
        # Should be approximately JWT_EXPIRE_MINUTES in the future
        expected_exp = after + (JWT_EXPIRE_MINUTES * 60)
        assert abs(payload["exp"] - expected_exp) < 10  # Within 10 seconds
    
    def test_token_can_be_decoded_by_external_service(self):
        """Test that tokens can be decoded by external services."""
        from auth.security import JWT_ALGO, JWT_SECRET, create_access_token
        
        token = create_access_token(sub="user@example.com")
        
        # Simulate external service decoding
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
            assert payload["sub"] == "user@example.com"
        except Exception as e:
            pytest.fail(f"External service should be able to decode token: {e}")
    
    @pytest.mark.asyncio
    async def test_supabase_jwks_endpoint_structure(self):
        """Test understanding of Supabase JWKS endpoint structure."""
        # This is a mock test showing how Supabase JWKS would work
        mock_jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "kid": "test-key-id",
                    "use": "sig",
                    "alg": "RS256",
                    "n": "test-n-value",
                    "e": "AQAB"
                }
            ]
        }
        
        # Verify structure
        assert "keys" in mock_jwks
        assert len(mock_jwks["keys"]) > 0
        assert all("kid" in key for key in mock_jwks["keys"])


class TestAuthServiceAsSupabaseReplacement:
    """Test auth service as a drop-in replacement for Supabase auth."""
    
    def test_user_registration_flow(self):
        """Test user registration similar to Supabase flow."""
        from fastapi.testclient import TestClient
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from auth.__main__ import app
        from auth.database import Base
        
        # Setup
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        from auth.api import get_db
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        
        # Register user (Supabase-like flow)
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "address": "123 Test St",
            "username": "testuser",
            "password": "SecurePass123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "password" not in data
        
        app.dependency_overrides.clear()
    
    def test_login_returns_access_token(self):
        """Test login flow returns access token like Supabase."""
        from fastapi.testclient import TestClient
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from auth.__main__ import app
        from auth.database import Base
        from auth.models import User
        from auth.security import hash_password
        
        # Setup
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        
        # Create test user
        session = TestingSessionLocal()
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash=hash_password("password123"),
        )
        session.add(user)
        session.commit()
        session.close()
        
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        from auth.api import get_db
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        
        # Login (Supabase-like flow)
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Supabase-compatible response
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        app.dependency_overrides.clear()


class TestSupabaseTokenValidation:
    """Test token validation patterns used by Supabase."""
    
    def test_bearer_token_format(self):
        """Test that tokens work with Bearer authentication."""
        from auth.security import create_access_token
        
        token = create_access_token(sub="user@example.com")
        
        # Should work with Bearer prefix
        auth_header = f"Bearer {token}"
        assert auth_header.startswith("Bearer ")
        
        # Extract token
        extracted = auth_header.split(" ")[1]
        assert extracted == token
    
    def test_token_validation_with_bearer_header(self):
        """Test token validation with Bearer header."""
        from fastapi.testclient import TestClient
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from auth.__main__ import app
        from auth.database import Base
        from auth.models import User
        from auth.security import create_access_token, hash_password
        
        # Setup
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        
        # Create user
        session = TestingSessionLocal()
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash=hash_password("password"),
        )
        session.add(user)
        session.commit()
        session.close()
        
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        from auth.api import get_db
        app.dependency_overrides[get_db] = override_get_db
        
        client = TestClient(app)
        
        # Get token
        token = create_access_token(sub="testuser")
        
        # Use Bearer header (Supabase pattern)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        
        app.dependency_overrides.clear()


class TestAuthServiceSupabaseCompatibility:
    """Test compatibility with Supabase patterns and conventions."""
    
    def test_email_based_authentication(self):
        """Test that service supports email-based auth like Supabase."""
        from auth.models import User
        from auth.security import hash_password
        
        # Users should have email field
        user = User(
            name="Test",
            email="user@example.com",
            address="123 St",
            username="user",
            password_hash=hash_password("pass"),
        )
        
        assert hasattr(user, "email")
        assert "@" in user.email
    
    def test_password_reset_token_generation(self):
        """Test password reset token generation like Supabase."""
        from auth.models import PasswordResetToken
        
        token = PasswordResetToken.generate_token()
        
        # Should be URL-safe
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Should not contain characters that need URL encoding
        import string
        allowed = string.ascii_letters + string.digits + "-_"
        assert all(c in allowed for c in token)
    
    def test_user_metadata_structure(self):
        """Test that user model has Supabase-like metadata."""
        from sqlalchemy import inspect

        from auth.models import User
        
        # Get columns
        mapper = inspect(User)
        columns = [c.key for c in mapper.column_attrs]
        
        # Should have standard Supabase fields
        assert "id" in columns
        assert "email" in columns
        assert "created_at" in columns
    
    def test_api_key_management_like_supabase(self):
        """Test API key management similar to Supabase service keys."""
        from auth.models import APIKey
        
        raw_key = APIKey.generate_raw_key()
        
        # Should be secure
        assert len(raw_key) > 20
        
        # Should be different each time
        raw_key2 = APIKey.generate_raw_key()
        assert raw_key != raw_key2


class TestCrossServiceAuthentication:
    """Test authentication across auth service and backend service."""
    
    def test_token_generated_by_auth_service(self):
        """Test that auth service generates valid tokens."""
        from auth.security import create_access_token, decode_access_token
        
        user_email = "user@example.com"
        token = create_access_token(sub=user_email)
        
        # Should be decodable
        decoded = decode_access_token(token)
        assert decoded == user_email
    
    def test_token_sharing_pattern(self):
        """Test pattern for sharing tokens between services."""
        import jwt as pyjwt

        from auth.security import JWT_ALGO, JWT_SECRET, create_access_token
        
        # Auth service creates token
        token = create_access_token(sub="user@example.com")
        
        # Backend service validates it (if using same secret)
        # This simulates cross-service validation
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        
        assert payload["sub"] == "user@example.com"
        assert "exp" in payload
    
    def test_health_check_for_service_discovery(self):
        """Test health check endpoint for service discovery."""
        from fastapi.testclient import TestClient

        from auth.__main__ import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should provide service info
        assert data["status"] == "healthy"
        assert data["service"] == "auth"
        assert "version" in data


class TestDatabaseConnectionPatterns:
    """Test database connection patterns for Supabase compatibility."""
    
    def test_postgresql_url_support(self):
        """Test that service supports PostgreSQL URLs like Supabase."""
        with mock.patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db"
        }):
            import importlib

            import auth.database
            importlib.reload(auth.database)
            
            from auth.database import DATABASE_URL
            assert "postgresql" in DATABASE_URL
    
    def test_connection_pooling_config(self):
        """Test connection pooling for production use."""
        with mock.patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db"
        }):
            import importlib

            import auth.database
            importlib.reload(auth.database)
            
            from auth.database import engine
            
            # Engine should be configured
            assert engine is not None


class TestSecurityBestPractices:
    """Test security best practices aligned with Supabase."""
    
    def test_password_hashing_strength(self):
        """Test that passwords are hashed securely."""
        from auth.security import hash_password
        
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Should be hashed (not plaintext)
        assert hashed != password
        
        # Should be substantial length
        assert len(hashed) > 50
    
    def test_api_keys_are_hashed(self):
        """Test that API keys are stored hashed."""
        from auth.security import hash_api_key
        
        raw_key = "test_api_key_12345"
        hashed = hash_api_key(raw_key)
        
        # Should be hashed
        assert hashed != raw_key
        
        # SHA-256 hex is 64 chars
        assert len(hashed) == 64
    
    def test_tokens_expire(self):
        """Test that tokens have expiration."""
        from jose import jwt

        from auth.security import create_access_token
        
        token = create_access_token(sub="user@example.com")
        
        # Decode without verification
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Should have exp claim
        assert "exp" in payload
        
        # Should be in the future
        import time
        assert payload["exp"] > time.time()


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""
    
    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        from auth.security import decode_access_token
        
        invalid_token = "invalid.token.here"
        result = decode_access_token(invalid_token)
        
        assert result is None
    
    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected."""
        import time

        import jwt as pyjwt

        from auth.security import JWT_ALGO, JWT_SECRET, decode_access_token
        
        # Create expired token
        payload = {
            "sub": "user@example.com",
            "exp": time.time() - 3600  # 1 hour ago
        }
        expired_token = pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        
        result = decode_access_token(expired_token)
        assert result is None
    
    def test_missing_authorization_header(self):
        """Test handling of missing authorization header."""
        from fastapi.testclient import TestClient

        from auth.__main__ import app
        
        client = TestClient(app)
        response = client.get("/auth/me")
        
        # Should return 401
        assert response.status_code == 401
    
    def test_malformed_authorization_header(self):
        """Test handling of malformed authorization header."""
        from fastapi.testclient import TestClient

        from auth.__main__ import app
        
        client = TestClient(app)
        
        # Missing Bearer prefix
        response = client.get("/auth/me", headers={"Authorization": "just-a-token"})
        assert response.status_code == 401
        
        # Empty header
        response = client.get("/auth/me", headers={"Authorization": ""})
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
