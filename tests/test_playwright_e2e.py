"""Legacy Playwright/API smoke tests against live Render (TC-LIVE-005)."""

from __future__ import annotations

import os
import pathlib
import warnings

import pytest
import requests
from tests.live_env import live_api_url, live_frontend_url, warn_deprecated_env


def _load_env_file() -> None:
    env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()
warn_deprecated_env()

FRONTEND_URL = live_frontend_url() or "http://app.doks.placeholder.metar-iwxxm.local"
BACKEND_URL = live_api_url() or "http://api.doks.placeholder.metar-iwxxm.local"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
VALID_METAR = os.getenv(
    "E2E_VALID_METAR",
    "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
)
BAD_METAR = os.getenv("E2E_BAD_METAR", "THIS IS NOT A METAR")

if os.getenv("E2E_BACKEND_URL") and not os.getenv("LIVE_API_URL"):
    warnings.warn(
        "E2E_BACKEND_URL is deprecated; use LIVE_API_URL",
        DeprecationWarning,
        stacklevel=1,
    )
if os.getenv("E2E_FRONTEND_URL") and not os.getenv("LIVE_FRONTEND_URL"):
    warnings.warn(
        "E2E_FRONTEND_URL is deprecated; use LIVE_FRONTEND_URL",
        DeprecationWarning,
        stacklevel=1,
    )


def _live_auth_headers() -> dict[str, str]:
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        pytest.skip("ADMIN_EMAIL/ADMIN_PASSWORD not configured")
    response = requests.post(
        f"{BACKEND_URL.rstrip('/')}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    token = payload.get("session", {}).get("access_token") or payload.get(
        "access_token"
    )
    assert token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def playwright_page():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as browser_context:
        browser = browser_context.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            yield page
        finally:
            browser.close()


def test_frontend_login_page_renders(playwright_page):
    page = playwright_page
    page.goto(FRONTEND_URL, wait_until="domcontentloaded")
    assert page.get_by_role("heading", name="METAR Converter").is_visible()
    assert page.get_by_role("button", name="Authenticate").is_visible()


def test_frontend_login_validation_messages(playwright_page):
    page = playwright_page
    page.goto(FRONTEND_URL, wait_until="domcontentloaded")
    page.get_by_role("button", name="Authenticate").click()
    assert page.get_by_text("Email or username is required").is_visible()
    assert page.get_by_text("Password is required").is_visible()


def test_auth_login_api_with_env_credentials():
    headers = _live_auth_headers()
    assert headers["Authorization"].startswith("Bearer ")


def test_conversion_endpoint_valid_tac():
    headers = _live_auth_headers()
    response = requests.post(
        f"{BACKEND_URL.rstrip('/')}/api/v1/convert",
        json={"metars": [VALID_METAR], "version": "2025-2"},
        headers=headers,
        timeout=30,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("successful", 0) >= 1
    assert payload.get("results")


def test_conversion_endpoint_invalid_tac():
    headers = _live_auth_headers()
    response = requests.post(
        f"{BACKEND_URL.rstrip('/')}/api/v1/convert",
        json={"metars": [BAD_METAR]},
        headers=headers,
        timeout=30,
    )
    assert response.status_code in (200, 400), response.text
    if response.status_code == 200:
        payload = response.json()
        assert payload.get("failed", 0) >= 1 or payload.get("errors")


def test_conversion_endpoint_empty_payload_no_input():
    headers = _live_auth_headers()
    response = requests.post(
        f"{BACKEND_URL.rstrip('/')}/api/v1/convert",
        json={},
        headers=headers,
        timeout=30,
    )
    assert response.status_code in (400, 422), response.text
