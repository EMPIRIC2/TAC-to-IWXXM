"""T8.3 - H4 CORS + H5 frontend config resolve on staging.

Spec: connectivity-gates H4-H5; docs/deploy.md live runbook;
docs/sessions/S008-general-tac-iwxxm-converter/reports/execution-plan.md T8.3.
"""

from __future__ import annotations

import json
import os

import httpx
import pytest
from tests.live_env import live_api_url, live_frontend_url, warn_deprecated_env

pytestmark = [pytest.mark.live, pytest.mark.live_api]


def _urls() -> tuple[str, str]:
    warn_deprecated_env()
    api = live_api_url() or os.environ.get("LIVE_API_URL", "").rstrip("/")
    frontend = live_frontend_url() or os.environ.get("LIVE_FRONTEND_URL", "").rstrip(
        "/"
    )
    if not api or not frontend:
        pytest.skip("LIVE_API_URL and LIVE_FRONTEND_URL required for T8.3")
    return api, frontend


def test_t83_h4_cors_preflight_convert() -> None:
    """H4 — OPTIONS preflight for /api/v1/convert from frontend origin."""
    api, origin = _urls()
    with httpx.Client(timeout=45.0) as client:
        # Wake free-tier API if needed
        client.get(f"{api}/health")
        response = client.options(
            f"{api}/api/v1/convert",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )
    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected CORS allow-origin {origin!r} or '*', got {allow_origin!r}"
    )
    allow_methods = response.headers.get("access-control-allow-methods", "").upper()
    assert "POST" in allow_methods, allow_methods


def test_t83_h5_frontend_config_json_api_base() -> None:
    """H5 — staging /config.json api.baseUrl matches LIVE_API_URL."""
    api, frontend = _urls()
    expected = api.rstrip("/")
    with httpx.Client(timeout=45.0, follow_redirects=True) as client:
        response = client.get(f"{frontend}/config.json")
    assert response.status_code == 200, response.text[:300]
    cfg = response.json()
    actual = str(cfg.get("api", {}).get("baseUrl", "")).rstrip("/")
    assert actual == expected, (
        f"config.json api.baseUrl mismatch: expected {expected!r}, got {actual!r}"
    )
    # Sanity: parseable JSON with expected keys
    assert "api" in cfg
    assert json.dumps(cfg)


def test_t83_h5_frontend_index_reachable() -> None:
    """H5 companion — frontend index responds (static site up)."""
    _, frontend = _urls()
    with httpx.Client(timeout=45.0, follow_redirects=True) as client:
        response = client.get(frontend)
    assert response.status_code == 200, response.text[:200]
