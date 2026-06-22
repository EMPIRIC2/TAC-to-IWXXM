"""Live stack integration tests — cross-service H3 + H4 against Render.

Targets:
  API:      https://metar-to-iwxxm-api.onrender.com
  Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com

Run:
  make test-live-integration
  LIVE_API_URL=... LIVE_FRONTEND_URL=... pytest tests/integration/test_live_stack.py -m live -v
"""

from __future__ import annotations

import httpx
import pytest
from tests.live_env import live_api_url, live_frontend_url, warn_deprecated_env
from tests.live_fixtures import DEFAULT_LIVE_API, live_api_base, wake_live_api

DEFAULT_LIVE_FRONTEND = "https://metar-to-iwxxm-frontend-v4-web.onrender.com"

SAMPLE_METAR = "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015 RMK AO2 SLP210"

pytestmark = [pytest.mark.integration, pytest.mark.live]


def _frontend_url() -> str:
    return (live_frontend_url() or DEFAULT_LIVE_FRONTEND).rstrip("/")


@pytest.mark.asyncio
async def test_live_frontend_serves_app_shell() -> None:
    """H6 prerequisite — static frontend is reachable and serves the converter shell."""
    warn_deprecated_env()
    origin = _frontend_url()
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(f"{origin}/")
    assert response.status_code == 200
    body = response.text
    assert "METAR" in body or "metar" in body.lower()


@pytest.mark.asyncio
async def test_live_cors_preflight_from_frontend_origin() -> None:
    """H4 — browser origin allowed on API preflight."""
    warn_deprecated_env()
    api_url = live_api_base()
    origin = _frontend_url()
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


@pytest.mark.asyncio
async def test_live_api_public_health_path(live_client_public) -> None:
    """H3 — public health + versions respond on deployed API."""
    health = await live_client_public.get("/health")
    assert health.status_code == 200
    data = health.json()
    assert data.get("status") in ("healthy", "ok", "degraded")

    versions = await live_client_public.get("/api/v1/versions")
    assert versions.status_code == 200
    supported = versions.json().get("supported_versions", [])
    assert any(v.get("version") == "2025-2" for v in supported)


@pytest.mark.asyncio
async def test_live_convert_then_validate_round_trip(live_client) -> None:
    """TC-LIVE-002 — convert TAC then validate IWXXM on live API."""
    convert = await live_client.post(
        "/api/v1/convert",
        json={"metars": [SAMPLE_METAR], "version": "2025-2"},
    )
    assert convert.status_code == 200, convert.text
    convert_data = convert.json()
    assert convert_data.get("successful", 0) >= 1
    xml_content = convert_data["results"][0]["content"]
    assert "iwxxm" in xml_content.lower()

    validate = await live_client.post(
        "/api/v1/validation/validate",
        json={"content": xml_content, "version": "2025-2"},
    )
    assert validate.status_code == 200, validate.text
    validate_data = validate.json()
    assert "passed" in validate_data
    assert "results" in validate_data


@pytest.mark.asyncio
async def test_live_auth_login_rejects_bad_credentials() -> None:
    """Auth route on merged API rejects invalid credentials."""
    api_url = wake_live_api()
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{api_url}/auth/login",
            json={"email": "not-a-real-user@example.com", "password": "wrong-password"},
        )
    assert response.status_code in (401, 403, 422)


def test_live_env_defaults_match_render_stack(monkeypatch: pytest.MonkeyPatch) -> None:
    """Documented Render URLs are used when LIVE_* vars are unset."""
    for key in (
        "LIVE_API_URL",
        "LIVE_FRONTEND_URL",
        "STAGING_API_URL",
        "STAGING_FRONTEND_ORIGIN",
        "E2E_API_URL",
        "E2E_FRONTEND_URL",
    ):
        monkeypatch.delenv(key, raising=False)
    assert live_api_url() == ""
    assert live_api_base() == DEFAULT_LIVE_API
    assert _frontend_url() == DEFAULT_LIVE_FRONTEND
