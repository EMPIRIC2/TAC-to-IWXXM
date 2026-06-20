"""Quick test script to verify Supabase pooler connection."""

from sqlalchemy import create_engine, text
import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Test pooler connection (Session Mode - port 5432)
# Use environment variable, with fallback to default URL scheme
DATABASE_URL = os.getenv(
    "TEST_POOLER_URL",
    "postgresql+psycopg2://postgres.project-ref:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
)
if "project-ref" in DATABASE_URL:
    pytest.skip("TEST_POOLER_URL not set - skipping pooler connection test", allow_module_level=True)

print(f"Testing connection to Supabase via IPv4 pooler (Session Mode)...")
print(f"Host: aws-0-us-east-1.pooler.supabase.com:5432")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    with engine.connect() as connection:
        # Test basic query
        result = connection.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        print("✓ Basic query successful")

        # Get version
        result = connection.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✓ PostgreSQL version: {version[:50]}...")

        # Get current database
        result = connection.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        print(f"✓ Connected to database: {db_name}")

        # Get current user
        result = connection.execute(text("SELECT current_user"))
        user = result.scalar()
        print(f"✓ Connected as user: {user}")

        # Test table creation
        connection.execute(
            text("""
            CREATE TABLE IF NOT EXISTS test_pooler_connection (
                id SERIAL PRIMARY KEY,
                message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        )
        connection.commit()
        print("✓ Test table created")

        # Insert test data
        connection.execute(
            text("""
            INSERT INTO test_pooler_connection (message)
            VALUES ('Test from metar-to-IWXXM via pooler')
        """)
        )
        connection.commit()
        print("✓ Test data inserted")

        # Query data
        result = connection.execute(text("SELECT COUNT(*) FROM test_pooler_connection"))
        count = result.scalar()
        print(f"✓ Test table has {count} rows")

        # Clean up
        connection.execute(text("DROP TABLE test_pooler_connection"))
        connection.commit()
        print("✓ Test table cleaned up")

    print("\n🎉 SUCCESS! Supabase connection via IPv4 pooler works!")

except Exception as e:
    print(f"\n❌ FAILED: {type(e).__name__}")
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
