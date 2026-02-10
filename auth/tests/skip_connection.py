"""Test script to verify Supabase connection."""
import os
import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Test the connection with the official format
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@db.project-ref.supabase.co:5432/postgres?sslmode=require"
)

if "project-ref" in DATABASE_URL or DATABASE_URL.endswith("postgres?sslmode=require"):
    pytest.skip(
        "DATABASE_URL not set or contains placeholders - skipping connection test",
        allow_module_level=True
    )

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✓ Connection successful!")
        print(f"PostgreSQL version: {version}")

        # Test table creation
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message TEXT
            )
        """))
        connection.commit()

        # Insert test data
        connection.execute(text("""
            INSERT INTO test_connection (message) VALUES ('Test from metar-to-IWXXM')
        """))
        connection.commit()

        # Query test data
        result = connection.execute(
            text("SELECT COUNT(*) FROM test_connection"))
        count = result.scalar()
        print(f"✓ Test table created and populated: {count} rows")

        # Clean up
        connection.execute(text("DROP TABLE test_connection"))
        connection.commit()
        print("✓ Test table cleaned up")

except Exception as e:
    print(f"✗ Connection failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
