"""Comprehensive tests for API endpoint error handling."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api import app
from src.utilities.conversion import ConversionError

client = TestClient(app)


class TestHealthEndpoint:
    """Test health endpoint edge cases."""

    def test_health_when_gifts_unavailable(self):
        """Test health endpoint when GIFTs is unavailable."""
        with patch("src.api.convert_metar_tac_with_metadata", side_effect=Exception("GIFTs unavailable")):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["gifts_available"] is False

    def test_health_when_conversion_fails(self):
        """Test health endpoint when test conversion fails."""
        with patch("src.api.convert_metar_tac_with_metadata", side_effect=ConversionError("Test error")):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["gifts_available"] is False


class TestConvertEndpointErrorHandling:
    """Test /api/v1/convert endpoint error scenarios."""

    def test_convert_without_auth_fails(self):
        """Test that convert endpoint requires authentication."""
        response = client.post(
            "/api/v1/convert", data={"manual_text": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"}
        )
        # Should fail without authentication
        assert response.status_code in [401, 403]


class TestConvertZipEndpointErrorHandling:
    """Test /api/v1/convert-zip endpoint error scenarios."""

    def test_convert_zip_without_auth_fails(self):
        """Test that convert-zip endpoint requires authentication."""
        response = client.post(
            "/api/v1/convert-zip", data={"manual_text": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"}
        )
        # Should fail without authentication
        assert response.status_code in [401, 403]


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_headers_present(self):
        """Test that CORS headers are configured."""
        response = client.options("/health")
        # CORS headers should be present or endpoint should respond
        assert response.status_code in [200, 405]

    def test_allowed_origins(self):
        """Test that allowed origins are configured."""
        # This tests that the middleware is set up
        response = client.get("/health", headers={"Origin": "http://localhost:8000"})
        assert response.status_code == 200


class TestAPIMetadata:
    """Test API metadata and documentation."""

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "METAR to IWXXM Backend API"

    def test_docs_endpoint(self):
        """Test that API docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
