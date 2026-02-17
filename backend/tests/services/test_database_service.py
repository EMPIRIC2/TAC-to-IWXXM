"""
Tests for the database connection service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.database import (
    get_database_url,
    init_db_engine,
    get_db_session,
    database_lifespan,
    test_db_connection,
    get_db_stats
)


class TestGetDatabaseUrl:
    """Test database URL construction."""
    
    def test_from_database_url(self):
        """Test using DATABASE_URL environment variable."""
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql+psycopg2://user:pass@localhost/db'}):
            url = get_database_url()
            # Should convert psycopg2 to asyncpg for async operations
            assert 'postgresql' in url
            assert 'user:pass' in url
            assert 'localhost' in url
    
    def test_psycopg2_to_asyncpg_conversion(self):
        """Test conversion of psycopg2 dialect to asyncpg for async operations."""
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql+psycopg2://user:pass@localhost/db'}):
            url = get_database_url()
            # Should be converted to asyncpg dialect
            assert 'postgresql+asyncpg://' in url
    
    def test_from_supabase_url(self):
        """Test using SUPABASE_DB_URL environment variable."""
        with patch.dict('os.environ', {
            'SUPABASE_DB_URL': 'postgresql://postgres:secret@db.supabase.co/postgres'
        }, clear=True):
            url = get_database_url()
            assert 'postgresql' in url
            assert 'db.supabase.co' in url
    
    def test_from_components(self):
        """Test constructing URL from component environment variables."""
        with patch.dict('os.environ', {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass'
        }, clear=True):
            url = get_database_url()
            assert 'localhost' in url
            assert 'testdb' in url
            assert 'testuser' in url
            assert 'testpass' in url
    
    def test_priority_order(self):
        """Test that DATABASE_URL takes priority."""
        with patch.dict('os.environ', {
            'DATABASE_URL': 'postgresql+psycopg2://priority@localhost/db',
            'SUPABASE_DB_URL': 'postgresql://supabase@localhost/db',
            'POSTGRES_HOST': 'other_host'
        }):
            url = get_database_url()
            # DATABASE_URL takes priority
            assert 'priority@localhost' in url
    
    def test_missing_all_config(self):
        """Test default configuration when no explicit config is provided."""
        with patch.dict('os.environ', {}, clear=True):
            # Should return default localhost URL with empty password
            url = get_database_url()
            assert "postgresql" in url
            assert "localhost" in url
            assert "asyncpg" in url


@pytest.mark.asyncio
class TestInitDbEngine:
    """Test database engine initialization."""
    
    async def test_init_db_engine_success(self):
        """Test successful engine initialization."""
        global _engine, _async_session_maker
        # Reset globals for this test
        import src.services.database as db_module
        db_module._engine = None
        db_module._async_session_maker = None
        
        with patch('src.services.database.get_database_url', return_value='postgresql+asyncpg://localhost/test'):
            with patch('src.services.database.create_async_engine') as mock_create:
                mock_engine = AsyncMock()
                mock_create.return_value = mock_engine
                
                engine = await init_db_engine()
                
                # Engine should be created
                mock_create.assert_called_once()


@pytest.mark.asyncio
class TestGetDbSession:
    """Test database session context manager."""
    
    async def test_get_db_session_no_engine(self):
        """Test error when engine is not initialized."""
        with patch('src.services.database._async_session_maker', None):
            with pytest.raises(RuntimeError, match="Database engine not initialized"):
                async with get_db_session():
                    pass


@pytest.mark.asyncio
class TestDatabaseLifespan:
    """Test FastAPI lifespan management."""
    
    async def test_lifespan_startup(self):
        """Test database engine initialization on startup."""
        with patch('src.services.database.init_db_engine', new_callable=AsyncMock) as mock_init:
            with patch('src.services.database.close_db_engine', new_callable=AsyncMock) as mock_close:
                with patch('src.services.database.create_tables', new_callable=AsyncMock) as mock_create:
                    from fastapi import FastAPI
                    app = FastAPI()
                    
                    # Execute lifespan
                    async with database_lifespan(app):
                        # Engine should be initialized
                        mock_init.assert_called_once()
                        mock_create.assert_called_once()
                    
                    # close_db_engine should be called after exit
                    mock_close.assert_called_once()


@pytest.mark.asyncio
class TestTestDbConnection:
    """Test database connection testing."""
    
    async def test_test_db_connection_no_engine(self):
        """Test connection test when engine is not initialized."""
        with patch('src.services.database._async_session_maker', None):
            result = await test_db_connection()
            # Should handle gracefully
            assert isinstance(result, bool)


@pytest.mark.asyncio
class TestGetDbStats:
    """Test database statistics retrieval."""
    
    async def test_get_db_stats_no_engine(self):
        """Test stats retrieval when engine is not initialized."""
        with patch('src.services.database._engine', None):
            stats = await get_db_stats()
            
            assert stats['status'] == 'not_initialized'
            assert stats['pool_size'] == 0

