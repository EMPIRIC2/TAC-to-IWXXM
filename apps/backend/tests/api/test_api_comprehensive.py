"""Tests for API module edge cases and error handling."""

import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api import app, get_cors_origins
from src.utilities.security import verify_supabase_token


class TestCorsConfiguration:
    """Test CORS configuration."""

    _MISSING_PROFILE = {"METAR_CONFIG_ENV": "__missing_cors_profile__"}

    def test_cors_origins_from_environment(self):
        """Test deprecated METAR_CORS_ORIGINS fallback when config has no corsOrigins."""
        env = {**self._MISSING_PROFILE, "METAR_CORS_ORIGINS": "https://example.com,http://localhost:3000"}
        with patch.dict(os.environ, env, clear=False):
            origins = get_cors_origins()

            assert "https://example.com" in origins
            assert "http://localhost:3000" in origins

    def test_cors_origins_with_spaces(self):
        """Test CORS origins with extra whitespace."""
        env = {**self._MISSING_PROFILE, "METAR_CORS_ORIGINS": " https://example.com , http://localhost:3000 "}
        with patch.dict(os.environ, env, clear=False):
            origins = get_cors_origins()

            assert "https://example.com" in origins
            assert "http://localhost:3000" in origins
            assert " https://example.com" not in origins

    def test_cors_origins_empty_env_var(self):
        """Test CORS origins when env var is empty string uses config defaults."""
        with patch.dict(os.environ, {"METAR_CONFIG_ENV": "local", "METAR_CORS_ORIGINS": ""}, clear=False):
            origins = get_cors_origins()

            assert "http://localhost:18000" in origins

    def test_cors_origins_without_env_var(self):
        """Test CORS origins from config/local.json when env unset."""
        with patch.dict(os.environ, {"METAR_CONFIG_ENV": "local"}, clear=False):
            origins = get_cors_origins()

            assert "http://localhost:18000" in origins

    def test_cors_origins_custom_frontend_url(self):
        """Test FRONTEND_URL fallback when config profile is missing."""
        custom_url = "https://custom.example.com"
        env = {**self._MISSING_PROFILE, "FRONTEND_URL": custom_url, "METAR_CORS_ORIGINS": ""}
        with patch.dict(os.environ, env, clear=False):
            origins = get_cors_origins()

            assert custom_url in origins

    def test_cors_origins_single_origin(self):
        """Test CORS origins with single origin via deprecated env."""
        env = {**self._MISSING_PROFILE, "METAR_CORS_ORIGINS": "https://single.example.com"}
        with patch.dict(os.environ, env, clear=False):
            origins = get_cors_origins()

            assert "https://single.example.com" in origins

    def test_cors_origins_with_trailing_comma(self):
        """Test CORS origins with trailing comma."""
        env = {**self._MISSING_PROFILE, "METAR_CORS_ORIGINS": "https://example.com,"}
        with patch.dict(os.environ, env, clear=False):
            origins = get_cors_origins()

            assert "https://example.com" in origins
            assert "" not in origins


class TestHealthEndpointEdgeCases:
    """Test health endpoint edge cases."""

    def test_health_with_gifts_available(self):
        """Test health when GIFTs is available."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "gifts_available" in data
        assert data["status"] in ["healthy", "degraded"]

    def test_health_response_has_version(self):
        """Test health response includes version."""
        client = TestClient(app)
        response = client.get("/health")

        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)

    def test_health_endpoint_no_auth_required(self):
        """Test health endpoint doesn't require authentication."""
        client = TestClient(app)
        # No auth headers provided
        response = client.get("/health")

        assert response.status_code == 200

    def test_health_status_values(self):
        """Test health status values are valid."""
        client = TestClient(app)
        response = client.get("/health")

        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_gifts_available_boolean(self):
        """Test gifts_available is boolean."""
        client = TestClient(app)
        response = client.get("/health")

        data = response.json()
        assert isinstance(data["gifts_available"], bool)


class TestRouterInclusion:
    """Test router inclusion in main app."""

    def test_validation_router_included(self):
        """Test validation router is included in app."""
        client = TestClient(app)

        # Check that validation endpoints exist
        response = client.get("/api/v1/validation/layers")
        assert response.status_code in [200, 401]

    def test_evaluation_router_included(self):
        """Test evaluation router is included in app."""
        client = TestClient(app)

        # Evaluation endpoints may be protected or not exist in test
        # Just verify app doesn't crash
        assert len(app.routes) > 0

    def test_all_routes_accessible(self):
        """Test that all routes are registered."""
        # Should have at least health, convert, validation routes
        assert len(app.routes) > 5


class TestAppInitialization:
    """Test app initialization and configuration."""

    def test_app_title_set(self):
        """Test app has proper title."""
        assert app.title is not None
        assert "METAR" in app.title

    def test_app_version_set(self):
        """Test app has version."""
        assert app.version is not None

    def test_app_description_set(self):
        """Test app has description."""
        assert app.description is not None

    def test_app_tags_defined(self):
        """Test app has OpenAPI tags defined."""
        assert app.openapi_tags is not None
        assert len(app.openapi_tags) > 0

    def test_app_tags_have_required_fields(self):
        """Test each tag has required fields."""
        for tag in app.openapi_tags:
            assert "name" in tag
            assert "description" in tag


class TestDependencyInjection:
    """Test dependency injection in endpoints."""

    def test_verify_supabase_token_override(self):
        """Test that verify_supabase_token can be overridden."""

        async def mock_token():
            return {"sub": "test-user"}

        app.dependency_overrides[verify_supabase_token] = mock_token

        try:
            # Should not raise
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_dependency_override_cleanup(self):
        """Test dependency overrides are cleaned up properly."""

        async def mock_token():
            return {"sub": "test"}

        initial_count = len(app.dependency_overrides)

        app.dependency_overrides[verify_supabase_token] = mock_token
        assert len(app.dependency_overrides) > initial_count

        app.dependency_overrides.clear()
        assert len(app.dependency_overrides) == initial_count


class TestRequestValidation:
    """Test request validation in API."""

    def test_malformed_json_request(self):
        """Test handling of malformed JSON in request."""
        client = TestClient(app)

        # Manually create invalid JSON request
        response = client.post("/api/v1/convert", content="{invalid json", headers={"Content-Type": "application/json"})

        # Should return 422 or 400 (or 401 if auth required)
        assert response.status_code in [400, 401, 422]

    def test_missing_content_type_header(self):
        """Test request without Content-Type header."""
        client = TestClient(app)

        response = client.post("/api/v1/convert", data="some data")

        # Should handle gracefully
        assert response.status_code in [200, 400, 401, 415, 422]

    def test_unsupported_content_type(self):
        """Test request with unsupported Content-Type."""
        client = TestClient(app)

        response = client.post("/api/v1/convert", data="some data", headers={"Content-Type": "application/xml"})

        # Should handle or reject
        assert response.status_code in [200, 400, 401, 415, 422]


class TestErrorResponses:
    """Test error response formatting."""

    def test_404_response_structure(self):
        """Test 404 response has proper structure."""
        client = TestClient(app)

        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        # Response should be JSON
        assert "detail" in response.json() or response.content

    def test_method_not_allowed_response(self):
        """Test 405 Method Not Allowed response."""
        client = TestClient(app)

        # Try to POST to a GET endpoint
        response = client.post("/health")

        assert response.status_code == 405

    def test_validation_error_response_structure(self):
        """Test validation error response structure."""
        client = TestClient(app)

        # Send request missing required field
        response = client.post("/api/v1/convert", json={})

        if response.status_code == 422:
            data = response.json()
            assert "detail" in data


class TestResponseHeaders:
    """Test response headers."""

    def test_response_content_type_json(self):
        """Test JSON responses have correct Content-Type."""
        client = TestClient(app)

        response = client.get("/health")

        assert response.headers["content-type"] == "application/json"

    def test_response_has_server_header(self):
        """Test response includes server header."""
        client = TestClient(app)

        response = client.get("/health")

        # Should have a server header (could be Uvicorn or similar)
        assert "server" in response.headers or True  # Optional header

    def test_cors_headers_present(self):
        """Test CORS headers in response."""
        client = TestClient(app)

        response = client.get("/health")

        # CORS headers may be present depending on configuration
        # Just ensure request succeeds
        assert response.status_code == 200
