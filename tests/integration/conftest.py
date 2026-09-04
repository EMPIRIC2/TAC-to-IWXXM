"""Fixtures for live stack integration tests."""

from __future__ import annotations

import os

import httpx
import pytest
from tests.live_fixtures import obtain_live_api_token, wake_live_api

LIVE_API_TIMEOUT = 30.0


@pytest.fixture(autouse=True, scope="session")
def _require_live_integration_opt_in() -> None:
    """Avoid hitting Render unless explicitly requested (make test-live-integration)."""
    if os.environ.get("RUN_LIVE_TESTS", "").lower() not in ("1", "true", "yes"):
        pytest.skip(
            "Live integration tests require RUN_LIVE_TESTS=1 (make test-live-integration)"
        )


@pytest.fixture(scope="session")
def live_api_token() -> str:
    """Bearer token from POST /auth/login (runtime - do not persist)."""
    return obtain_live_api_token()


@pytest.fixture
async def live_client_public():
    """httpx client for unauthenticated live API calls."""
    base_url = wake_live_api()
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=LIVE_API_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
async def live_client(live_api_token: str):
    """httpx client with runtime JWT."""
    base_url = wake_live_api()
    headers = {"Authorization": f"Bearer {live_api_token}"}
    async with httpx.AsyncClient(
        base_url=base_url,
        headers=headers,
        timeout=LIVE_API_TIMEOUT,
        follow_redirects=True,
    ) as client:
        yield client
