"""Connectivity tests for a running local auth service.

These tests are integration-style smoke checks and are skipped when the
service is not reachable at localhost:8002.
"""

import pytest
import requests

AUTH_URL = "http://localhost:8002"


def _service_available() -> bool:
    try:
        response = requests.get(f"{AUTH_URL}/health", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


pytestmark = pytest.mark.skipif(
    not _service_available(),
    reason="Auth service is not running on localhost:8002",
)


def test_health_endpoint_reachable() -> None:
    response = requests.get(f"{AUTH_URL}/health", timeout=5)
    assert response.status_code == 200


def test_login_options_preflight() -> None:
    response = requests.options(
        f"{AUTH_URL}/auth/login",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
        timeout=5,
    )
    assert response.status_code in (200, 204)


def test_login_with_invalid_credentials() -> None:
    response = requests.post(
        f"{AUTH_URL}/auth/login",
        json={"email": "test@test.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    assert response.status_code >= 400
