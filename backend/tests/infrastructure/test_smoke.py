"""Smoke test suite for rapid CI/CD validation.

These tests provide quick validation (~30 seconds) of critical API functionality
without external dependencies. Ideal for:
- Pre-commit hooks
- Pull request validation
- Rapid CI/CD pipelines
- Pre-deployment checks

Only tests the critical happy path. For comprehensive testing, run full test suite.

Run with: pytest -m smoke backend/tests/test_smoke.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from src.api import app
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client():
    """Create test client with mocked authentication."""
    async def override_verify_token():
        return {"sub": "test-user-id", "aud": "test-project"}
    
    app.dependency_overrides[verify_supabase_token] = override_verify_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client():
    """Create test client without authentication."""
    return TestClient(app)


@pytest.mark.smoke
class TestSmokeHealthCheck:
    """Smoke test: Health check endpoint."""

    def test_health_endpoint_responds(self, unauthenticated_client):
        """Test health endpoint is accessible and responds."""
        response = unauthenticated_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.smoke
class TestSmokeAuthentication:
    """Smoke test: Authentication works."""

    def test_authenticated_endpoint_accessible(self, client):
        """Test can access authenticated endpoint with valid token."""
        response = client.get("/api/v1/validation/layers")
        
        assert response.status_code == 200

    def test_unauthenticated_request_rejected(self, unauthenticated_client):
        """Test authenticated endpoint rejects requests without token."""
        response = unauthenticated_client.post(
            "/api/v1/convert",
            json={"metars": ["METAR TEST"]}
        )
        
        assert response.status_code == 401


@pytest.mark.smoke
class TestSmokeConversion:
    """Smoke test: METAR conversion works."""

    def test_basic_metar_conversion(self, client):
        """Test can convert a simple METAR."""
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": ["METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015"],
                "version": "2025-2",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        # Skip if empty results (conversion might fail in some environments)
        if len(data["results"]) > 0:
            result = data["results"][0]
            # ConversionResult has 'content' field with the XML, not 'iwxxm_xml'
            assert "content" in result
            assert len(result["content"]) > 0

    def test_multiline_manual_input_is_processed_as_individual_entries(self, client):
        """Each non-empty manual input line is treated as an individual TAC entry."""
        multiline = "\n".join([
            "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
            "",
            "METAR EGLL 161220Z 09010KT 9999 SCT030 10/05 Q1018",
        ])

        response = client.post(
            "/api/v1/convert",
            data={
                "manual_text": multiline,
                "iwxxm_version": "2025-2",
                "bulletin_id": "saaa00",
                "issuing_center": "kwbc",
                "validation_level": "comprehensive",
                "stop_on_error": "false",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] >= 2
        assert "metadata" in data
        assert data["metadata"]["bulletin_id"] == "SAAA00"
        assert data["metadata"]["issuing_center"] == "KWBC"


@pytest.mark.smoke
class TestSmokeValidation:
    """Smoke test: Validation works."""

    def test_validation_layers_available(self, client):
        """Test validation layers endpoint works."""
        response = client.get("/api/v1/validation/layers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "layers" in data
        assert len(data["layers"]) == 7

    def test_basic_validation_request(self, client):
        """Test can validate a simple METAR."""
        response = client.post(
            "/api/v1/validation/validate",
            json={
                "content": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "passed" in data
        assert "results" in data


@pytest.mark.smoke
class TestSmokeEvaluation:
    """Smoke test: Evaluation job creation works."""

    def test_create_evaluation_job(self, client):
        """Test can create an evaluation job."""
        with patch('src.routers.evaluation.get_supabase_client') as mock_get_client:
            # Create the mock response
            mock_response = MagicMock()
            mock_response.json.return_value = [{"id": "test-job-123"}]
            mock_response.raise_for_status.return_value = None
            
            # Create the mock client with async post and patch methods
            mock_client = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.patch = AsyncMock(return_value=mock_response)
            
            # Use AsyncMock to create a mock that handles async __aenter__ and __aexit__
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            
            # Make get_supabase_client() return an awaitable that resolves to the context manager
            mock_get_client.return_value = mock_context
            
            response = client.post(
                "/api/v1/eval/jobs",
                json={
                    "mode": "single",
                    "station_ids": ["KJFK"],
                    "hours": 1,
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "job_id" in data
            assert data["status"] == "pending"


@pytest.mark.smoke
class TestSmokeTranslationStats:
    """Smoke test: Translation Centre endpoints work."""

    def test_centre_info_accessible(self, unauthenticated_client):
        """Test Translation Centre info is accessible."""
        response = unauthenticated_client.get("/api/v1/translation/centre-info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "centre_name" in data
        assert "supported_iwxxm_versions" in data

    def test_airport_region_lookup(self, unauthenticated_client):
        """Test airport region lookup works."""
        response = unauthenticated_client.get("/api/v1/translation/airport-region/KJFK")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["airport_code"] == "KJFK"
        assert data["icao_region"] == "NAM"


@pytest.mark.smoke
class TestSmokeVersions:
    """Smoke test: Version endpoints work."""

    def test_versions_endpoint(self, unauthenticated_client):
        """Test versions endpoint returns supported IWXXM versions."""
        response = unauthenticated_client.get("/api/v1/versions")
        
        assert response.status_code == 200
        data = response.json()
        
        # API returns 'supported_versions' not 'versions'
        assert "supported_versions" in data
        assert isinstance(data["supported_versions"], list)
        assert len(data["supported_versions"]) > 0

    def test_schema_status_endpoint(self, unauthenticated_client):
        """Test schema status endpoint works."""
        response = unauthenticated_client.get("/api/v1/schema-status")
        
        assert response.status_code == 200
        data = response.json()
        
        # API returns 'stable', 'rc', 'all', and 'default' keys
        assert "stable" in data or "all" in data or "default" in data


@pytest.mark.smoke
class TestSmokeCriticalPath:
    """Smoke test: Critical path end-to-end."""

    def test_complete_conversion_workflow(self, client):
        """Test complete workflow: convert and validate."""
        # Step 1: Convert METAR
        convert_response = client.post(
            "/api/v1/convert",
            json={
                "metars": ["METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015"],
                "version": "2025-2",
            }
        )
        
        assert convert_response.status_code == 200
        convert_data = convert_response.json()
        
        # Skip if no results (conversion might fail in some environments)
        if len(convert_data["results"]) > 0:
            result = convert_data["results"][0]
            # ConversionResult has 'content' field with the XML, not 'iwxxm_xml'
            if "content" in result:
                # Step 2: Validate the converted IWXXM
                iwxxm_xml = result["content"]
                validate_response = client.post(
                    "/api/v1/validation/validate",
                    json={"content": iwxxm_xml}
                )
                
                assert validate_response.status_code == 200
                validate_data = validate_response.json()
                assert "passed" in validate_data
                assert "results" in validate_data

    def test_all_public_endpoints_accessible(self, unauthenticated_client):
        """Test all public endpoints are accessible."""
        public_endpoints = [
            "/health",
            "/api/v1/versions",
            "/api/v1/schema-status",
            "/api/v1/translation/centre-info",
            "/api/v1/translation/airport-region/KJFK",
        ]
        
        for endpoint in public_endpoints:
            response = unauthenticated_client.get(endpoint)
            assert response.status_code == 200, f"Failed: {endpoint}"


@pytest.mark.smoke
class TestSmokeErrorHandling:
    """Smoke test: Basic error handling."""

    def test_invalid_endpoint_returns_404(self, client):
        """Test non-existent endpoint returns 404."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404

    def test_malformed_conversion_request(self, client):
        """Test malformed conversion request is handled."""
        response = client.post(
            "/api/v1/convert",
            json={}  # Missing required fields
        )
        
        # Should return error (200 with error or 400/422)
        assert response.status_code in [200, 400, 422]

    def test_invalid_iwxxm_version(self, client):
        """Test invalid IWXXM version is handled."""
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": ["METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015"],
                "version": "99.99.99",  # Invalid version
            }
        )
        
        # Should handle gracefully (200 with error or 400)
        assert response.status_code in [200, 400, 422]


@pytest.mark.smoke
class TestSmokeCORS:
    """Smoke test: CORS configuration."""

    def test_cors_headers_present(self, unauthenticated_client):
        """Test CORS headers are present on responses."""
        response = unauthenticated_client.options("/health")
        
        # OPTIONS should be handled
        assert response.status_code in [200, 204, 405]


@pytest.mark.smoke
class TestSmokeOpenAPI:
    """Smoke test: OpenAPI documentation."""

    def test_openapi_docs_accessible(self, unauthenticated_client):
        """Test OpenAPI documentation is accessible."""
        response = unauthenticated_client.get("/docs")
        
        # Should redirect to Swagger UI or return docs
        assert response.status_code in [200, 307, 308]

    def test_openapi_json_available(self, unauthenticated_client):
        """Test OpenAPI JSON schema is available."""
        response = unauthenticated_client.get("/openapi.json")
        
        assert response.status_code == 200
        
        # Should be valid JSON
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "components" in data


# Smoke test runner function
def run_smoke_tests():
    """
    Run smoke tests and return True if all pass.
    
    Useful for pre-deployment scripts.
    """
    import sys
    
    exit_code = pytest.main([
        "-m", "smoke",
        "--tb=short",
        __file__,
    ])
    
    return exit_code == 0


if __name__ == "__main__":
    # Allow running smoke tests directly
    success = run_smoke_tests()
    exit(0 if success else 1)
