"""
Database connection management for PostgreSQL using SQLAlchemy.

Provides async session management for statistics and other database operations.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)

# Database engine and session maker (singletons)
_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker] = None


def get_database_url() -> str:
    """
    Get PostgreSQL connection URL from environment.

    Supports multiple environment variable formats:
    - DATABASE_URL (standard PostgreSQL URL)
    - SUPABASE_DB_URL (Supabase specific)
    - Individual components (POSTGRES_HOST, POSTGRES_DB, etc.)

    Returns:
        PostgreSQL connection URL with SQLAlchemy async dialect

    Raises:
        ValueError: If no valid database configuration found
    """
    # Try direct DATABASE_URL first
    if database_url := os.getenv("DATABASE_URL"):
        # Convert SQLAlchemy psycopg2 dialect to asyncpg dialect for async operations
        # Both are valid SQL Alchemy URLs - psycopg2 dialect becomes asyncpg for async support
        database_url = database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
        return database_url

    # Try Supabase-specific URL
    if supabase_url := os.getenv("SUPABASE_DB_URL"):
        supabase_url = supabase_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
        return supabase_url

    # Build from components
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "postgres")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")

    if not password:
        logger.warning("No PostgreSQL password configured, using passwordless connection")

    # Use postgresql+asyncpg:// for SQLAlchemy 2.0 async with asyncpg driver
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


async def init_db_engine(
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
) -> AsyncEngine:
    """
    Initialize async database engine and session maker.

    Args:
        echo: Enable SQLAlchemy logging
        pool_size: Number of connections to keep in pool
        max_overflow: Maximum overflow connections beyond pool_size
        pool_pre_ping: Test connections before using them
        pool_recycle: Recycle connections after this many seconds

    Returns:
        AsyncEngine instance

    Raises:
        Exception: If connection fails
    """
    global _engine, _async_session_maker

    if _engine is not None:
        logger.info("Database engine already initialized")
        return _engine

    try:
        database_url = get_database_url()
        logger.info(f"Initializing database engine with URL: {database_url[:50]}...")

        # Create async engine
        _engine = create_async_engine(
            database_url,
            echo=echo,
            echo_pool=False,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
            # Connection parameters
            connect_args={
                "command_timeout": 60,
                "timeout": 60,
                # Disable prepared statement caches for PgBouncer transaction/statement pool modes
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
        )

        # Create async session maker
        _async_session_maker = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        logger.info("Database engine initialized successfully")
        return _engine

    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}", exc_info=True)
        raise


async def close_db_engine():
    """Close database engine and dispose of connections."""
    global _engine, _async_session_maker

    if _engine is not None:
        logger.info("Closing database engine")
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
        logger.info("Database engine closed")


def get_db_engine() -> Optional[AsyncEngine]:
    """
    Get existing database engine.

    Returns:
        AsyncEngine instance or None if not initialized
    """
    return _engine


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for acquiring database sessions.

    Usage:
        async with get_db_session() as session:
            result = await session.execute(select(SomeModel))

    Yields:
        AsyncSession instance

    Raises:
        RuntimeError: If engine not initialized
    """
    if _async_session_maker is None:
        raise RuntimeError("Database engine not initialized. Call init_db_engine() first.")

    async with _async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# Backward compatibility alias for async with get_db_connection()
get_db_connection = get_db_session


async def test_db_connection() -> bool:
    """
    Test database connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def get_db_stats() -> dict:
    """
    Get database engine statistics.

    Returns:
        Dictionary with pool statistics
    """
    if _engine is None:
        return {
            "status": "not_initialized",
            "pool_size": 0,
        }

    pool = _engine.pool
    return {
        "status": "active",
        "pool_size": pool.size() if hasattr(pool, 'size') else "unknown",
        "pool_checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else "unknown",
    }


# Lifespan context manager for FastAPI
@asynccontextmanager
async def database_lifespan(app):
    """
    FastAPI lifespan context manager for database engine.

    Usage:
        app = FastAPI(lifespan=database_lifespan)
    """
    # Startup
    logger.info("Initializing database engine on startup")
    try:
        await init_db_engine()
        # Create tables if they don't exist
        await create_tables()
        yield
    finally:
        # Shutdown
        logger.info("Closing database engine on shutdown")
        await close_db_engine()


async def create_tables():
    """
    Create all database tables defined in ORM models.

    This is called during application startup to ensure tables exist.
    It's safe to call multiple times - SQLAlchemy will skip existing tables.
    """
    if _engine is None:
        logger.error("Database engine not initialized, cannot create tables")
        return

    try:
        from ..models import Base

        logger.info("Creating database tables if they don't exist...")
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}", exc_info=True)
        # Don't raise - allow app to continue even if tables can't be created
        # (e.g., in test environments with read-only databases)

