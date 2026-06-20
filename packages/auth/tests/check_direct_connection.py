"""Test Supabase direct connection (from dashboard)."""

from sqlalchemy import create_engine, text
import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

print("Testing Supabase Direct Connection")
print("=" * 60)

# Use environment variable for connection string
DATABASE_URL = os.getenv(
    "TEST_DIRECT_CONNECTION_URL",
    "postgresql+psycopg2://postgres:password@db.project-ref.supabase.co:5432/postgres?sslmode=require",
)

if "project-ref" in DATABASE_URL or "password" in DATABASE_URL:
    pytest.skip("TEST_DIRECT_CONNECTION_URL not set - skipping direct connection test", allow_module_level=True)

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    with engine.connect() as connection:
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

        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Supabase direct connection works!")
        print("=" * 60)
        sys.exit(0)

except Exception as e:
    print(f"\n❌ FAILED: {type(e).__name__}")
    error_str = str(e)
    if "IPv6" in error_str or "getaddrinfo" in error_str or "Name or service not known" in error_str:
        print("Error: IPv6-only DNS (expected on this system)")
        print("\nNote: Your system doesn't support IPv6, so the direct connection")
        print("to db.YOUR_PROJECT_REF.supabase.co won't work.")
        print("\nSolution: Enable the Connection Pooler in Supabase dashboard:")
        print("1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT_REF/settings/database")
        print("2. In 'Connection pooling' section, select 'Session' or 'Transaction' mode")
        print("3. Copy the pooler connection string (uses aws-0-us-east-1.pooler.supabase.com)")
        print("4. Update DATABASE_URL in .env with the pooler connection string")
    else:
        print(f"Error: {error_str[:300]}")
    sys.exit(1)
