"""BUG-2026-06-20 - production login Failed to fetch (CORS).

Browser symptom: TypeError: Failed to fetch on POST /auth/login from the
production frontend origin. Root cause: deployed API missing METAR_CORS_ORIGINS.

Live probe (requires STAGING_* env vars):

    STAGING_API_URL=https://metar-to-iwxxm-api.onrender.com \\
    STAGING_FRONTEND_ORIGIN=https://metar-to-iwxxm-frontend-v4-web.onrender.com \\
      pytest tests/bugs/test_bug_2026_06_20_login_cors_failed_fetch.py -m live -v
"""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.live

PRODUCTION_API = "https://metar-to-iwxxm-api.onrender.com"
PRODUCTION_FRONTEND = "https://metar-to-iwxxm-frontend-v4-web.onrender.com"


def _require_env(name: str, default: str) -> str:
    value = os.environ.get(name, default).strip()
    if not value:
        pytest.skip(f"{name} not set - skip live repro")
    return value


@pytest.mark.asyncio
async def test_bug_login_cors_preflight_allows_production_frontend() -> None:
    """Repro: OPTIONS /auth/login from frontend origin must succeed (H4)."""
    api_url = _require_env("STAGING_API_URL", PRODUCTION_API).rstrip("/")
    origin = _require_env("STAGING_FRONTEND_ORIGIN", PRODUCTION_FRONTEND)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.options(
            f"{api_url}/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected allow-origin {origin!r} or '*', got {allow_origin!r}"
    )
