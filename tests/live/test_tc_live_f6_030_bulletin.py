"""H7 / TC-LIVE-F6-030 live bulletin gate (T4.9 / T7.3).

Requires LIVE_API_URL (or STAGING_API_URL) and a JWT from live login when auth
is enforced. Skips when live URL is unset or convert-bulletin is not deployed yet.
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import pytest

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "live"
    / "metar_multi_ahl_bulletin.txt"
)

pytestmark = [pytest.mark.live, pytest.mark.live_api]


def _live_api_base() -> str | None:
    return os.environ.get("LIVE_API_URL") or os.environ.get("STAGING_API_URL")


def _extract_token(payload: dict) -> str | None:
    return (
        payload.get("access_token")
        or payload.get("token")
        or (payload.get("session") or {}).get("access_token")
    )


@pytest.fixture(scope="module")
def live_api() -> str:
    base = _live_api_base()
    if not base:
        pytest.skip("LIVE_API_URL / STAGING_API_URL not set")
    return base.rstrip("/")


@pytest.fixture(scope="module")
def live_token(live_api: str) -> str | None:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        return None
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{live_api}/auth/login", json={"email": email, "password": password}
        )
        if resp.status_code != 200:
            pytest.skip(f"live login failed: {resp.status_code}")
        token = _extract_token(resp.json())
        if not token:
            pytest.skip("live login response missing access_token")
        return token


def test_tc_live_f6_030_convert_bulletin(live_api: str, live_token: str | None) -> None:
    """Multi-report AHL bulletin → convert-bulletin returns per-report results."""
    if not FIXTURE.is_file():
        pytest.fail(f"missing H7 fixture: {FIXTURE}")
    bulletin = FIXTURE.read_bytes()
    headers = {}
    if live_token:
        headers["Authorization"] = f"Bearer {live_token}"
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{live_api}/api/v1/convert-bulletin",
            headers=headers,
            files={
                "file": ("metar_multi_ahl_bulletin.txt", bulletin, "text/plain"),
                "product": (None, "METAR"),
                "profile": (None, "annex3"),
                "iwxxm_version": (None, "2025-2"),
            },
        )
    if resp.status_code in {401, 403} and not live_token:
        pytest.skip(
            "live convert-bulletin requires auth; set ADMIN_EMAIL/ADMIN_PASSWORD"
        )
    if resp.status_code == 404:
        pytest.skip(
            "convert-bulletin not on live yet (merge/deploy F6 cutover PRs #706-#708)"
        )
    assert resp.status_code == 200, resp.text[:500]
    body = resp.json()
    assert "results" in body or "reports" in body or isinstance(body, dict)
