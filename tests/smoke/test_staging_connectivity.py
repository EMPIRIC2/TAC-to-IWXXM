"""Live staging connectivity tests (H4).

Run against deployed staging when URLs are configured:

    pytest tests/smoke/test_staging_connectivity.py -m live

Requires: STAGING_API_URL, STAGING_FRONTEND_ORIGIN (see docs/staging-secrets-matrix.md).
"""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = pytest.mark.live


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.skip(f"{name} not set — skip live H4 connectivity")
    return value


@pytest.mark.asyncio
async def test_staging_cors_preflight_allows_frontend_origin() -> None:
    """H4 — OPTIONS preflight from browser origin succeeds."""
    api_url = _require_env("STAGING_API_URL").rstrip("/")
    origin = _require_env("STAGING_FRONTEND_ORIGIN")

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
