"""Shared test fixtures and utilities for backend tests.

This module provides common fixtures used across multiple test files to ensure consistent test setup and reduce code duplication.

Fixtures:
- client: TestClient with regular user authentication
- admin_client: TestClient with admin authentication
- unauthenticated_client: TestClient without authentication
- live_api_client: httpx AsyncClient for live API testing
- mock_supabase_client: Mock Supabase database client
- mock_aviation_weather_client: Mock Aviation Weather API client
- test_database_engine: Real PostgreSQL engine for E2E tests
- sample_metars: Sample METAR data for testing
"""

import os
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token

# ============================================================================
# Global Test Configuration
# ============================================================================

# Disable statistics logging during tests to avoid database errors
os.environ["ENABLE_STATISTICS"] = "false"

# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def client():
    """Create test client with mocked regular user authentication.

    Returns TestClient configured with:
    - User ID: test-user-id
    - Role: user
    - Audience: test-project
    """

    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project", "role": "user"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client():
    """Create test client with mocked admin authentication.

    Returns TestClient configured with:
    - User ID: admin-user-id
    - Role: admin
    - Audience: test-project
    """

    async def override_verify_token_admin():
        return {"sub": "admin-user-id", "aud": "test-project", "role": "admin"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token_admin
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client():
    """Create test client without authentication.

    Use this for testing:
    - Public endpoints
    - Authentication requirements
    - 401 error responses
    """
    return TestClient(app)


@pytest.fixture
def user_client(client):
    """Alias for client fixture for clarity.

    Useful when you need to distinguish between admin and regular user clients.
    """
    return client


# ============================================================================
# Live API Testing Fixtures
# ============================================================================


@pytest.fixture
async def live_api_client():
    """Create httpx AsyncClient for live API testing.

    Configuration via environment variables:
    - LIVE_API_URL: Base URL of deployed API (default: http://localhost:8000)
    - LIVE_API_TOKEN: Bearer token for authenticated endpoints
    - LIVE_API_TIMEOUT: Request timeout in seconds (default: 30)

    Usage:
        @pytest.mark.live_api
        async def test_something(live_api_client):
            response = await live_api_client.get("/health")
    """
    live_api_url = os.getenv("LIVE_API_URL", "http://localhost:8000")
    live_api_token = os.getenv("LIVE_API_TOKEN", "")
    timeout = int(os.getenv("LIVE_API_TIMEOUT", "30"))

    headers = {}
    if live_api_token:
        headers["Authorization"] = f"Bearer {live_api_token}"

    async with httpx.AsyncClient(
        base_url=live_api_url, headers=headers, timeout=timeout, follow_redirects=True
    ) as client:
        yield client


# ============================================================================
# Mock Service Fixtures
# ============================================================================


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for database operations.

    Returns a mock AsyncClient with configurable responses.

    Usage:
        def test_something(mock_supabase_client):
            mock_supabase_client.get.return_value = AsyncMock(
                json=MagicMock(return_value=[{"id": "123"}]),
                raise_for_status=MagicMock()
            )
    """
    with patch("src.routers.evaluation.get_supabase_client") as mock:
        mock_client = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_statistics_service():
    """Mock statistics service for ICAO OPMET testing.

    Returns a mock statistics_service with configurable methods.

    Usage:
        def test_something(mock_statistics_service):
            mock_statistics_service.get_statistics.return_value = {...}
    """
    with patch("src.routers.icao_opmet.statistics_service") as mock:
        yield mock


@pytest.fixture
def mock_aviation_weather_client():
    """Mock Aviation Weather API client for evaluation testing.

    Returns a mock AviationWeatherClient with configurable responses.

    Usage:
        def test_something(mock_aviation_weather_client):
            mock_aviation_weather_client.fetch_metar_batch.return_value = {
                "KJFK": ("METAR...", "<iwxxm>...</iwxxm>")
            }
    """
    with patch("src.clients.aviation_weather_client.AviationWeatherClient") as mock_class:
        mock_client = AsyncMock()
        mock_class.return_value.__aenter__.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_validation_orchestrator():
    """Mock validation orchestrator for validation testing.

    Returns a mock ValidationOrchestrator with configurable responses.
    """
    with patch("src.services.validation_orchestrator.get_validation_orchestrator") as mock:
        mock_orchestrator = MagicMock()
        mock.return_value = mock_orchestrator
        yield mock_orchestrator


# ============================================================================
# Database Fixtures (for E2E tests)
# ============================================================================


@pytest.fixture
async def test_database_engine():
    """Create real PostgreSQL engine for E2E tests.

    Requires DATABASE_URL environment variable pointing to test database.

    Warning: This uses a real database. Ensure using test database, not production!

    Usage:
        @pytest.mark.e2e
        async def test_something(test_database_engine):
            async with test_database_engine.begin() as conn:
                await conn.execute(...)
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/test")

    if "test" not in database_url.lower():
        pytest.skip("DATABASE_URL must contain 'test' for E2E tests (safety check)")

    engine = create_async_engine(database_url, echo=False)
    yield engine
    await engine.dispose()


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_metars() -> Dict[str, str]:
    """Sample METAR messages for testing.

    Returns a dictionary mapping ICAO airport codes to METAR strings.

    Keys are airport codes (KJFK, KORD, EGLL, etc.) with realistic METAR data.
    """
    return {
        "KJFK": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
        "KORD": "METAR KORD 161200Z 27015G25KT 3SM -SHRA BR FEW015 BKN025 OVC050 18/16 A2990 RMK AO2",
        "EGLL": "METAR EGLL 161200Z 27015KT 9999 FEW040 18/12 Q1015",
        "LFPG": "METAR LFPG 161200Z 36008KT CAVOK 22/10 Q1025",
        "RJTT": "SPECI RJTT 161215Z 09008KT 10SM FEW030 20/15 A2995",
        "FAOR": "METAR FAOR 161200Z 18010KT 9999 SCT030 25/18 Q1020",
        "EDDM": "METAR EDDM 161200Z 12012KT 9999 SCT040 21/14 Q1018",
        "VHHH": "METAR VHHH 161200Z 15008KT 9999 BKN035 28/24 Q1010",
        "SBGR": "METAR SBGR 161200Z 18015KT 9999 FEW030 26/22 A2990",
        "OMDB": "METAR OMDB 161200Z 12010KT CAVOK 32/18 Q1012",
        # Additional examples by condition
        "CYYZ": "METAR CYYZ 161200Z 36012KT 1SM SN BKN015 OVC025 -05/-07 A2995",
    }


@pytest.fixture
def sample_iwxxm() -> str:
    """Sample IWXXM XML for validation testing.

    Returns a minimal valid IWXXM 2025-2 document.
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR
    xmlns:iwxxm="http://icao.int/iwxxm/2025-2"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://icao.int/iwxxm/2025-2 http://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd"
    gml:id="metar-KJFK-20260216120000"
    status="NORMAL">
    <iwxxm:observation>
        <om:OM_Observation gml:id="obs-KJFK-20260216120000">
            <!-- Minimal observation content -->
        </om:OM_Observation>
    </iwxxm:observation>
</iwxxm:METAR>"""


@pytest.fixture
def sample_station_ids() -> List[str]:
    """Sample ICAO station IDs for testing.

    Returns list of major international airports across all ICAO regions.
    """
    return [
        "KJFK",  # New York JFK (NAM)
        "KORD",  # Chicago ORD (NAM)
        "EGLL",  # London Heathrow (EUR)
        "LFPG",  # Paris CDG (EUR)
        "EDDM",  # Munich (EUR)
        "RJTT",  # Tokyo NRT (APAC)
        "VHHH",  # Hong Kong (APAC)
        "FAOR",  # Johannesburg (AFI)
        "SBGR",  # São Paulo (SAM)
        "OMDB",  # Dubai (MID)
    ]


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def test_environment():
    """Set up test environment variables.

    This fixture runs automatically for all tests (autouse=True).
    """
    original_env = os.environ.copy()

    # Set test environment variables
    test_vars = {
        "ENABLE_WEBHOOKS": "false",
        "IWXXM_VERSION": "2025-2",
    }

    # Only set if not already set
    for key, value in test_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def disable_auth():
    """Temporarily disable authentication for testing.

    Usage:
        def test_something(disable_auth):
            # Auth is disabled for this test
    """
    with patch.dict(os.environ, {"DISABLE_AUTH": "true"}):
        yield


# ============================================================================
# Performance Testing Fixtures
# ============================================================================


@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing.

    Usage:
        def test_something(performance_timer):
            with performance_timer("operation_name") as timer:
                # ... do something ...
                pass
            assert timer.elapsed < 1.0  # Assert took less than 1 second
    """
    import time
    from contextlib import contextmanager

    class Timer:
        def __init__(self):
            self.elapsed = 0.0

        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            self.elapsed = time.time() - self.start

    @contextmanager
    def timer(name: str):
        t = Timer()
        with t:
            yield t
        print(f"{name}: {t.elapsed:.3f}s")

    return timer


# ============================================================================
# Conditional Skip Fixtures
# ============================================================================


@pytest.fixture
def skip_if_no_live_api():
    """Skip test if live API is not configured.

    Usage:
        def test_something(skip_if_no_live_api):
            # Test will skip if LIVE_API_URL not set
    """
    live_api_url = os.getenv("LIVE_API_URL", "")
    if not live_api_url or live_api_url == "http://localhost:8000":
        pytest.skip("LIVE_API_URL not configured")


@pytest.fixture
def skip_if_no_database():
    """Skip test if test database is not configured.

    Usage:
        def test_something(skip_if_no_database):
            # Test will skip if DATABASE_URL not set
    """
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        pytest.skip("DATABASE_URL not configured")


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "smoke: Quick smoke tests for CI/CD")
    config.addinivalue_line("markers", "e2e: End-to-end tests requiring real services")
    # live_api marker already registered in conftest.py
