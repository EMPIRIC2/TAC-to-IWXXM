"""Test both username formats for Supabase pooler."""
from sqlalchemy import create_engine, text
import sys

# Test both formats
formats = [
    ("postgres.ktvxijislbtgqapllmuk", "With project reference"),
    ("postgres", "Without project reference"),
]

for username, description in formats:
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Username: {username}")
    print(f"{'='*60}")

    DATABASE_URL = f"postgresql+psycopg2://{username}:P2wT%5EgJ2iLBSwQ%21d4@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

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
