"""T7.3 - TC-EV031-* live probes on provisional DOKS topology.

Spec: docs/test-plan.md TC-EV031-003/004; TC-F30-004 deepen; D-S038-t63-waive.
Requires: source scripts/deploy/doks_provisional_live_env.sh (or make target).
"""

from __future__ import annotations

import os

import httpx
import pytest
from tests.live_env import (
    doks_provisional,
    live_api_host_headers,
    live_api_url,
    warn_deprecated_env,
)

pytestmark = [pytest.mark.live, pytest.mark.live_api]


def _require_provisional_api() -> str:
    warn_deprecated_env()
    api = live_api_url()
    if not api:
        pytest.skip("LIVE_API_URL required for TC-EV031 DOKS topology")
    if not doks_provisional():
        pytest.skip(
            "PLAYWRIGHT_DOKS_PROVISIONAL=1 or DOKS_PROVISIONAL=1 required "
            "(make test-live-topology-doks-provisional)"
        )
    return api


def _e2e_credentials() -> tuple[str, str]:
    email = (
        os.environ.get("E2E_USER_EMAIL", "").strip()
        or os.environ.get("ADMIN_EMAIL", "").strip()
    )
    password = (
        os.environ.get("E2E_USER_PASSWORD", "").strip()
        or os.environ.get("ADMIN_PASSWORD", "").strip()
    )
    if not email or not password:
        pytest.skip("E2E_USER_* or ADMIN_* credentials required for login CRUD")
    return email, password


def test_tc_ev031_003_public_convert_without_jwt_on_doks() -> None:
    """TC-EV031-003 - convert stays JWT-free on provisional DOKS."""
    api = _require_provisional_api()
    headers = {
        "Content-Type": "application/json",
        **live_api_host_headers(),
    }
    with httpx.Client(timeout=45.0) as client:
        health = client.get(f"{api}/health", headers=live_api_host_headers())
        assert health.status_code == 200, health.text[:300]
        convert = client.post(
            f"{api}/api/v1/convert",
            headers=headers,
            json={"metars": ["METAR KJFK 031951Z 18010KT 10SM FEW050 22/12 A3012"]},
        )
    assert convert.status_code == 200, convert.text[:400]


def test_tc_ev031_003_work_sessions_require_jwt_on_doks() -> None:
    """TC-EV031-003 companion - work-sessions stay JWT-gated on DOKS."""
    api = _require_provisional_api()
    with httpx.Client(timeout=45.0) as client:
        response = client.get(
            f"{api}/api/v1/work-sessions",
            headers=live_api_host_headers(),
        )
    assert response.status_code in (401, 403), response.text[:300]


def test_tc_ev031_004_login_session_list_on_doks() -> None:
    """TC-EV031-004 - login + list work-sessions against DO Postgres on DOKS."""
    api = _require_provisional_api()
    email, password = _e2e_credentials()
    host_headers = live_api_host_headers()
    with httpx.Client(timeout=45.0) as client:
        login = client.post(
            f"{api}/auth/login",
            headers={**host_headers, "Content-Type": "application/json"},
            json={"email": email, "password": password},
        )
        assert login.status_code == 200, login.text[:400]
        body = login.json()
        token = body.get("access_token") or body.get("accessToken")
        if not token and isinstance(body.get("session"), dict):
            token = body["session"].get("access_token")
        assert token, f"login response missing access_token: {sorted(body.keys())}"

        sessions = client.get(
            f"{api}/api/v1/work-sessions",
            headers={**host_headers, "Authorization": f"Bearer {token}"},
        )
    assert sessions.status_code == 200, sessions.text[:400]
    payload = sessions.json()
    assert "items" in payload or isinstance(payload, list)
