"""Test script to verify Supabase connection."""
import os
from sqlalchemy import create_engine, text

# Test the connection with the official format
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:P2wT%5EgJ2iLBSwQ%21d4@db.ktvxijislbtgqapllmuk.supabase.co:5432/postgres?sslmode=require"
)

print(f"Testing connection to: {DATABASE_URL.split('@')[1]}")

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
