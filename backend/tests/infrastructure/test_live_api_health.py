"""Live API health check suite for production monitoring.

This test suite performs real HTTP requests to a deployed API instance
to verify endpoint availability and basic functionality. Suitable for:
- Continuous monitoring in production
- Pre-deployment smoke testing
- Post-deployment verification
- CI/CD health checks

Configuration via environment variables:
- LIVE_API_URL: Base URL of deployed API (required)
- LIVE_API_TOKEN: Bearer token for authenticated endpoints (optional)
- LIVE_API_TIMEOUT: Request timeout in seconds (default: 30)

Run with: pytest -m live_api backend/tests/test_live_api_health.py -v

Skip with: pytest -m "not live_api"
"""

import os
import pytest
import httpx
from datetime import datetime


# Configuration
LIVE_API_URL = os.getenv("LIVE_API_URL", "http://localhost:8000")
LIVE_API_TOKEN = os.getenv("LIVE_API_TOKEN", "")
LIVE_API_TIMEOUT = int(os.getenv("LIVE_API_TIMEOUT", "30"))

# Performance thresholds (seconds)
HEALTH_CHECK_THRESHOLD = 2.0
VERSION_CHECK_THRESHOLD = 2.0
CONVERSION_THRESHOLD = 5.0
VALIDATION_THRESHOLD = 10.0


@pytest.fixture
async def live_client():
    """Create httpx AsyncClient for live API testing."""
    headers = {}
    if LIVE_API_TOKEN:
        headers["Authorization"] = f"Bearer {LIVE_API_TOKEN}"
    
    # Check if API is available before running tests
    try:
        async with httpx.AsyncClient(
            base_url=LIVE_API_URL,
            headers=headers,
            timeout=5.0,  # Short timeout for availability check
            follow_redirects=True
        ) as test_client:
            await test_client.get("/health")
    except (httpx.ConnectError, httpx.TimeoutException):
        pytest.skip(f"Live API not available at {LIVE_API_URL}")
    
    # If we get here, API is available
    async with httpx.AsyncClient(
        base_url=LIVE_API_URL,
        headers=headers,
        timeout=LIVE_API_TIMEOUT,
        follow_redirects=True
    ) as client:
        yield client


@pytest.fixture
def verify_live_api_configured():
    """Verify live API URL is configured."""
    if not LIVE_API_URL or LIVE_API_URL == "http://localhost:8000":
        pytest.skip("LIVE_API_URL not configured or using default")


class TestLiveAPIHealth:
    """Live API health check tests."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_health_endpoint(self, live_client):
        """Test /health endpoint responds successfully."""
        start_time = datetime.now()
        response = await live_client.get("/health")
        duration = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]
        
        # Performance check
        assert duration < HEALTH_CHECK_THRESHOLD, (
            f"Health check too slow: {duration:.2f}s > {HEALTH_CHECK_THRESHOLD}s"
        )

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_health_check_structure(self, live_client):
        """Test health endpoint returns expected structure."""
        response = await live_client.get("/health")
        data = response.json()
        
        # Should contain status and GIFTs availability
        assert "status" in data
        assert "gifts_available" in data or "message" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_versions_endpoint(self, live_client):
        """Test /api/v1/versions endpoint returns supported versions."""
        start_time = datetime.now()
        response = await live_client.get("/api/v1/versions")
        duration = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200
        data = response.json()
        
        assert "versions" in data
        assert isinstance(data["versions"], list)
        assert len(data["versions"]) > 0
        
        # Verify 2025-2 is present
        version_ids = [v["version"] for v in data["versions"]]
        assert "2025-2" in version_ids or "3.0.0" in version_ids
        
        # Performance check
        assert duration < VERSION_CHECK_THRESHOLD

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_schema_status_endpoint(self, live_client):
        """Test /api/v1/schema-status endpoint."""
        response = await live_client.get("/api/v1/schema-status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain version information
        assert "supported_versions" in data or "schemas" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_translation_centre_info(self, live_client):
        """Test /api/v1/translation/centre-info endpoint."""
        response = await live_client.get("/api/v1/translation/centre-info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "centre_name" in data
        assert "centre_designator" in data
        assert "icao_location_indicator" in data
        assert "supported_iwxxm_versions" in data
        assert "supported_products" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_airport_region_lookup(self, live_client):
        """Test /api/v1/translation/airport-region/{code} endpoint."""
        test_airports = {
            "KJFK": "NAM",
            "EGLL": "EUR",
            "RJTT": "APAC",
        }
        
        for airport_code, expected_region in test_airports.items():
            response = await live_client.get(f"/api/v1/translation/airport-region/{airport_code}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["airport_code"] == airport_code
            assert data["icao_region"] == expected_region


class TestLiveAPIAuthentication:
    """Test authenticated endpoints (requires LIVE_API_TOKEN)."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_convert_endpoint_authenticated(self, live_client, verify_live_api_configured):
        """Test /api/v1/convert endpoint with authentication."""
        if not LIVE_API_TOKEN:
            pytest.skip("LIVE_API_TOKEN not configured")
        
        start_time = datetime.now()
        response = await live_client.post(
            "/api/v1/convert",
            json={
                "manual_text": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015 RMK AO2 SLP210",
                "iwxxm_version": "2025-2",
            }
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200, f"Conversion failed: {response.text}"
        
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        
        result = data["results"][0]
        assert result["status"] == "success"
        assert "iwxxm_xml" in result
        assert len(result["iwxxm_xml"]) > 0
        
        # Performance check
        assert duration < CONVERSION_THRESHOLD, (
            f"Conversion too slow: {duration:.2f}s > {CONVERSION_THRESHOLD}s"
        )

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_convert_endpoint_without_auth(self, verify_live_api_configured):
        """Test convert endpoint requires authentication."""
        # Create client without auth header
        async with httpx.AsyncClient(base_url=LIVE_API_URL, timeout=LIVE_API_TIMEOUT) as client:
            response = await client.post(
                "/api/v1/convert",
                json={
                    "manual_text": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
                }
            )
            
            # Should require authentication
            assert response.status_code == 401

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_validation_layers_endpoint(self, live_client, verify_live_api_configured):
        """Test /api/v1/validation/layers endpoint."""
        if not LIVE_API_TOKEN:
            pytest.skip("LIVE_API_TOKEN not configured")
        
        response = await live_client.get("/api/v1/validation/layers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "layers" in data
        assert len(data["layers"]) == 7  # All 7 validation layers

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_validation_validate_endpoint(self, live_client, verify_live_api_configured):
        """Test /api/v1/validation/validate endpoint."""
        if not LIVE_API_TOKEN:
            pytest.skip("LIVE_API_TOKEN not configured")
        
        start_time = datetime.now()
        response = await live_client.post(
            "/api/v1/validation/validate",
            json={
                "content": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
            }
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200
        data = response.json()
        
        assert "passed" in data
        assert "results" in data
        
        # Performance check
        assert duration < VALIDATION_THRESHOLD


class TestLiveAPIPerformance:
    """Performance and load testing for live API."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_health_checks(self, verify_live_api_configured):
        """Test API handles concurrent health check requests."""
        import asyncio
        
        async def health_check():
            async with httpx.AsyncClient(base_url=LIVE_API_URL, timeout=LIVE_API_TIMEOUT) as client:
                response = await client.get("/health")
                return response.status_code
        
        # Run 10 concurrent health checks
        start_time = datetime.now()
        results = await asyncio.gather(*[health_check() for _ in range(10)])
        duration = (datetime.now() - start_time).total_seconds()
        
        # All should succeed
        assert all(status == 200 for status in results)
        
        # Should complete reasonably fast
        assert duration < 5.0, f"Concurrent requests too slow: {duration:.2f}s"

    @pytest.mark.live_api
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_multiple_conversions_sequential(self, live_client, verify_live_api_configured):
        """Test multiple sequential conversions."""
        if not LIVE_API_TOKEN:
            pytest.skip("LIVE_API_TOKEN not configured")
        
        test_metars = [
            "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
            "METAR EGLL 161200Z 27015KT 9999 FEW040 18/12 Q1015",
            "METAR RJTT 161200Z 09008KT 10SM FEW030 20/15 A2995",
        ]
        
        start_time = datetime.now()
        for metar in test_metars:
            response = await live_client.post(
                "/api/v1/convert",
                json={"manual_text": metar, "iwxxm_version": "2025-2"}
            )
            assert response.status_code == 200
        
        duration = (datetime.now() - start_time).total_seconds()
        avg_duration = duration / len(test_metars)
        
        # Average should be reasonable
        assert avg_duration < CONVERSION_THRESHOLD


class TestLiveAPIErrorHandling:
    """Test error handling in live API."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_invalid_endpoint_returns_404(self, live_client):
        """Test accessing non-existent endpoint returns 404."""
        response = await live_client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_malformed_request_returns_400(self, live_client, verify_live_api_configured):
        """Test malformed request returns 400."""
        if not LIVE_API_TOKEN:
            pytest.skip("LIVE_API_TOKEN not configured")
        
        response = await live_client.post(
            "/api/v1/convert",
            json={"invalid_field": "value"}
        )
        
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422]

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_invalid_metar_handled_gracefully(self, live_client, verify_live_api_configured):
        """Test invalid METAR is handled gracefully."""
        if not LIVE_API_TOKEN:
            pytest.skip("LIVE_API_TOKEN not configured")
        
        response = await live_client.post(
            "/api/v1/convert",
            json={"manual_text": "INVALID METAR STRING"}
        )
        
        # Should return 200 with error in results, or 400
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            if len(data["results"]) > 0:
                # Error should be reported in result
                assert "error" in data["results"][0] or data["results"][0]["status"] == "error"


class TestLiveAPIAvailability:
    """Test API availability and uptime monitoring."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_api_is_reachable(self, verify_live_api_configured):
        """Test API is reachable at configured URL."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{LIVE_API_URL}/health")
                assert response.status_code == 200
        except httpx.ConnectError:
            pytest.fail(f"Cannot connect to API at {LIVE_API_URL}")
        except httpx.TimeoutException:
            pytest.fail(f"API at {LIVE_API_URL} timed out")

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_api_returns_valid_json(self, live_client):
        """Test API returns valid JSON responses."""
        response = await live_client.get("/health")
        
        assert response.status_code == 200
        
        # Should be able to parse as JSON
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("API did not return valid JSON")

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_api_cors_headers(self, live_client):
        """Test API returns appropriate CORS headers."""
        response = await live_client.options("/health")
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 204]
        
        # May have CORS headers
        # This is informational, not a failure
        if "access-control-allow-origin" in response.headers:
            print(f"CORS enabled: {response.headers['access-control-allow-origin']}")


class TestLiveAPIMonitoring:
    """Tests for continuous monitoring and alerting."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_critical_path_health(self, live_client, verify_live_api_configured):
        """Test critical path: health, version, centre info (no auth required)."""
        endpoints = [
            ("/health", "Health Check"),
            ("/api/v1/versions", "Version Info"),
            ("/api/v1/translation/centre-info", "Centre Info"),
        ]
        
        failures = []
        for endpoint, name in endpoints:
            try:
                response = await live_client.get(endpoint)
                if response.status_code != 200:
                    failures.append(f"{name} ({endpoint}): Status {response.status_code}")
            except Exception as e:
                failures.append(f"{name} ({endpoint}): {str(e)}")
        
        assert len(failures) == 0, f"Critical path failures: {', '.join(failures)}"

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_response_times_acceptable(self, live_client):
        """Test all public endpoints respond within acceptable time."""
        endpoints = [
            ("/health", HEALTH_CHECK_THRESHOLD),
            ("/api/v1/versions", VERSION_CHECK_THRESHOLD),
            ("/api/v1/schema-status", VERSION_CHECK_THRESHOLD),
            ("/api/v1/translation/centre-info", VERSION_CHECK_THRESHOLD),
        ]
        
        slow_endpoints = []
        for endpoint, threshold in endpoints:
            start_time = datetime.now()
            response = await live_client.get(endpoint)
            duration = (datetime.now() - start_time).total_seconds()
            
            if duration > threshold:
                slow_endpoints.append(f"{endpoint}: {duration:.2f}s > {threshold}s")
        
        assert len(slow_endpoints) == 0, f"Slow endpoints: {', '.join(slow_endpoints)}"
