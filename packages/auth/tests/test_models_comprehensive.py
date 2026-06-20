"""Comprehensive unit tests for auth.models module.

Tests all database models: User, APIKey, PasswordResetToken.
Target: 95%+ coverage.
"""

import pytest
import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth.database import Base
from auth.models import User, APIKey, PasswordResetToken


@pytest.fixture
def db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create a database session for tests."""
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    yield session
    session.close()


class TestUserModel:
    """Test the User model."""

    def test_create_user(self, db_session):
        """Test creating a user with all fields."""
        user = User(
            name="John Doe",
            email="john@example.com",
            address="123 Main St",
            username="johndoe",
            password_hash="hashed_password_here",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.address == "123 Main St"
        assert user.username == "johndoe"
        assert user.password_hash == "hashed_password_here"
        assert user.is_active is True
        assert isinstance(user.created_at, dt.datetime)

    def test_user_defaults(self, db_session):
        """Test user default values."""
        user = User(
            name="Test",
            email="test@test.com",
            address="456 St",
            username="test",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.is_active is True
        assert user.created_at is not None

    def test_user_unique_email(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            name="User 1",
            email="same@example.com",
            address="123 St",
            username="user1",
            password_hash="hash1",
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            name="User 2",
            email="same@example.com",
            address="456 St",
            username="user2",
            password_hash="hash2",
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_user_unique_username(self, db_session):
        """Test that username must be unique."""
        user1 = User(
            name="User 1",
            email="email1@example.com",
            address="123 St",
            username="sameuser",
            password_hash="hash1",
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            name="User 2",
            email="email2@example.com",
            address="456 St",
            username="sameuser",
            password_hash="hash2",
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_user_api_keys_relationship(self, db_session):
        """Test that user has api_keys relationship."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Initially empty
        assert user.api_keys == []

        # Add API key
        api_key = APIKey(key_hash="test_hash", user_id=user.id)
        db_session.add(api_key)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.api_keys) == 1
        assert user.api_keys[0].key_hash == "test_hash"

    def test_user_reset_tokens_relationship(self, db_session):
        """Test that user has reset_tokens relationship."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Initially empty
        assert user.reset_tokens == []

        # Add reset token
        reset_token = PasswordResetToken(
            token="test_token",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
        )
        db_session.add(reset_token)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.reset_tokens) == 1
        assert user.reset_tokens[0].token == "test_token"

    def test_user_cascade_delete_api_keys(self, db_session):
        """Test that deleting a user deletes their API keys."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        api_key = APIKey(key_hash="test_hash", user_id=user.id)
        db_session.add(api_key)
        db_session.commit()

        user_id = user.id
        db_session.delete(user)
        db_session.commit()

        # API key should be deleted
        remaining_keys = db_session.query(APIKey).filter(APIKey.user_id == user_id).all()
        assert len(remaining_keys) == 0

    def test_user_cascade_delete_reset_tokens(self, db_session):
        """Test that deleting a user deletes their reset tokens."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        reset_token = PasswordResetToken(
            token="test_token",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
        )
        db_session.add(reset_token)
        db_session.commit()

        user_id = user.id
        db_session.delete(user)
        db_session.commit()

        # Reset token should be deleted
        remaining_tokens = db_session.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id).all()
        assert len(remaining_tokens) == 0


class TestAPIKeyModel:
    """Test the APIKey model."""

    def test_create_api_key(self, db_session):
        """Test creating an API key."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        api_key = APIKey(
            key_hash="hashed_key_value",
            user_id=user.id,
        )
        db_session.add(api_key)
        db_session.commit()
        db_session.refresh(api_key)

        assert api_key.id is not None
        assert api_key.key_hash == "hashed_key_value"
        assert api_key.user_id == user.id
        assert isinstance(api_key.created_at, dt.datetime)
        assert api_key.revoked is False

    def test_api_key_defaults(self, db_session):
        """Test API key default values."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        api_key = APIKey(key_hash="hash", user_id=user.id)
        db_session.add(api_key)
        db_session.commit()
        db_session.refresh(api_key)

        assert api_key.revoked is False
        assert api_key.created_at is not None

    def test_api_key_unique_hash(self, db_session):
        """Test that key_hash must be unique."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        key1 = APIKey(key_hash="same_hash", user_id=user.id)
        db_session.add(key1)
        db_session.commit()

        key2 = APIKey(key_hash="same_hash", user_id=user.id)
        db_session.add(key2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_api_key_user_relationship(self, db_session):
        """Test the back-reference to user."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        api_key = APIKey(key_hash="hash", user_id=user.id)
        db_session.add(api_key)
        db_session.commit()
        db_session.refresh(api_key)

        assert api_key.user is not None
        assert api_key.user.username == "testuser"

    def test_generate_raw_key(self):
        """Test the static method for generating raw API keys."""
        key1 = APIKey.generate_raw_key()
        key2 = APIKey.generate_raw_key()

        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert len(key1) > 20  # Should be substantial
        assert len(key2) > 20
        assert key1 != key2  # Should be unique

    def test_revoke_api_key(self, db_session):
        """Test revoking an API key."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        api_key = APIKey(key_hash="hash", user_id=user.id)
        db_session.add(api_key)
        db_session.commit()

        api_key.revoked = True
        db_session.commit()
        db_session.refresh(api_key)

        assert api_key.revoked is True


class TestPasswordResetTokenModel:
    """Test the PasswordResetToken model."""

    def test_create_reset_token(self, db_session):
        """Test creating a password reset token."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)
        token = PasswordResetToken(
            token="reset_token_value",
            user_id=user.id,
            expires_at=expires,
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)

        assert token.id is not None
        assert token.token == "reset_token_value"
        assert token.user_id == user.id
        assert isinstance(token.expires_at, dt.datetime)
        assert token.used is False
        assert isinstance(token.created_at, dt.datetime)

    def test_reset_token_defaults(self, db_session):
        """Test reset token default values."""
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
            token="token",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)

        assert token.used is False
        assert token.created_at is not None

    def test_reset_token_unique(self, db_session):
        """Test that token must be unique."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)

        token1 = PasswordResetToken(
            token="same_token",
            user_id=user.id,
            expires_at=expires,
        )
        db_session.add(token1)
        db_session.commit()

        token2 = PasswordResetToken(
            token="same_token",
            user_id=user.id,
            expires_at=expires,
        )
        db_session.add(token2)

        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_reset_token_user_relationship(self, db_session):
        """Test the back-reference to user."""
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
            token="token",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)

        assert token.user is not None
        assert token.user.username == "testuser"

    def test_generate_token(self):
        """Test the static method for generating tokens."""
        token1 = PasswordResetToken.generate_token()
        token2 = PasswordResetToken.generate_token()

        assert isinstance(token1, str)
        assert isinstance(token2, str)
        assert len(token1) > 30  # Should be substantial
        assert len(token2) > 30
        assert token1 != token2  # Should be unique

    def test_mark_token_as_used(self, db_session):
        """Test marking a token as used."""
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
            token="token",
            user_id=user.id,
            expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
        )
        db_session.add(token)
        db_session.commit()

        token.used = True
        db_session.commit()
        db_session.refresh(token)

        assert token.used is True

    def test_token_expiration_check(self, db_session):
        """Test checking if a token is expired."""
        user = User(
            name="Test",
            email="test@example.com",
            address="123 St",
            username="testuser",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        # Expired token
        expired_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
        expired = PasswordResetToken(
            token="expired",
            user_id=user.id,
            expires_at=expired_time,
        )
        db_session.add(expired)

        # Valid token
        valid_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)
        valid = PasswordResetToken(
            token="valid",
            user_id=user.id,
            expires_at=valid_time,
        )
        db_session.add(valid)
        db_session.commit()

        # Refresh from database
        db_session.refresh(expired)
        db_session.refresh(valid)

        now = dt.datetime.now(dt.timezone.utc)

        # Handle both naive and aware datetimes from SQLite
        expired_dt = expired.expires_at
        valid_dt = valid.expires_at

        if expired_dt.tzinfo is None:
            expired_dt = expired_dt.replace(tzinfo=dt.timezone.utc)
        if valid_dt.tzinfo is None:
            valid_dt = valid_dt.replace(tzinfo=dt.timezone.utc)

        assert expired_dt < now
        assert valid_dt > now


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
