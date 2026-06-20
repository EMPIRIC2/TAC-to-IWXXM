"""Backend-specific pytest configuration and fixtures.

This file ensures backend src is importable in tests and sets up environment.
All other pytest configuration is in pyproject.toml.
"""

import os

import pytest

from src.schemas.airport import get_airport_validator

# Set test environment variables BEFORE any imports of modules that use os.getenv()
# This must be done at module load time before pytest collects tests
os.environ.setdefault("DISABLE_AUTH", "false")
os.environ.setdefault("ENABLE_WEBHOOKS", "false")
# Use postgresql+asyncpg:// for SQLAlchemy async engine with psycopg driver
# The async engine will convert this appropriately for asyncpg
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/test")
os.environ.setdefault("IWXXM_VERSION", "2025-2")


@pytest.fixture(scope="session", autouse=True)
def ensure_airport_data():
    """Ensure airport data is loaded before any tests run.

    This fixture runs once per test session and ensures the AirportValidator
    singleton has loaded the airports.json data file. This is required for
    METAR conversion tests that need airport metadata.
    """
    # Get the validator singleton (will initialize and load data if needed)
    validator = get_airport_validator()
    assert validator.count() > 0, "Airport data not loaded"

    return validator
