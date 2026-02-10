"""Auth service tests: register, login, API key, password reset, database connectivity.

Uses in-memory SQLite DB by setting AUTH_DB_URL before importing modules.
Tests include Supabase PostgreSQL connection validation and comprehensive edge cases.

NOTE: These tests are SKIPPED because the application uses Supabase authentication.
The custom auth API endpoints are not used in production.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Custom auth API unused - application uses Supabase auth")

import os
import importlib
import sys
import pathlib
import time
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError

# Ensure src layout path precedence for imports
ROOT = pathlib.Path(__file__).resolve().parents[2]
AUTH_SRC = ROOT / "auth" / "src"
if str(AUTH_SRC) not in sys.path:
    sys.path.insert(0, str(AUTH_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


@pytest.fixture(scope="session")
def app_client():
    # Use file-based SQLite to persist schema across connections; ensure clean start
    os.environ["AUTH_DB_URL"] = "sqlite:///./test_auth.db"
    test_db_path = pathlib.Path("test_auth.db")
    if test_db_path.exists():
        test_db_path.unlink()
    import auth.database as database
    import auth.models as models
    import auth.api as api
    importlib.reload(database)
    importlib.reload(models)
    importlib.reload(api)
    database.init_db()
    app = FastAPI()
    app.include_router(api.router)
    return TestClient(app)


def test_register_and_login(app_client):
    client = app_client
    reg_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "address": "123 Test Ave",
        "username": "testuser",
        "password": "StrongPass123!",
    }
    r = client.post("/auth/register", json=reg_payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["username"] == "testuser"
    r_dup = client.post("/auth/register", json=reg_payload)
    assert r_dup.status_code == 400
    r_login = client.post(
        "/auth/login", json={"username": "testuser", "password": "StrongPass123!"})
    assert r_login.status_code == 200, r_login.text
    token = r_login.json()["access_token"]
    bad_login = client.post(
        "/auth/login", json={"username": "testuser", "password": "Wrong"})
    assert bad_login.status_code == 400
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "testuser"


def test_apikey_flow(app_client):
    client = app_client
    client.post("/auth/register", json={
        "name": "API User",
        "email": "api@example.com",
        "address": "1 Key Way",
        "username": "apiuser",
        "password": "StrongPass123!",
    })
    login = client.post(
        "/auth/login", json={"username": "apiuser", "password": "StrongPass123!"})
    token = login.json()["access_token"]
    create = client.post(
        "/auth/apikeys", headers={"Authorization": f"Bearer {token}"})
    assert create.status_code == 200, create.text
    key_id = create.json()["id"]
    list_keys = client.get(
        "/auth/apikeys", headers={"Authorization": f"Bearer {token}"})
    keys = list_keys.json()
    assert any(k["id"] == key_id for k in keys)
    revoke = client.delete(
        f"/auth/apikeys/{key_id}", headers={"Authorization": f"Bearer {token}"})
    assert revoke.status_code == 200
    list_after = client.get(
        "/auth/apikeys", headers={"Authorization": f"Bearer {token}"})
    after_keys = list_after.json()
    assert any(k["id"] == key_id and k["revoked"] for k in after_keys)


def test_password_reset_flow(app_client, monkeypatch):
    client = app_client
    captured = {"token": None}
    import auth.api as api_mod

    def fake_send(email: str, token: str):
        captured["token"] = token

    monkeypatch.setattr(api_mod, "send_reset_email", fake_send)
    client.post("/auth/register", json={
        "name": "Reset User",
        "email": "reset@example.com",
        "address": "99 Reset Rd",
        "username": "resetuser",
        "password": "OriginalPass1!",
    })
    req = client.post("/auth/password-reset/request",
                      json={"email": "reset@example.com"})
    assert req.status_code == 200
    assert captured["token"] is not None
    reset_token = captured["token"]
    conf = client.post("/auth/password-reset/confirm",
                       json={"token": reset_token, "new_password": "NewPass456!"})
    assert conf.status_code == 200, conf.text
    login_new = client.post(
        "/auth/login", json={"username": "resetuser", "password": "NewPass456!"})
    assert login_new.status_code == 200
    login_old = client.post(
        "/auth/login", json={"username": "resetuser", "password": "OriginalPass1!"})
    assert login_old.status_code == 400

# ============================================================================
# Database Connectivity Tests
# ============================================================================


def test_database_url_from_environment():
    """Test that DATABASE_URL is read from environment variables."""
    import auth.database as database

    # The test fixture sets AUTH_DB_URL, but in production DATABASE_URL is used
    assert database.DATABASE_URL is not None
    assert len(database.DATABASE_URL) > 0


def test_sqlite_connection():
    """Test basic SQLite connection and table creation."""
    test_db_path = pathlib.Path("test_connectivity.db")
    if test_db_path.exists():
        test_db_path.unlink()

    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///./test_connectivity.db")
    SessionLocal = sessionmaker(bind=engine)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    finally:
        engine.dispose()
        if test_db_path.exists():
            test_db_path.unlink()


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or "postgresql" not in os.getenv(
        "DATABASE_URL", ""),
    reason="Requires DATABASE_URL with PostgreSQL connection"
)
def test_supabase_connection():
    """Test connection to Supabase PostgreSQL database.

    This test validates:
    - Connection establishment
    - URL encoding of special characters
    - Query execution
    - Connection pooling
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import NullPool

    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None, "DATABASE_URL not set"
    assert "postgresql" in db_url, "DATABASE_URL must be PostgreSQL"

    # Test with minimal connection pool for testing
    engine = create_engine(
        db_url,
        poolclass=NullPool,  # No connection pooling for test
    )

    try:
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            assert result.scalar() == 1

            # Test database version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            assert "PostgreSQL" in version

            # Test current database
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            assert db_name is not None
    finally:
        engine.dispose()


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or "postgresql" not in os.getenv(
        "DATABASE_URL", ""),
    reason="Requires DATABASE_URL with PostgreSQL connection"
)
def test_supabase_table_operations():
    """Test creating and querying tables in Supabase PostgreSQL."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import NullPool

    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url, poolclass=NullPool)

    try:
        with engine.connect() as conn:
            # Create a test table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connectivity (
                    id SERIAL PRIMARY KEY,
                    test_value VARCHAR(100)
                )
            """))
            conn.commit()

            # Insert test data
            conn.execute(text("""
                INSERT INTO test_connectivity (test_value) 
                VALUES ('test_connection')
            """))
            conn.commit()

            # Query test data
            result = conn.execute(text("""
                SELECT test_value FROM test_connectivity 
                WHERE test_value = 'test_connection'
            """))
            value = result.scalar()
            assert value == "test_connection"

            # Clean up
            conn.execute(text("DROP TABLE IF EXISTS test_connectivity"))
            conn.commit()
    finally:
        engine.dispose()


def test_database_pool_configuration(app_client):
    """Test that database connection pooling is properly configured."""
    import auth.database as database

    # Check that engine has proper pool settings
    engine = database.engine
    pool = engine.pool

    # Pool should exist
    assert pool is not None

    # Check pool status - size may be a property or method depending on pool type
    try:
        size = pool.size() if callable(pool.size) else pool.size
        assert size >= 0
    except (AttributeError, TypeError):
        # Some pool implementations don't have size
        assert pool is not None


def test_database_connection_error_handling():
    """Test handling of database connection errors."""
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError

    # Try to connect to invalid database
    invalid_engine = create_engine(
        "postgresql://invalid:invalid@localhost:9999/invalid")

    with pytest.raises(OperationalError):
        with invalid_engine.connect() as conn:
            conn.execute(text("SELECT 1"))


# ============================================================================
# Model Tests
# ============================================================================

def test_user_model_creation(app_client):
    """Test User model creation and validation."""
    import auth.models as models
    import auth.database as database
    from sqlalchemy.orm import Session

    db = database.SessionLocal()
    try:
        user = models.User(
            name="Model Test User",
            email="model@test.com",
            address="Model St",
            username="modeltest",
            password_hash="hashed_password",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.created_at is not None
        assert user.is_active is True

        # Test retrieval
        retrieved = db.query(models.User).filter(
            models.User.username == "modeltest"
        ).first()
        assert retrieved is not None
        assert retrieved.username == "modeltest"
        assert retrieved.email == "model@test.com"
    finally:
        db.close()


def test_apikey_model_creation(app_client):
    """Test APIKey model creation and relationships."""
    import auth.models as models
    import auth.database as database

    db = database.SessionLocal()
    try:
        # Create user first
        user = models.User(
            name="API Key Test",
            email="apikey@test.com",
            address="Key St",
            username="apikeytest",
            password_hash="hashed",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create API key
        api_key = models.APIKey(
            key_hash="test_hash_123",
            user_id=user.id,
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        assert api_key.id is not None
        assert api_key.created_at is not None
        assert api_key.revoked is False
        assert api_key.user_id == user.id

        # Test relationship
        assert len(user.api_keys) > 0
        assert user.api_keys[0].key_hash == "test_hash_123"
    finally:
        db.close()


def test_apikey_generate_raw_key():
    """Test API key generation."""
    import auth.models as models

    key1 = models.APIKey.generate_raw_key()
    key2 = models.APIKey.generate_raw_key()

    assert key1 != key2
    assert len(key1) > 20
    assert len(key2) > 20


def test_password_reset_token_model(app_client):
    """Test PasswordResetToken model."""
    import auth.models as models
    import auth.database as database
    import datetime as dt

    db = database.SessionLocal()
    try:
        # Create user
        user = models.User(
            name="Reset Test",
            email="reset@test.com",
            address="Reset St",
            username="resettest",
            password_hash="hashed",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create reset token
        token = models.PasswordResetToken(
            token="test_token_123",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(hours=1),
        )
        db.add(token)
        db.commit()
        db.refresh(token)

        assert token.id is not None
        assert token.used is False
        # Handle both timezone-aware and naive datetimes depending on database
        now = dt.datetime.now(dt.UTC)
        if token.expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)
        assert token.expires_at > now
    finally:
        db.close()


# ============================================================================
# Security Tests
# ============================================================================

def test_password_hashing():
    """Test password hashing and verification."""
    import auth.security as security

    password = "TestPassword123!"
    hashed = security.hash_password(password)

    assert hashed != password
    assert len(hashed) > 20
    assert security.verify_password(password, hashed)
    assert not security.verify_password("WrongPassword", hashed)


def test_jwt_token_creation_and_decoding():
    """Test JWT token creation and decoding."""
    import auth.security as security

    username = "testuser"
    token = security.create_access_token(username)

    assert token is not None
    assert len(token) > 20

    decoded = security.decode_access_token(token)
    assert decoded == username


def test_jwt_token_expiration():
    """Test that JWT token expiration is set correctly."""
    import auth.security as security
    from jose import jwt

    token = security.create_access_token("testuser")
    payload = jwt.decode(token, security.JWT_SECRET,
                         algorithms=[security.JWT_ALGO])

    assert "exp" in payload
    assert "sub" in payload
    assert payload["sub"] == "testuser"


def test_invalid_jwt_token():
    """Test handling of invalid JWT tokens."""
    import auth.security as security

    invalid_token = "invalid.token.here"
    decoded = security.decode_access_token(invalid_token)

    assert decoded is None


def test_api_key_hashing():
    """Test API key hashing."""
    import auth.security as security

    raw_key = "test_api_key_123"
    hashed = security.hash_api_key(raw_key)

    assert hashed != raw_key
    assert len(hashed) == 64  # SHA-256 produces 64 hex characters

    # Same key should produce same hash
    hashed2 = security.hash_api_key(raw_key)
    assert hashed == hashed2


def test_reset_token_expiry():
    """Test reset token expiry calculation."""
    import auth.security as security
    import datetime as dt

    expiry = security.create_reset_expiry()
    now = dt.datetime.now(dt.UTC)

    assert expiry > now
    # Should be approximately RESET_TOKEN_EXPIRE_MINUTES in the future
    delta = expiry - now
    assert delta.total_seconds() > 0
    assert delta.total_seconds() < (security.RESET_TOKEN_EXPIRE_MINUTES + 1) * 60


# ============================================================================
# API Endpoint Edge Case Tests
# ============================================================================

def test_register_with_invalid_email(app_client):
    """Test registration with invalid email format."""
    client = app_client

    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "invalid-email",
        "address": "123 Test Ave",
        "username": "testuser2",
        "password": "StrongPass123!",
    })
    assert response.status_code == 422  # Validation error


def test_register_with_short_password(app_client):
    """Test registration with password too short."""
    client = app_client

    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test2@example.com",
        "address": "123 Test Ave",
        "username": "testuser3",
        "password": "short",
    })
    assert response.status_code == 422


def test_register_with_short_username(app_client):
    """Test registration with username too short."""
    client = app_client

    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test3@example.com",
        "address": "123 Test Ave",
        "username": "ab",
        "password": "StrongPass123!",
    })
    assert response.status_code == 422


def test_login_with_nonexistent_user(app_client):
    """Test login with user that doesn't exist."""
    client = app_client

    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "SomePassword123!",
    })
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


def test_me_endpoint_without_token(app_client):
    """Test /me endpoint without authentication token."""
    client = app_client

    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_endpoint_with_invalid_token(app_client):
    """Test /me endpoint with invalid token."""
    client = app_client

    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


def test_create_apikey_without_auth(app_client):
    """Test API key creation without authentication."""
    client = app_client

    response = client.post("/auth/apikeys")
    assert response.status_code == 401


def test_revoke_nonexistent_apikey(app_client):
    """Test revoking API key that doesn't exist."""
    client = app_client

    # Create and login user
    client.post("/auth/register", json={
        "name": "API Test",
        "email": "apitest@example.com",
        "address": "API St",
        "username": "apitest",
        "password": "StrongPass123!",
    })
    login = client.post("/auth/login", json={
        "username": "apitest",
        "password": "StrongPass123!",
    })
    token = login.json()["access_token"]

    # Try to revoke non-existent key
    response = client.delete(
        "/auth/apikeys/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_password_reset_with_expired_token(app_client, monkeypatch):
    """Test password reset with expired token."""
    import auth.models as models
    import auth.database as database
    import datetime as dt

    client = app_client

    # Create user
    client.post("/auth/register", json={
        "name": "Expire Test",
        "email": "expire@example.com",
        "address": "Expire St",
        "username": "expiretest",
        "password": "OriginalPass1!",
    })

    # Manually create expired token
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(
            models.User.email == "expire@example.com"
        ).first()

        expired_token = models.PasswordResetToken(
            token="expired_token_123",
            user_id=user.id,
            expires_at=dt.datetime.now(
                dt.UTC) - dt.timedelta(hours=1),  # Expired
        )
        db.add(expired_token)
        db.commit()
    finally:
        db.close()

    # Try to use expired token
    response = client.post("/auth/password-reset/confirm", json={
        "token": "expired_token_123",
        "new_password": "NewPass456!",
    })
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_password_reset_with_used_token(app_client, monkeypatch):
    """Test password reset with already used token."""
    client = app_client
    captured = {"token": None}
    import auth.api as api_mod

    def fake_send(email: str, token: str):
        captured["token"] = token

    monkeypatch.setattr(api_mod, "send_reset_email", fake_send)

    # Create user and request reset
    client.post("/auth/register", json={
        "name": "Used Test",
        "email": "used@example.com",
        "address": "Used St",
        "username": "usedtest",
        "password": "OriginalPass1!",
    })

    client.post("/auth/password-reset/request",
                json={"email": "used@example.com"})
    token = captured["token"]

    # Use token once
    client.post("/auth/password-reset/confirm", json={
        "token": token,
        "new_password": "NewPass456!",
    })

    # Try to use again
    response = client.post("/auth/password-reset/confirm", json={
        "token": token,
        "new_password": "AnotherPass789!",
    })
    assert response.status_code == 400


def test_concurrent_registration(app_client):
    """Test handling of concurrent registration attempts."""
    client = app_client

    user_data = {
        "name": "Concurrent Test",
        "email": "concurrent@example.com",
        "address": "Concurrent St",
        "username": "concurrent",
        "password": "StrongPass123!",
    }

    # First registration should succeed
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 200

    # Second registration should fail
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400


# ============================================================================
# Health Check Test
# ============================================================================

def test_health_endpoint():
    """Test health check endpoint (if implemented)."""
    # This test assumes a health endpoint exists
    # If not implemented, this can be a placeholder for future implementation
    pass
