"""Fixtures for live API infrastructure tests (H3)."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest

# Repo-root tests package (shared live harness)
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.live_fixtures import (  # noqa: E402
    live_api_base,
    obtain_live_api_token,
    wake_live_api,
)

LIVE_API_TIMEOUT = 30.0


@pytest.fixture(scope="session")
def live_api_token() -> str:
    """Obtain bearer token via POST /auth/login (runtime — do not persist)."""
    return obtain_live_api_token()


@pytest.fixture
async def live_client(live_api_token: str):
    """Create httpx AsyncClient for live API testing with runtime JWT."""
    base_url = wake_live_api()
    headers = {"Authorization": f"Bearer {live_api_token}"}
    async with httpx.AsyncClient(
        base_url=base_url,
        headers=headers,
        timeout=LIVE_API_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
async def live_client_public():
    """Create httpx AsyncClient without auth for public endpoint tests."""
    base_url = wake_live_api()
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=LIVE_API_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
def verify_live_api_configured():
    """Verify live API URL is configured (non-localhost default)."""
    if live_api_base() == "http://localhost:8000":
        pytest.skip("LIVE_API_URL not configured or using default")
