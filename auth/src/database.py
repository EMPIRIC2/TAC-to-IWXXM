"""Database setup for authentication module."""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# In Docker, env vars come from docker-compose.yml
# For local dev, you can use python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required in production

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./auth.db"  # Default to SQLite for local dev
)


class Base(DeclarativeBase):
    pass


# Configure engine based on database type
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL with connection pooling for production
    # Notes on pooler modes:
    # - Transaction pooler (port 6543): Ideal for serverless/stateless apps, does NOT support PREPARE statements
    # - Session pooler (port 5432): Better for long-lived connections, supports prepared statements

    connect_args = {}

    # Supabase transaction pooler doesn't support prepared statements
    # Disable them using execution_options in connection
    if "pooler.supabase.com" in DATABASE_URL and ":6543/" in DATABASE_URL:
        # Transaction mode pooler - disable prepared statements
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # Test connection before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            execution_options={
                "postgresql_psycopg2_prepared_statements": False},
        )
    else:
        # Standard PostgreSQL or session mode pooler
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "sslmode": "require"} if "sslmode" not in DATABASE_URL else {},
        )
else:
    # SQLite for local development
    engine = create_engine(
        DATABASE_URL,
        # Allow SQLite to work with FastAPI
        connect_args={"check_same_thread": False},
    )
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def init_db():
    # Import models to register them with Base
    _ensure_models_imported()
    Base.metadata.create_all(bind=engine)


def _ensure_models_imported():
    """Ensure models are imported and registered with Base."""
    try:
        from auth import models  # noqa: F401
    except ImportError:
        pass  # Models may not be available in some contexts


# Import models at module level to register them with Base.metadata
_ensure_models_imported()


__all__ = ["DATABASE_URL", "engine", "SessionLocal", "Base", "init_db"]
