"""H0i connectivity gate — in-process cross-package integration (test-plan.md §H0i).

Verifies apps/backend wires packages/tac2iwxxm and CORS on one host with
merged Auth (F31 / ADR-033) and public convert (F21 Amended). No docker-compose
required.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.api import app

pytestmark = [pytest.mark.integration, pytest.mark.h0i]

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
BROWSER_ORIGIN = "http://localhost:18000"


@pytest.fixture
def h0i_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Public in-process client (operator Auth removed)."""
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("METAR_CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENABLE_DEV_CORS_RELAXATION", "true")

    app.dependency_overrides.clear()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestH0iCorsPreflight:
    """Browser CORS preflight against public API host."""

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

    def test_options_auth_login_present(self, h0i_client: TestClient) -> None:
        """F31: /auth/login is mounted on the API host (no separate auth service)."""
        response = h0i_client.options(
            "/auth/login",
            headers={
                "Origin": BROWSER_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code in {200, 405}
        post = h0i_client.post(
            "/auth/login",
            json={"email": "h0i@example.test", "password": "x"},
        )
        # Mounted but may 503 without SUPABASE_URL / publishable key in unit env.
        assert post.status_code != 404

    def test_options_work_sessions_jwt_gated(self, h0i_client: TestClient) -> None:
        """F31: work-sessions mounted; unauthenticated GET is 401/403 (not public 200)."""
        for method in ("PATCH", "DELETE"):
            response = h0i_client.options(
                "/api/v1/work-sessions",
                headers={
                    "Origin": BROWSER_ORIGIN,
                    "Access-Control-Request-Method": method,
                },
            )
            assert response.status_code in {200, 404, 405}
        assert h0i_client.get("/api/v1/work-sessions").status_code in {401, 403}

    @pytest.mark.parametrize(
        "path",
        ["/api/v1/lint-tac", "/api/v1/decode-tac"],
    )
    def test_options_f7_live_assist_allows_post(self, h0i_client: TestClient, path: str) -> None:
        """F7 UI connection points — browser preflight for live lint/decode."""
        response = h0i_client.options(
            path,
            headers={
                "Origin": BROWSER_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.status_code == 200
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods.upper()


class TestH0iPublicConversionWiring:
    """tac2iwxxm conversion on single backend deployable without Auth."""

    def test_convert_succeeds_without_authorization(self, h0i_client: TestClient) -> None:
        response = h0i_client.post(
            "/api/v1/convert",
            data={"manual_text": SAMPLE_METAR},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["successful"] >= 1
        assert "<iwxxm" in payload["results"][0]["content"].lower()

    def test_auth_login_route_mounted(self, h0i_client: TestClient) -> None:
        response = h0i_client.post(
            "/auth/login",
            json={"email": "h0i@example.test", "password": "SecretPass1!"},
        )
        assert response.status_code != 404


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
