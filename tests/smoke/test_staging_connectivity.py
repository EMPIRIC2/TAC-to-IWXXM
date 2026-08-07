"""Live staging connectivity tests (H4).

Run against deployed Render stack when URLs are configured:

    pytest tests/smoke/test_staging_connectivity.py -m live

Requires: LIVE_API_URL, LIVE_FRONTEND_URL (STAGING_* fallbacks supported).

Provisional DOKS (D-S038-t63-waive): set PLAYWRIGHT_DOKS_PROVISIONAL=1 (or
DOKS_PROVISIONAL=1) plus DOKS_* hosts — requests hit the LB IP with Ingress Host
headers (see scripts/deploy/doks_provisional_live_env.sh).
"""

from __future__ import annotations

import pytest
from tests.live_env import (
    live_api_host_headers,
    live_api_url,
    live_frontend_url,
    warn_deprecated_env,
)

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

    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
        **live_api_host_headers(),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.options(
            f"{api_url}/health",
            headers=headers,
        )

    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected CORS allow-origin {origin!r} or '*', got {allow_origin!r}"
    )


@pytest.mark.asyncio
async def test_staging_cors_preflight_work_sessions_patch() -> None:
    """H4 — work-sessions PATCH preflight for F5 auto-save."""
    warn_deprecated_env()
    api_url = live_api_url()
    origin = live_frontend_url()
    if not api_url or not origin:
        pytest.skip(
            "LIVE_API_URL and LIVE_FRONTEND_URL not set — skip live H4 connectivity"
        )

    import httpx

    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "PATCH",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
        **live_api_host_headers(),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.options(
            f"{api_url}/api/v1/work-sessions",
            headers=headers,
        )

    assert response.status_code in (200, 204), response.text
    allow_methods = response.headers.get("access-control-allow-methods", "").upper()
    assert "PATCH" in allow_methods, allow_methods


@pytest.mark.asyncio
async def test_staging_cors_preflight_mass_ingest_post() -> None:
    """H4 — F33 mass ingest POST preflight from frontend origin (UJ-051 / EV-042)."""
    warn_deprecated_env()
    api_url = live_api_url()
    origin = live_frontend_url()
    if not api_url or not origin:
        pytest.skip(
            "LIVE_API_URL and LIVE_FRONTEND_URL not set — skip live H4 connectivity"
        )

    import httpx

    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
        **live_api_host_headers(),
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.options(
            f"{api_url}/api/v1/ingest/mass",
            headers=headers,
        )

    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected CORS allow-origin {origin!r} or '*', got {allow_origin!r}"
    )
    allow_methods = response.headers.get("access-control-allow-methods", "").upper()
    assert "POST" in allow_methods or allow_methods == "*", allow_methods
