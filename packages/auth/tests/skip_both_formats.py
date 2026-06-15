"""Test both username formats for Supabase pooler."""
from sqlalchemy import create_engine, text
import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get connection parameters from environment
BASE_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")
BASE_HOST = os.getenv("SUPABASE_POOLER_HOST", "aws-0-us-east-1.pooler.supabase.com")
BASE_PORT = os.getenv("SUPABASE_POOLER_PORT", "5432")
PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF", "")

if not BASE_PASSWORD or not PROJECT_REF:
    pytest.skip(
        "SUPABASE_DB_PASSWORD and SUPABASE_PROJECT_REF not set - skipping pooler format test",
        allow_module_level=True
    )

# Test both formats
formats = [
    (f"postgres.{PROJECT_REF}", "With project reference"),
    ("postgres", "Without project reference"),
]

for username, description in formats:
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Username: {username}")
    print(f"{'='*60}")

    DATABASE_URL = f"postgresql+psycopg2://{username}:{BASE_PASSWORD}@{BASE_HOST}:{BASE_PORT}/postgres"

    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            assert result.scalar() == 1
            print(f"✓ Connection SUCCESSFUL with {description}!")

            result = connection.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✓ Database: {db_name}")

            result = connection.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"✓ User: {user}")

            # Exit on success
            sys.exit(0)

    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}")
        print(f"  Error: {str(e)[:200]}")

print("\n" + "="*60)
print("Both formats failed! Please verify credentials in Supabase dashboard.")
print("="*60)
