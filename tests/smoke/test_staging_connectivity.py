"""Live staging connectivity tests (H4).

Run against deployed Render stack when URLs are configured:

    pytest tests/smoke/test_staging_connectivity.py -m live

Requires: LIVE_API_URL, LIVE_FRONTEND_URL (STAGING_* fallbacks supported).
"""

from __future__ import annotations

import pytest
from tests.live_env import live_api_url, live_frontend_url, warn_deprecated_env

pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_staging_cors_preflight_allows_frontend_origin() -> None:
    """H4 — OPTIONS preflight from browser origin succeeds."""
    warn_deprecated_env()
    api_url = live_api_url()
    origin = live_frontend_url()
    if not api_url or not origin:
        pytest.skip(
            "LIVE_API_URL and LIVE_FRONTEND_URL not set — skip live H4 connectivity"
        )

    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.options(
            f"{api_url}/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )

    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected CORS allow-origin {origin!r} or '*', got {allow_origin!r}"
    )
