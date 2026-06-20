"""Pytest configuration for backend tests."""

import os
import sys
from pathlib import Path

import pytest

# Add tests directory to path so we can import test_fixtures
sys.path.insert(0, str(Path(__file__).parent))

# Import all fixtures from test_fixtures to make them available globally
pytest_plugins = ["test_fixtures"]


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers",
        "live_api: tests that require internet connection to aviationweather.gov (use -m 'not live_api' to skip)",
    )
    config.addinivalue_line("markers", "smoke: quick smoke tests for CI/CD pipelines (~30 seconds)")
    config.addinivalue_line("markers", "e2e: end-to-end tests requiring real services (database, auth, etc.)")


@pytest.fixture(autouse=True)
def check_live_api_tests(request):
    """Enable live_api tests by default, skip only if explicitly disabled.

    Set environment variable ENABLE_LIVE_API_TESTS=false to skip.
    Default behavior is to run these tests.
    """
    if "live_api" in request.keywords:
        enable_live_tests = os.getenv("ENABLE_LIVE_API_TESTS", "true").lower()
        if enable_live_tests == "false":
            pytest.skip("Live API tests disabled (ENABLE_LIVE_API_TESTS=false)")
