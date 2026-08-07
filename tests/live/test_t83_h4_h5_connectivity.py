"""T8.3 - H4 CORS + H5 frontend config resolve on staging.

Spec: connectivity-gates H4-H5; docs/deploy.md live runbook;
docs/sessions/S008-general-tac-iwxxm-converter/reports/execution-plan.md T8.3.
"""

from __future__ import annotations

import json
import os

import httpx
import pytest
from tests.live_env import (
    expected_api_base_url,
    live_api_host_headers,
    live_api_url,
    live_frontend_fetch_base,
    live_frontend_host_headers,
    live_frontend_url,
    warn_deprecated_env,
)

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
    api_headers = live_api_host_headers()
    with httpx.Client(timeout=45.0) as client:
        # Wake free-tier API if needed
        client.get(f"{api}/health", headers=api_headers)
        response = client.options(
            f"{api}/api/v1/convert",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
                **api_headers,
            },
        )
    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected CORS allow-origin {origin!r} or '*', got {allow_origin!r}"
    )
    allow_methods = response.headers.get("access-control-allow-methods", "").upper()
    assert "POST" in allow_methods, allow_methods


def test_t83_h4_cors_preflight_mass_ingest() -> None:
    """H4 — OPTIONS preflight for /api/v1/ingest/mass (F33 / UJ-051)."""
    api, origin = _urls()
    api_headers = live_api_host_headers()
    with httpx.Client(timeout=45.0) as client:
        client.get(f"{api}/health", headers=api_headers)
        response = client.options(
            f"{api}/api/v1/ingest/mass",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
                **api_headers,
            },
        )
    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in (origin, "*"), (
        f"Expected CORS allow-origin {origin!r} or '*', got {allow_origin!r}"
    )
    allow_methods = response.headers.get("access-control-allow-methods", "").upper()
    assert "POST" in allow_methods or allow_methods == "*", allow_methods


def test_t83_h5_frontend_config_json_api_base() -> None:
    """H5 — staging /config.json api.baseUrl matches expected API base.

    F33 mass ingest uses the same ``api.baseUrl`` (no separate mass URL knob).
    """
    _api, _frontend = _urls()
    expected = expected_api_base_url()
    fetch_base = live_frontend_fetch_base()
    with httpx.Client(timeout=45.0, follow_redirects=True) as client:
        response = client.get(
            f"{fetch_base}/config.json",
            headers=live_frontend_host_headers(),
        )
    assert response.status_code == 200, response.text[:300]
    cfg = response.json()
    actual = str(cfg.get("api", {}).get("baseUrl", "")).rstrip("/")
    assert actual == expected, (
        f"config.json api.baseUrl mismatch: expected {expected!r}, got {actual!r}"
    )
    # Sanity: parseable JSON with expected keys; no separate mass-ingest URL.
    assert "api" in cfg
    assert "massIngestUrl" not in cfg.get("api", {})
    assert json.dumps(cfg)


def test_t83_h5_frontend_index_reachable() -> None:
    """H5 companion — frontend index responds (static site up)."""
    _urls()
    fetch_base = live_frontend_fetch_base()
    with httpx.Client(timeout=45.0, follow_redirects=True) as client:
        response = client.get(
            fetch_base,
            headers=live_frontend_host_headers(),
        )
    assert response.status_code == 200, response.text[:200]
