"""Supabase PostgreSQL Integration Tests.

These tests validate the connection and operations with Supabase PostgreSQL using
the official connection format from Supabase documentation:
- Dialect: postgresql+psycopg2://
- SSL Mode: sslmode=require
- Format: postgresql+psycopg2://user:password@host:port/dbname?sslmode=require

IMPORTANT: Supabase's db.*.supabase.co hostnames only have IPv6 (AAAA) DNS records.
Docker containers need IPv6 enabled to resolve these hostnames. If you encounter
"could not translate host name" errors, enable IPv6 in Docker or use SQLite for
local development.

Run these tests with:
    pytest auth/tests/test_supabase_integration.py -v

To skip Supabase tests when DATABASE_URL points to SQLite:
    DATABASE_URL=sqlite:///./auth.db pytest auth/tests/test_supabase_integration.py -v
"""

from __future__ import annotations

import os
import sys
import pathlib

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

# Ensure src layout path precedence
ROOT = pathlib.Path(__file__).resolve().parents[2]
AUTH_SRC = ROOT / "auth" / "src"
if str(AUTH_SRC) not in sys.path:
    sys.path.insert(0, str(AUTH_SRC))


# Mark all tests in this file as explicit opt-in integration tests.
# This prevents accidental execution in standard CI/unit runs where DATABASE_URL
# may be populated indirectly (for example via local .env loading).
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_SUPABASE_INTEGRATION_TESTS", "").lower() not in {"1", "true", "yes"}
    or not os.getenv("DATABASE_URL")
    or "postgresql" not in os.getenv("DATABASE_URL", ""),
    reason=("Requires RUN_SUPABASE_INTEGRATION_TESTS=true and DATABASE_URL with PostgreSQL connection"),
)


class TestSupabaseConnection:
    """Test suite for Supabase database connection following official documentation."""

    def test_connection_string_format(self):
        """Verify DATABASE_URL uses official Supabase connection format."""
        db_url = os.getenv("DATABASE_URL")

        assert db_url is not None
        # Per Supabase docs, should use postgresql+psycopg2:// dialect
        assert db_url.startswith("postgresql+psycopg2://"), "Supabase requires postgresql+psycopg2:// dialect"

    def test_ssl_requirement(self):
        """Verify that SSL mode is properly configured."""
        db_url = os.getenv("DATABASE_URL", "")

        # Supabase requires SSL connections
        assert "sslmode=require" in db_url, "Supabase connections must use sslmode=require"

        # Check for URL-encoded special characters (if password contains them)
        # Common special chars: !, @, #, $, %, ^, &, *, (, )
        # URL-encoded: %21, %40, %23, %24, %25, %5E, %26, %2A, %28, %29
        if any(char in db_url for char in ["%21", "%40", "%23", "%5E", "%26"]):
            print("✓ Password appears to be URL-encoded")

    def test_basic_connection(self):
        """Test establishing connection to Supabase."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            engine.dispose()

    def test_database_version(self):
        """Test retrieving PostgreSQL version from Supabase."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()

                assert version is not None
                assert "PostgreSQL" in version
                print(f"Database version: {version}")
        finally:
            engine.dispose()

    def test_current_database_info(self):
        """Test retrieving current database information."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Get database name
                result = conn.execute(text("SELECT current_database()"))
                db_name = result.scalar()
                assert db_name is not None
                print(f"Connected to database: {db_name}")

                # Get current user
                result = conn.execute(text("SELECT current_user"))
                user = result.scalar()
                assert user is not None
                print(f"Connected as user: {user}")
        finally:
            engine.dispose()

    def test_connection_with_pool_pre_ping(self):
        """Test connection with pool_pre_ping enabled."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)

        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            engine.dispose()

    def test_multiple_connections(self):
        """Test opening multiple connections."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, pool_size=5)

        try:
            connections = []
            for i in range(3):
                conn = engine.connect()
                connections.append(conn)
                result = conn.execute(text(f"SELECT {i}"))
                assert result.scalar() == i

            # Close all connections
            for conn in connections:
                conn.close()
        finally:
            engine.dispose()


class TestSupabaseTableOperations:
    """Test suite for table operations on Supabase."""

    def test_create_and_drop_table(self):
        """Test creating and dropping a test table."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Create table
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS test_supabase_ops (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                )
                conn.commit()

                # Verify table exists
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                assert "test_supabase_ops" in tables

                # Drop table
                conn.execute(text("DROP TABLE IF EXISTS test_supabase_ops"))
                conn.commit()
        finally:
            engine.dispose()

    def test_insert_and_query(self):
        """Test inserting and querying data."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Create table
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS test_insert_query (
                        id SERIAL PRIMARY KEY,
                        value TEXT
                    )
                """)
                )
                conn.commit()

                # Insert data
                conn.execute(
                    text("""
                    INSERT INTO test_insert_query (value)
                    VALUES ('test_value_1'), ('test_value_2')
                """)
                )
                conn.commit()

                # Query data
                result = conn.execute(
                    text("""
                    SELECT COUNT(*) FROM test_insert_query
                """)
                )
                count = result.scalar()
                assert count >= 2

                # Query specific value
                result = conn.execute(
                    text("""
                    SELECT value FROM test_insert_query
                    WHERE value = 'test_value_1'
                """)
                )
                value = result.scalar()
                assert value == "test_value_1"

                # Clean up
                conn.execute(text("DROP TABLE IF EXISTS test_insert_query"))
                conn.commit()
        finally:
            engine.dispose()

    def test_transaction_rollback(self):
        """Test transaction rollback."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Create table
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS test_transaction (
                        id SERIAL PRIMARY KEY,
                        value TEXT
                    )
                """)
                )
                conn.commit()

                # Start transaction
                trans = conn.begin()
                try:
                    conn.execute(
                        text("""
                        INSERT INTO test_transaction (value) VALUES ('will_rollback')
                    """)
                    )
                    trans.rollback()
                except Exception:
                    trans.rollback()
                    raise

                # Verify data was not inserted
                result = conn.execute(
                    text("""
                    SELECT COUNT(*) FROM test_transaction
                    WHERE value = 'will_rollback'
                """)
                )
                count = result.scalar()
                assert count == 0

                # Clean up
                conn.execute(text("DROP TABLE IF EXISTS test_transaction"))
                conn.commit()
        finally:
            engine.dispose()

    def test_update_and_delete(self):
        """Test updating and deleting records."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Create and populate table
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS test_update_delete (
                        id SERIAL PRIMARY KEY,
                        value TEXT
                    )
                """)
                )
                conn.commit()

                conn.execute(
                    text("""
                    INSERT INTO test_update_delete (value)
                    VALUES ('original')
                """)
                )
                conn.commit()

                # Update
                conn.execute(
                    text("""
                    UPDATE test_update_delete
                    SET value = 'updated'
                    WHERE value = 'original'
                """)
                )
                conn.commit()

                result = conn.execute(
                    text("""
                    SELECT value FROM test_update_delete
                """)
                )
                value = result.scalar()
                assert value == "updated"

                # Delete
                conn.execute(
                    text("""
                    DELETE FROM test_update_delete WHERE value = 'updated'
                """)
                )
                conn.commit()

                result = conn.execute(
                    text("""
                    SELECT COUNT(*) FROM test_update_delete
                """)
                )
                count = result.scalar()
                assert count == 0

                # Clean up
                conn.execute(text("DROP TABLE IF EXISTS test_update_delete"))
                conn.commit()
        finally:
            engine.dispose()


class TestSupabaseAuthModels:
    """Test auth models with Supabase database."""

    def test_user_table_creation(self):
        """Test creating users table in Supabase."""
        import auth.database as database
        import auth.models as models

        # Initialize database (creates tables)
        database.init_db()

        # Verify tables exist
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()

        assert "users" in tables
        assert "api_keys" in tables
        assert "password_reset_tokens" in tables

    def test_user_crud_operations(self):
        """Test CRUD operations on User model."""
        import auth.database as database
        import auth.models as models
        import auth.security as security

        database.init_db()
        db = database.SessionLocal()

        try:
            # Create
            user = models.User(
                name="Supabase Test User",
                email="supabase@test.com",
                address="Supabase St",
                username="supabasetest",
                password_hash=security.hash_password("TestPass123!"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            assert user.id is not None
            user_id = user.id

            # Read
            retrieved = db.query(models.User).filter(models.User.id == user_id).first()
            assert retrieved is not None
            assert retrieved.username == "supabasetest"

            # Update
            retrieved.address = "New Supabase Address"
            db.commit()

            updated = db.query(models.User).filter(models.User.id == user_id).first()
            assert updated.address == "New Supabase Address"

            # Delete
            db.delete(updated)
            db.commit()

            deleted = db.query(models.User).filter(models.User.id == user_id).first()
            assert deleted is None

        finally:
            db.close()

    def test_api_key_relationship(self):
        """Test User-APIKey relationship in Supabase."""
        import auth.database as database
        import auth.models as models
        import auth.security as security

        database.init_db()
        db = database.SessionLocal()

        try:
            # Create user
            user = models.User(
                name="API Key Test",
                email="apikey_supabase@test.com",
                address="API St",
                username="apikeysupabase",
                password_hash=security.hash_password("TestPass123!"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create API key
            raw_key = models.APIKey.generate_raw_key()
            api_key = models.APIKey(
                key_hash=security.hash_api_key(raw_key),
                user_id=user.id,
            )
            db.add(api_key)
            db.commit()
            db.refresh(api_key)

            # Test relationship
            assert len(user.api_keys) > 0
            assert user.api_keys[0].id == api_key.id

            # Clean up
            db.delete(user)  # Cascade should delete api_key
            db.commit()

        finally:
            db.close()

    def test_password_reset_token_relationship(self):
        """Test User-PasswordResetToken relationship."""
        import auth.database as database
        import auth.models as models
        import auth.security as security
        import datetime as dt

        database.init_db()
        db = database.SessionLocal()

        try:
            # Create user
            user = models.User(
                name="Reset Test",
                email="reset_supabase@test.com",
                address="Reset St",
                username="resetsupabase",
                password_hash=security.hash_password("TestPass123!"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create reset token
            token = models.PasswordResetToken(
                token=models.PasswordResetToken.generate_token(),
                user_id=user.id,
                expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(hours=1),
            )
            db.add(token)
            db.commit()
            db.refresh(token)

            # Test relationship
            assert len(user.reset_tokens) > 0
            assert user.reset_tokens[0].id == token.id

            # Clean up
            db.delete(user)  # Cascade should delete token
            db.commit()

        finally:
            db.close()


class TestSupabaseErrorHandling:
    """Test error handling with Supabase."""

    def test_connection_timeout(self):
        """Test handling connection timeout."""
        # Create engine with very short timeout
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, connect_args={"connect_timeout": 1})

        try:
            with engine.connect() as conn:
                # This should work if Supabase is responsive
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            engine.dispose()

    def test_invalid_query_error(self):
        """Test handling of invalid SQL query."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                with pytest.raises(Exception):  # Should raise database error
                    conn.execute(text("SELECT * FROM nonexistent_table_xyz"))
        finally:
            engine.dispose()

    def test_duplicate_key_error(self):
        """Test handling of duplicate key constraint violation."""
        import auth.database as database
        import auth.models as models
        import auth.security as security
        from sqlalchemy.exc import IntegrityError

        database.init_db()
        db = database.SessionLocal()

        try:
            # Create first user
            user1 = models.User(
                name="Duplicate Test",
                email="duplicate@test.com",
                address="Dup St",
                username="duplicate",
                password_hash=security.hash_password("TestPass123!"),
            )
            db.add(user1)
            db.commit()

            # Try to create duplicate
            user2 = models.User(
                name="Duplicate Test 2",
                email="duplicate@test.com",  # Same email
                address="Dup St 2",
                username="duplicate2",
                password_hash=security.hash_password("TestPass123!"),
            )
            db.add(user2)

            with pytest.raises(IntegrityError):
                db.commit()

            db.rollback()

            # Clean up
            db.query(models.User).filter(models.User.username == "duplicate").delete()
            db.commit()

        finally:
            db.close()


class TestSupabasePerformance:
    """Test performance characteristics with Supabase."""

    def test_batch_insert_performance(self):
        """Test inserting multiple records efficiently."""
        import time

        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Create table
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS test_batch_insert (
                        id SERIAL PRIMARY KEY,
                        value TEXT
                    )
                """)
                )
                conn.commit()

                # Insert 100 records
                start_time = time.time()

                values = ", ".join([f"('value_{i}')" for i in range(100)])
                conn.execute(
                    text(f"""
                    INSERT INTO test_batch_insert (value) VALUES {values}
                """)
                )
                conn.commit()

                elapsed = time.time() - start_time
                print(f"Batch insert of 100 records took {elapsed:.3f} seconds")

                # Verify count
                result = conn.execute(
                    text("""
                    SELECT COUNT(*) FROM test_batch_insert
                """)
                )
                count = result.scalar()
                assert count >= 100

                # Clean up
                conn.execute(text("DROP TABLE IF EXISTS test_batch_insert"))
                conn.commit()
        finally:
            engine.dispose()

    def test_query_with_index(self):
        """Test query performance with and without index."""
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url, poolclass=NullPool)

        try:
            with engine.connect() as conn:
                # Create table
                conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS test_index (
                        id SERIAL PRIMARY KEY,
                        value TEXT
                    )
                """)
                )
                conn.commit()

                # Insert test data
                values = ", ".join([f"('value_{i}')" for i in range(1000)])
                conn.execute(
                    text(f"""
                    INSERT INTO test_index (value) VALUES {values}
                """)
                )
                conn.commit()

                # Create index
                conn.execute(
                    text("""
                    CREATE INDEX IF NOT EXISTS idx_test_value
                    ON test_index(value)
                """)
                )
                conn.commit()

                # Query with index
                result = conn.execute(
                    text("""
                    SELECT value FROM test_index WHERE value = 'value_500'
                """)
                )
                value = result.scalar()
                assert value == "value_500"

                # Clean up
                conn.execute(text("DROP TABLE IF EXISTS test_index"))
                conn.commit()
        finally:
            engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
