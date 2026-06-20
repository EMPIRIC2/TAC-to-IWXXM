"""Integration tests and E2E tests at root level."""
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure backend src is importable
REPO_ROOT = pathlib.Path(__file__).resolve().parents[0]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.src.api import app
from backend.src.utilities.security import verify_supabase_token

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
SAMPLE_METAR_2 = "METAR KLAX 231753Z 25008KT 10SM FEW020 18/12 A2992"


@pytest.fixture
def client():
    """Create test client with mocked authentication."""
    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}
    
    app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestIntegrationConversion:
    """Integration tests for conversion endpoints."""

    def test_end_to_end_single_metar(self, client):
        """E2E: Convert single METAR from input to output."""
        # 1. Check health
        health_r = client.get("/health")
        assert health_r.status_code == 200
        assert health_r.json()["status"] in {"healthy", "degraded"}
        
        # 2. Convert METAR
        convert_r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        assert convert_r.status_code == 200
        data = convert_r.json()
        assert data["successful"] >= 1
        assert len(data["results"]) >= 1
        assert "<iwxxm:METAR" in data["results"][0]["content"]

    def test_end_to_end_batch_conversion_zip(self, client):
        """E2E: Batch convert multiple METARs to ZIP."""
        files = [
            ("files", ("m1.tac", SAMPLE_METAR, "text/plain")),
            ("files", ("m2.tac", SAMPLE_METAR_2, "text/plain")),
        ]
        r = client.post("/api/v1/convert-zip", files=files)
        assert r.status_code == 200
        assert "application/zip" in r.headers.get("content-type", "")

    def test_integration_multiple_endpoints(self, client):
        """Test integration between different API endpoints."""
        # Convert single
        r1 = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        assert r1.status_code == 200
        
        # Convert to ZIP
        r2 = client.post("/api/v1/convert-zip", data={"manual_text": SAMPLE_METAR})
        assert r2.status_code == 200


class TestAPIIntegration:
    """API integration tests with backend services."""

    def test_conversion_service_through_api(self, client):
        """Test that conversion service works through API layer."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        assert r.status_code == 200
        data = r.json()
        
        # Verify response structure
        assert "results" in data
        assert "errors" in data
        assert "total_processed" in data
        assert "successful" in data
        assert "failed" in data

    def test_schema_compliance_in_response(self, client):
        """Test that API responses follow schema."""
        r = client.post("/api/v1/convert", data={"manual_text": SAMPLE_METAR})
        data = r.json()
        
        for result in data["results"]:
            assert "name" in result
            assert "content" in result
            assert "source" in result or result["source"] is None
            assert "size_bytes" in result or result["size_bytes"] is None

    def test_health_check_integration(self, client):
        """Test health check with actual conversion test."""
        r = client.get("/health")
        assert r.status_code == 200
        health_data = r.json()
        
        # Health check should test GIFTs availability
        assert "status" in health_data
        assert "version" in health_data
        assert isinstance(health_data["gifts_available"], bool)


class TestErrorHandling:
    """Test error handling across API."""

    def test_error_response_format(self, client):
        """Test that errors follow expected format."""
        files = [
            ("files", ("empty.tac", "", "text/plain")),
        ]
        r = client.post("/api/v1/convert", files=files)
        assert r.status_code == 400
        data = r.json()
        
        assert "detail" in data
        assert "message" in data["detail"]
        assert "errors" in data["detail"]

    def test_graceful_error_handling(self, client):
        """Test graceful error handling in conversion."""
        # Ensure no crashes with edge cases
        r = client.post("/api/v1/convert", data={"manual_text": "  "})
        # Should either succeed or fail gracefully
        assert r.status_code in [200, 400]
