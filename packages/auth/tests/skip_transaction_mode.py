"""Test Supabase Transaction Mode pooler (port 6543)."""

from sqlalchemy import create_engine, text
import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

print("Testing Supabase Transaction Mode Pooler")
print("Port 6543 (Transaction Mode)")
print("=" * 60)

# Transaction mode uses port 6543
# Username format for transaction mode: postgres.PROJECT_REF
DATABASE_URL = os.getenv(
    "TEST_TRANSACTION_POOLER_URL",
    "postgresql+psycopg2://postgres.project-ref:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
)

if "project-ref" in DATABASE_URL:
    pytest.skip("TEST_TRANSACTION_POOLER_URL not set - skipping transaction pooler test", allow_module_level=True)

try:
    # Transaction mode doesn't support prepared statements
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"options": "-c statement_timeout=30000"})

    with engine.connect() as connection:
        # Use execution_options to disable prepared statements
        connection = connection.execution_options(postgresql_use_native_compiled=False)

        result = connection.execute(text("SELECT 1 as test"))
        assert result.scalar() == 1
        print("✓ Basic query successful")

        result = connection.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✓ PostgreSQL version: {version[:80]}...")

        result = connection.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        print(f"✓ Connected to database: {db_name}")

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
            VALUES ('Test from metar-to-IWXXM via transaction pooler')
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

    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Supabase Transaction Mode pooler works!")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print(f"\n❌ FAILED: {type(e).__name__}")
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
