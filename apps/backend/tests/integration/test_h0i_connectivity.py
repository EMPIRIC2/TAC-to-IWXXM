"""H0i connectivity gate — in-process cross-package integration (test-plan.md §H0i).

Verifies apps/backend wires packages/auth, packages/gifts, and CORS on one host
without a separate auth microservice. No docker-compose or live Supabase required.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.utilities.security import verify_supabase_token

pytestmark = [pytest.mark.integration, pytest.mark.h0i]

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
BROWSER_ORIGIN = "http://localhost:18000"


@pytest.fixture
def h0i_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Authenticated in-process client with auth enforcement enabled."""
    monkeypatch.setenv("DISABLE_AUTH", "false")
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

    from src.utilities import security as sec

    monkeypatch.setattr(sec, "DISABLE_AUTH", False)

    async def _auth_user() -> dict[str, str]:
        return {"sub": "h0i-user", "aud": "test"}

    app.dependency_overrides[verify_supabase_token] = _auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestH0iCorsPreflight:
    """Browser CORS preflight against merged API host."""

    def test_options_convert_allows_post(self, h0i_client: TestClient) -> None:
        response = h0i_client.options(
            "/api/v1/convert",
            headers={
                "Origin": BROWSER_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods.upper()

    def test_options_auth_login_allows_post(self, h0i_client: TestClient) -> None:
        response = h0i_client.options(
            "/auth/login",
            headers={
                "Origin": BROWSER_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods.upper()


class TestH0iAuthConversionWiring:
    """Auth package + GIFTs conversion on single backend deployable."""

    def test_convert_requires_auth_when_enforced(self, h0i_client: TestClient) -> None:
        app.dependency_overrides.clear()
        try:
            response = TestClient(app).post(
                "/api/v1/convert",
                data={"manual_text": SAMPLE_METAR},
            )
        finally:

            async def _auth_user() -> dict[str, str]:
                return {"sub": "h0i-user", "aud": "test"}

            app.dependency_overrides[verify_supabase_token] = _auth_user

        assert response.status_code == 401

    def test_convert_returns_iwxxm_when_authenticated(self, h0i_client: TestClient) -> None:
        response = h0i_client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["successful"] >= 1
        assert "<iwxxm" in payload["results"][0]["content"].lower()

    def test_auth_login_route_on_same_host(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from auth.api_supabase import get_supabase_proxy

        mock_proxy = MagicMock()
        mock_proxy.sign_in.return_value = {
            "user": {"id": "h0i-user", "email": "h0i@example.test", "metadata": {}},
            "session": {
                "access_token": "h0i-token",
                "refresh_token": "h0i-refresh",
                "expires_at": 4_102_444_800,
            },
        }

        def _override() -> MagicMock:
            return mock_proxy

        app.dependency_overrides[get_supabase_proxy] = _override
        try:
            client = TestClient(app)
            response = client.post(
                "/auth/login",
                json={"email": "h0i@example.test", "password": "SecretPass1!"},
            )
        finally:
            app.dependency_overrides.pop(get_supabase_proxy, None)

        assert response.status_code == 200
        assert response.json()["session"]["access_token"] == "h0i-token"


class TestH0iPublicEndpoints:
    """Health and version discovery without auth."""

    def test_health_endpoint(self, h0i_client: TestClient) -> None:
        response = h0i_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_versions_endpoint(self, h0i_client: TestClient) -> None:
        response = h0i_client.get("/api/v1/versions")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body.get("supported_versions"), list)
        assert len(body["supported_versions"]) >= 1
