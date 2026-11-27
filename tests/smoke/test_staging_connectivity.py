"""Live staging connectivity tests (H4).

Run against deployed Render stack when URLs are configured:

    pytest tests/smoke/test_staging_connectivity.py -m live

Requires: LIVE_API_URL, LIVE_FRONTEND_URL (STAGING_* fallbacks supported).

Provisional DOKS (D-S038-t63-waive): set PLAYWRIGHT_DOKS_PROVISIONAL=1 (or
DOKS_PROVISIONAL=1) plus DOKS_* hosts - requests hit the LB IP with Ingress Host
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
    """H4 - OPTIONS preflight from browser origin succeeds."""
    warn_deprecated_env()
    api_url = live_api_url()
    origin = live_frontend_url()
    if not api_url or not origin:
        pytest.skip(
            "LIVE_API_URL and LIVE_FRONTEND_URL not set - skip live H4 connectivity"
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
    """H4 - work-sessions PATCH preflight for F5 auto-save."""
    warn_deprecated_env()
    api_url = live_api_url()
    origin = live_frontend_url()
    if not api_url or not origin:
        pytest.skip(
            "LIVE_API_URL and LIVE_FRONTEND_URL not set - skip live H4 connectivity"
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
    """H4 - F33 mass ingest POST preflight from frontend origin (UJ-051 / EV-042)."""
    warn_deprecated_env()
    api_url = live_api_url()
    origin = live_frontend_url()
    if not api_url or not origin:
        pytest.skip(
            "LIVE_API_URL and LIVE_FRONTEND_URL not set - skip live H4 connectivity"
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


@pytest.mark.asyncio
async def test_staging_live_map_eval_get_returns_snapshot() -> None:
    """FR-045 — GET /api/v1/live-map/eval returns cron snapshot shape."""
    warn_deprecated_env()
    api_url = live_api_url()
    if not api_url:
        pytest.skip("LIVE_API_URL not set - skip live FR-045 connectivity")

    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{api_url}/api/v1/live-map/eval",
            headers=live_api_host_headers(),
        )

    assert response.status_code == 200, response.text
    body = response.json()
    computed_at = body.get("computed_at")
    assert isinstance(computed_at, str)
    assert computed_at
    assert isinstance(body.get("window_hours"), int)
    assert isinstance(body.get("products"), list)
    assert isinstance(body.get("partial_decode_count"), int)
    assert isinstance(body.get("lint_count"), int)
    assert isinstance(body.get("top_lint_codes"), list)
    assert isinstance(body.get("convert_failure_count"), int)
    iwxxm = body.get("iwxxm_validation")
    assert isinstance(iwxxm, dict)
    for key in ("pass", "fail", "skip"):
        assert key in iwxxm
    assert isinstance(body.get("failure_locations"), list)


@pytest.mark.asyncio
async def test_staging_live_map_eval_refresh_disabled() -> None:
    """FR-045 — staging keeps POST refresh off (cron owns writes)."""
    warn_deprecated_env()
    api_url = live_api_url()
    if not api_url:
        pytest.skip("LIVE_API_URL not set - skip live FR-045 connectivity")

    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{api_url}/api/v1/live-map/eval/refresh",
            headers=live_api_host_headers(),
        )

    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_staging_eval_benchmark_get_returns_snapshot() -> None:
    """FR-064 / NFR-028 — GET station-health/eval-benchmark returns snapshot shape."""
    warn_deprecated_env()
    api_url = live_api_url()
    if not api_url:
        pytest.skip("LIVE_API_URL not set - skip live eval-benchmark connectivity")

    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{api_url}/api/v1/station-health/eval-benchmark",
            headers=live_api_host_headers(),
        )

    assert response.status_code == 200, response.text
    body = response.json()
    computed_at = body.get("computed_at")
    assert isinstance(computed_at, str)
    assert computed_at
    assert isinstance(body.get("product_breakdown"), list)
    assert isinstance(body.get("partial_decode_count"), int)
    assert isinstance(body.get("lint_count"), int)
    iwxxm = body.get("iwxxm_validation")
    assert isinstance(iwxxm, dict)
    for key in ("pass", "fail", "skip"):
        assert key in iwxxm


@pytest.mark.asyncio
async def test_staging_eval_benchmark_rejects_invalid_icao() -> None:
    """FR-064 / NFR-028 — invalid ICAO filter is rejected (validation failure)."""
    warn_deprecated_env()
    api_url = live_api_url()
    if not api_url:
        pytest.skip("LIVE_API_URL not set - skip live eval-benchmark connectivity")

    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{api_url}/api/v1/station-health/eval-benchmark",
            params={"icao": "BAD"},
            headers=live_api_host_headers(),
        )

    assert response.status_code == 400, response.text
