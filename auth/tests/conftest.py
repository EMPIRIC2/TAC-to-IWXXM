"""Pytest configuration for auth tests.

Auth service is now a Supabase proxy - no local database.
Tests use FastAPI TestClient to test API endpoints.
"""
import os
import pytest

# Set required environment variables for auth service
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
os.environ["FRONTEND_BASE_URL"] = "http://localhost:8000"


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return "asyncio"
