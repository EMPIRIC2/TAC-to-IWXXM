"""H3 live smoke - convert / lint-tac / convert-bulletin (T7.2).

Uses LIVE_API_URL (default staging API). Skips when URL unset or auth fails.
"""

from __future__ import annotations

import os

import httpx
import pytest

pytestmark = [pytest.mark.live, pytest.mark.live_api]

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="


def _live_api_base() -> str | None:
    return os.environ.get("LIVE_API_URL") or os.environ.get("STAGING_API_URL")


@pytest.fixture(scope="module")
def live_api() -> str:
    base = _live_api_base()
    if not base:
        pytest.skip("LIVE_API_URL / STAGING_API_URL not set")
    return base.rstrip("/")


@pytest.fixture(scope="module")
def live_headers(live_api: str) -> dict[str, str]:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    headers: dict[str, str] = {}
    if not email or not password:
        return headers
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{live_api}/auth/login",
            json={"email": email, "password": password},
        )
        if resp.status_code != 200:
            pytest.skip(f"live login failed: {resp.status_code}")
        data = resp.json()
        token = (
            data.get("access_token")
            or data.get("token")
            or (data.get("session") or {}).get("access_token")
        )
        if not token:
            pytest.skip("live login response missing access_token")
        headers["Authorization"] = f"Bearer {token}"
    return headers


def test_h3_health(live_api: str) -> None:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(f"{live_api}/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") in {"healthy", "ok", "UP", "up"} or "status" in body


def test_h3_lint_tac(live_api: str, live_headers: dict[str, str]) -> None:
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{live_api}/api/v1/lint-tac",
            headers=live_headers,
            files={
                "manual_text": (None, SAMPLE_METAR),
                "product": (None, "METAR"),
            },
        )
    if resp.status_code in {401, 403} and "Authorization" not in live_headers:
        pytest.skip("lint-tac requires auth")
    if resp.status_code == 404:
        pytest.skip("lint-tac not deployed on live yet")
    assert resp.status_code == 200, resp.text[:400]
    assert "ok" in resp.json()


def test_h3_convert(live_api: str, live_headers: dict[str, str]) -> None:
    with httpx.Client(timeout=90.0) as client:
        resp = client.post(
            f"{live_api}/api/v1/convert",
            headers=live_headers,
            data={
                "manual_text": SAMPLE_METAR,
                "product": "METAR",
                "iwxxm_version": "2025-2",
                "lint": "false",
            },
        )
    if resp.status_code in {401, 403} and "Authorization" not in live_headers:
        pytest.skip("convert requires auth")
    assert resp.status_code == 200, resp.text[:500]
    body = resp.json()
    assert body.get("successful", body.get("total_processed", 0)) >= 1 or body.get(
        "results"
    )
