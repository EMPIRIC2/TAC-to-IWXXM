"""Comprehensive unit tests for auth.security module.

Tests password hashing, JWT tokens, API key hashing, and reset token utilities.
Target: 95%+ coverage.
"""
import pytest
import datetime as dt
import os
from unittest import mock

from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    hash_api_key,
    create_reset_expiry,
    JWT_SECRET,
    JWT_ALGO,
    JWT_EXPIRE_MINUTES,
    RESET_TOKEN_EXPIRE_MINUTES,
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 20
    
    def test_hash_password_not_plaintext(self):
        """Test that hashed password is not the same as plaintext."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
    
    def test_hash_password_unique_salt(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes due to random salt
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test verifying the correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test verifying an incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_verify_password_empty(self):
        """Test verifying an empty password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("testpassword123", hashed) is False
        assert verify_password("TestPassword123", hashed) is True


class TestJWTTokens:
    """Test JWT token creation and decoding."""
    
    def test_create_access_token(self):
        """Test creating a JWT access token."""
        username = "testuser"
        token = create_access_token(sub=username)
        
        assert isinstance(token, str)
        assert len(token) > 20
        assert "." in token  # JWT format has dots
    
    def test_decode_access_token_valid(self):
        """Test decoding a valid token."""
        username = "testuser"
        token = create_access_token(sub=username)
        
        decoded = decode_access_token(token)
        assert decoded == username
    
    def test_decode_access_token_invalid(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        assert decoded is None
    
    def test_decode_access_token_expired(self):
        """Test decoding an expired token."""
        from jose import jwt
        
        # Create expired token
        expire = dt.datetime.now(dt.UTC) - dt.timedelta(minutes=1)
        payload = {"sub": "testuser", "exp": expire}
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        
        decoded = decode_access_token(expired_token)
        assert decoded is None
    
    def test_decode_access_token_no_sub(self):
        """Test decoding a token without 'sub' claim."""
        from jose import jwt
        
        # Create token without sub
        expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=5)
        payload = {"exp": expire}
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_token_has_expiration(self):
        """Test that created tokens have expiration."""
        from jose import jwt
        
        token = create_access_token(sub="testuser")
        
        # Decode without verification to inspect
        unverified = jwt.decode(token, "", options={"verify_signature": False})
        
        assert "exp" in unverified
        assert "sub" in unverified
        assert unverified["sub"] == "testuser"
    
    def test_token_expiration_time(self):
        """Test that token expiration is set correctly."""
        from jose import jwt
        
        token = create_access_token(sub="testuser")
        
        unverified = jwt.decode(token, "", options={"verify_signature": False})
        exp_timestamp = unverified["exp"]
        exp_datetime = dt.datetime.fromtimestamp(exp_timestamp, tz=dt.UTC)
        
        # Token should expire in approximately JWT_EXPIRE_MINUTES minutes
        # Use a generous window to account for execution time
        now = dt.datetime.now(dt.UTC)
        expected_min = now + dt.timedelta(minutes=JWT_EXPIRE_MINUTES - 1)
        expected_max = now + dt.timedelta(minutes=JWT_EXPIRE_MINUTES + 1)
        
        assert expected_min <= exp_datetime <= expected_max
    
    def test_token_algorithm(self):
        """Test that the correct algorithm is used."""
        from jose import jwt
        
        token = create_access_token(sub="testuser")
        
        # Should decode with the expected algorithm
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        except Exception as e:
            pytest.fail(f"Token should decode with {JWT_ALGO}: {e}")
    
    def test_different_users_different_tokens(self):
        """Test that different users get different tokens."""
        token1 = create_access_token(sub="user1")
        token2 = create_access_token(sub="user2")
        
        assert token1 != token2
        
        decoded1 = decode_access_token(token1)
        decoded2 = decode_access_token(token2)
        
        assert decoded1 == "user1"
        assert decoded2 == "user2"


class TestAPIKeyHashing:
    """Test API key hashing."""
    
    def test_hash_api_key_returns_string(self):
        """Test that hash_api_key returns a string."""
        raw_key = "test_api_key_12345"
        hashed = hash_api_key(raw_key)
        
        assert isinstance(hashed, str)
    
    def test_hash_api_key_not_plaintext(self):
        """Test that hashed key is not the same as plaintext."""
        raw_key = "test_api_key_12345"
        hashed = hash_api_key(raw_key)
        
        assert hashed != raw_key
    
    def test_hash_api_key_deterministic(self):
        """Test that same key produces same hash (no salt)."""
        raw_key = "test_api_key_12345"
        hash1 = hash_api_key(raw_key)
        hash2 = hash_api_key(raw_key)
        
        assert hash1 == hash2
    
    def test_hash_api_key_sha256_length(self):
        """Test that hash is 64 characters (SHA-256 hex)."""
        raw_key = "test_api_key_12345"
        hashed = hash_api_key(raw_key)
        
        assert len(hashed) == 64
    
    def test_hash_api_key_different_keys(self):
        """Test that different keys produce different hashes."""
        hash1 = hash_api_key("key1")
        hash2 = hash_api_key("key2")
        
        assert hash1 != hash2
    
    def test_hash_api_key_hex_format(self):
        """Test that hash is in hexadecimal format."""
        raw_key = "test_api_key_12345"
        hashed = hash_api_key(raw_key)
        
        # Should only contain hex characters
        assert all(c in "0123456789abcdef" for c in hashed)


class TestResetTokenExpiry:
    """Test reset token expiry creation."""
    
    def test_create_reset_expiry_returns_datetime(self):
        """Test that create_reset_expiry returns a datetime."""
        expiry = create_reset_expiry()
        
        assert isinstance(expiry, dt.datetime)
    
    def test_reset_expiry_is_future(self):
        """Test that expiry is in the future."""
        now = dt.datetime.now(dt.UTC)
        expiry = create_reset_expiry()
        
        assert expiry > now
    
    def test_reset_expiry_correct_duration(self):
        """Test that expiry is set to the correct duration."""
        before = dt.datetime.now(dt.UTC)
        expiry = create_reset_expiry()
        after = dt.datetime.now(dt.UTC)
        
        expected_min = before + dt.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        expected_max = after + dt.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        
        assert expected_min <= expiry <= expected_max
    
    def test_reset_expiry_timezone_aware(self):
        """Test that expiry is timezone-aware (UTC)."""
        expiry = create_reset_expiry()
        
        assert expiry.tzinfo is not None
        assert expiry.tzinfo == dt.UTC


class TestSecurityConfiguration:
    """Test security configuration and environment variables."""
    
    def test_jwt_secret_from_env(self):
        """Test that JWT secret can be set from environment."""
        with mock.patch.dict(os.environ, {"AUTH_JWT_SECRET": "test-secret"}):
            # Re-import to get new env value
            import importlib
            import auth.security
            importlib.reload(auth.security)
            
            from auth.security import JWT_SECRET
            assert JWT_SECRET == "test-secret"
    
    def test_jwt_expire_from_env(self):
        """Test that JWT expiration can be set from environment."""
        with mock.patch.dict(os.environ, {"AUTH_JWT_EXPIRE_MINUTES": "120"}):
            import importlib
            import auth.security
            importlib.reload(auth.security)
            
            from auth.security import JWT_EXPIRE_MINUTES
            assert JWT_EXPIRE_MINUTES == 120
    
    def test_reset_expire_from_env(self):
        """Test that reset expiration can be set from environment."""
        with mock.patch.dict(os.environ, {"AUTH_RESET_EXPIRE_MINUTES": "60"}):
            import importlib
            import auth.security
            importlib.reload(auth.security)
            
            from auth.security import RESET_TOKEN_EXPIRE_MINUTES
            assert RESET_TOKEN_EXPIRE_MINUTES == 60
    
    def test_default_jwt_secret(self):
        """Test default JWT secret when not in env."""
        # JWT_SECRET should have a default value
        assert JWT_SECRET is not None
        assert len(JWT_SECRET) > 0
    
    def test_default_jwt_expire(self):
        """Test default JWT expiration."""
        assert JWT_EXPIRE_MINUTES > 0
        assert isinstance(JWT_EXPIRE_MINUTES, int)
    
    def test_default_reset_expire(self):
        """Test default reset token expiration."""
        assert RESET_TOKEN_EXPIRE_MINUTES > 0
        assert isinstance(RESET_TOKEN_EXPIRE_MINUTES, int)
    
    def test_jwt_algorithm(self):
        """Test JWT algorithm configuration."""
        assert JWT_ALGO == "HS256"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_hash_empty_password(self):
        """Test hashing an empty password."""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_empty_hash(self):
        """Test verifying against an empty hash."""
        from passlib.exc import UnknownHashError
        
        # Empty hash should raise an error
        with pytest.raises(UnknownHashError):
            verify_password("password", "")
    
    def test_hash_unicode_password(self):
        """Test hashing a password with unicode characters."""
        password = "пароль123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("password123", hashed) is False
    
    def test_hash_long_password(self):
        """Test hashing a very long password."""
        password = "a" * 1000
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_decode_malformed_token(self):
        """Test decoding a malformed token."""
        malformed_tokens = [
            "",
            "no-dots",
            "one.dot",
            "...",
            "a.b.c.d.e",
        ]
        
        for token in malformed_tokens:
            result = decode_access_token(token)
            assert result is None, f"Token '{token}' should return None"
    
    def test_hash_empty_api_key(self):
        """Test hashing an empty API key."""
        hashed = hash_api_key("")
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # Still 64 hex chars
    
    def test_hash_unicode_api_key(self):
        """Test hashing an API key with unicode characters."""
        key = "ключ-api-123"
        hashed = hash_api_key(key)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
