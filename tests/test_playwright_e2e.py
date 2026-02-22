"""Playwright E2E tests for auth and conversion flows."""
import os
import pathlib
import pytest
import requests


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

FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "https://metar-to-iwxxm-frontend-v4-web.onrender.com/")
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "https://metar-to-iwxxm-api.onrender.com")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
VALID_METAR = os.getenv(
    "E2E_VALID_METAR",
    "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
)
BAD_METAR = os.getenv("E2E_BAD_METAR", "THIS IS NOT A METAR")


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
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        pytest.skip("ADMIN_EMAIL/ADMIN_PASSWORD not configured")
    response = requests.post(
        f"{BACKEND_URL.replace('metar-to-iwxxm-api', 'metar-to-iwxxm-auth-v2')}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/json"},
        timeout=20,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "session" in payload
    assert payload["session"].get("access_token")


def test_conversion_endpoint_valid_tac():
    response = requests.post(
        f"{BACKEND_URL}/api/v1/convert",
        json={"metars": [VALID_METAR]},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("successful", 0) >= 1
    assert payload.get("results")


def test_conversion_endpoint_invalid_tac():
    response = requests.post(
        f"{BACKEND_URL}/api/v1/convert",
        json={"metars": [BAD_METAR]},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    assert response.status_code == 400, response.text
    payload = response.json()
    detail = payload.get("detail", {})
    assert detail.get("issues")


def test_conversion_endpoint_empty_payload_no_input():
    response = requests.post(
        f"{BACKEND_URL}/api/v1/convert",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    assert response.status_code in (400, 422), response.text
    payload = response.json()
    detail = payload.get("detail", {})
    issues = detail.get("issues") or []
    if response.status_code == 400:
        assert any(issue.get("code") == "NO_INPUT" for issue in issues)
