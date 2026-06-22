"""Shared helpers for live Render API tests (H3 integration)."""

from __future__ import annotations

import os
import time

import httpx
import pytest
from tests.live_env import live_api_url

DEFAULT_LIVE_API = "https://metar-to-iwxxm-api.onrender.com"
WAKE_ATTEMPTS = 3
WAKE_WAIT_SECONDS = 30


def live_api_base() -> str:
    """Resolved API base URL with Makefile-aligned default."""
    return (live_api_url() or DEFAULT_LIVE_API).rstrip("/")


def wake_live_api(base_url: str | None = None) -> str:
    """Retry health check to handle Render cold-start spin-up."""
    url = (base_url or live_api_base()).rstrip("/")
    last_error: Exception | None = None
    for attempt in range(1, WAKE_ATTEMPTS + 1):
        try:
            response = httpx.get(f"{url}/health", timeout=30.0, follow_redirects=True)
            if response.status_code == 200:
                return url
            last_error = RuntimeError(f"health returned {response.status_code}")
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            last_error = exc
        if attempt < WAKE_ATTEMPTS:
            time.sleep(WAKE_WAIT_SECONDS)
    pytest.skip(
        f"Live API not reachable at {url} after {WAKE_ATTEMPTS} attempts: {last_error}"
    )
    return url  # unreachable — satisfies type checker after skip


def login_with_backoff(base_url: str, email: str, password: str) -> str:
    """Obtain bearer token via POST /auth/login with 429 backoff."""
    last_response: httpx.Response | None = None
    for attempt in range(1, WAKE_ATTEMPTS + 1):
        response = httpx.post(
            f"{base_url}/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )
        last_response = response
        if response.status_code == 200:
            payload = response.json()
            token = payload.get("session", {}).get("access_token") or payload.get(
                "access_token"
            )
            if token:
                return str(token)
            raise RuntimeError("Login succeeded but no access_token in response")
        if response.status_code == 429 and attempt < WAKE_ATTEMPTS:
            time.sleep(WAKE_WAIT_SECONDS * attempt)
            continue
        break
    detail = last_response.text if last_response is not None else "no response"
    pytest.skip(f"Could not obtain live JWT from {base_url}/auth/login: {detail}")
    return ""  # unreachable


def obtain_live_api_token() -> str:
    """Session-scoped token helper for conftest fixtures."""
    base_url = wake_live_api()
    email = os.environ.get("ADMIN_EMAIL", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "").strip()
    if not email or not password:
        pytest.skip(
            "ADMIN_EMAIL and ADMIN_PASSWORD required for authenticated live API tests"
        )
    return login_with_backoff(base_url, email, password)
