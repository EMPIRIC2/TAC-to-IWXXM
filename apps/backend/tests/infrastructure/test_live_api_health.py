"""Live API health check suite for production monitoring.

This test suite performs real HTTP requests to a deployed API instance
to verify endpoint availability and basic functionality. Suitable for:
- Continuous monitoring in production
- Pre-deployment smoke testing
- Post-deployment verification
- CI/CD health checks

Configuration via environment variables:
- LIVE_API_URL: Base URL of deployed API (required)
- ADMIN_EMAIL / ADMIN_PASSWORD: Credentials for runtime JWT via POST /auth/login
- LIVE_API_TIMEOUT: Request timeout in seconds (default: 30)

Run with: pytest -m live_api backend/tests/test_live_api_health.py -v

Skip with: pytest -m "not live_api"
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.live_fixtures import live_api_base  # noqa: E402

# Configuration
LIVE_API_URL = live_api_base()
LIVE_API_TIMEOUT = int(os.getenv("LIVE_API_TIMEOUT", "30"))
# Render free tier can cold-start during concurrent probes
CONCURRENT_HEALTH_THRESHOLD = float(os.getenv("LIVE_CONCURRENT_HEALTH_THRESHOLD", "30"))

# Performance thresholds (seconds)
HEALTH_CHECK_THRESHOLD = 2.0
VERSION_CHECK_THRESHOLD = 2.0
CONVERSION_THRESHOLD = 5.0
VALIDATION_THRESHOLD = 10.0

LIVE_CONVERT_PAYLOAD = {
    "metars": ["METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015 RMK AO2 SLP210"],
    "version": "2025-2",
}


class TestLiveAPIHealth:
    """Live API health check tests."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_health_endpoint(self, live_client_public):
        """Test /health endpoint responds successfully."""
        start_time = datetime.now()
        response = await live_client_public.get("/health")
        duration = (datetime.now() - start_time).total_seconds()

        assert response.status_code == 200, f"Health check failed: {response.text}"

        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]

        # Performance check
        assert duration < HEALTH_CHECK_THRESHOLD, f"Health check too slow: {duration:.2f}s > {HEALTH_CHECK_THRESHOLD}s"

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_health_check_structure(self, live_client_public):
        """Test health endpoint returns expected structure."""
        response = await live_client_public.get("/health")
        data = response.json()

        # Should contain status and GIFTs availability
        assert "status" in data
        assert "gifts_available" in data or "message" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_versions_endpoint(self, live_client_public):
        """Test /api/v1/versions endpoint returns supported versions."""
        start_time = datetime.now()
        response = await live_client_public.get("/api/v1/versions")
        duration = (datetime.now() - start_time).total_seconds()

        assert response.status_code == 200
        data = response.json()

        assert "supported_versions" in data
        assert isinstance(data["supported_versions"], list)
        assert len(data["supported_versions"]) > 0

        version_ids = [v["version"] for v in data["supported_versions"]]
        assert "2025-2" in version_ids

        # Performance check
        assert duration < VERSION_CHECK_THRESHOLD

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_schema_status_endpoint(self, live_client_public):
        """Test /api/v1/schema-status endpoint."""
        response = await live_client_public.get("/api/v1/schema-status")

        assert response.status_code == 200
        data = response.json()

        assert "supported_versions" in data or "stable" in data or "all" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_translation_centre_info(self, live_client_public):
        """Test /api/v1/translation/centre-info endpoint."""
        response = await live_client_public.get("/api/v1/translation/centre-info")

        assert response.status_code == 200
        data = response.json()

        assert "centre_name" in data
        assert "centre_designator" in data
        assert "icao_location_indicator" in data
        assert "supported_iwxxm_versions" in data
        assert "supported_products" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_airport_region_lookup(self, live_client_public):
        """Test /api/v1/translation/airport-region/{code} endpoint."""
        test_airports = {
            "KJFK": "NAM",
            "EGLL": "EUR",
            "RJTT": "APAC",
        }

        for airport_code, expected_region in test_airports.items():
            response = await live_client_public.get(f"/api/v1/translation/airport-region/{airport_code}")

            assert response.status_code == 200
            data = response.json()

            assert data["airport_code"] == airport_code
            assert data["icao_region"] == expected_region


class TestLiveAPIAuthentication:
    """Test authenticated endpoints (runtime JWT from login fixture)."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_auth_me_endpoint(self, live_client, verify_live_api_configured):
        """Test /auth/me returns authenticated user profile."""
        response = await live_client.get("/auth/me")
        assert response.status_code == 200, response.text
        data = response.json()
        assert "email" in data or "user" in data or "id" in data

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_convert_endpoint_authenticated(self, live_client, verify_live_api_configured):
        """Test /api/v1/convert endpoint with authentication."""
        start_time = datetime.now()
        response = await live_client.post("/api/v1/convert", json=LIVE_CONVERT_PAYLOAD)
        duration = (datetime.now() - start_time).total_seconds()

        assert response.status_code == 200, f"Conversion failed: {response.text}"

        data = response.json()
        assert data.get("successful", 0) >= 1
        assert len(data.get("results", [])) > 0

        result = data["results"][0]
        assert "content" in result
        assert len(result["content"]) > 0
        assert "iwxxm" in result["content"].lower()

        # Performance check
        assert duration < CONVERSION_THRESHOLD, f"Conversion too slow: {duration:.2f}s > {CONVERSION_THRESHOLD}s"

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_convert_endpoint_without_auth(self, verify_live_api_configured):
        """Test convert endpoint rejects unauthenticated requests when auth is enabled."""
        payload = {"metars": ["METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015"], "version": "2025-2"}
        async with httpx.AsyncClient(base_url=LIVE_API_URL.rstrip("/"), timeout=LIVE_API_TIMEOUT) as client:
            response = await client.post("/api/v1/convert", json=payload)

            if response.status_code == 200:
                pytest.skip("Auth disabled on target stack (unauthenticated convert succeeded)")
            assert response.status_code == 401, (
                f"Expected 401 for unauthenticated convert, got {response.status_code}: {response.text}"
            )

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_validation_layers_endpoint(self, live_client, verify_live_api_configured):
        """Test /api/v1/validation/layers endpoint."""
        response = await live_client.get("/api/v1/validation/layers")

        assert response.status_code == 200
        data = response.json()

        assert "layers" in data
        assert len(data["layers"]) == 7  # All 7 validation layers

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_validation_validate_endpoint(self, live_client, verify_live_api_configured):
        """Test /api/v1/validation/validate endpoint."""
        start_time = datetime.now()
        response = await live_client.post(
            "/api/v1/validation/validate",
            json={
                "content": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
            },
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

        # Render cold-start can stall one concurrent probe on free tier
        assert duration < CONCURRENT_HEALTH_THRESHOLD, (
            f"Concurrent requests too slow: {duration:.2f}s > {CONCURRENT_HEALTH_THRESHOLD}s"
        )

    @pytest.mark.live_api
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_multiple_conversions_sequential(self, live_client, verify_live_api_configured):
        """Test multiple sequential conversions."""
        test_metars = [
            "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
            "METAR EGLL 161200Z 27015KT 9999 FEW040 18/12 Q1015",
            "METAR RJTT 161200Z 09008KT 10SM FEW030 20/15 A2995",
        ]

        start_time = datetime.now()
        for metar in test_metars:
            response = await live_client.post(
                "/api/v1/convert",
                json={"metars": [metar], "version": "2025-2"},
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
    async def test_invalid_endpoint_returns_404(self, live_client_public):
        """Test accessing non-existent endpoint returns 404."""
        response = await live_client_public.get("/api/v1/nonexistent")

        assert response.status_code == 404

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_malformed_request_returns_400(self, live_client, verify_live_api_configured):
        """Test malformed request returns 400."""
        response = await live_client.post("/api/v1/convert", json={"invalid_field": "value"})

        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422]

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_invalid_metar_handled_gracefully(self, live_client, verify_live_api_configured):
        """Test invalid METAR is handled gracefully."""
        response = await live_client.post("/api/v1/convert", json={"metars": ["INVALID METAR STRING"]})

        # Should return 200 with error in results, or 400
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert data.get("failed", 0) >= 1 or data.get("errors")


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
    async def test_api_returns_valid_json(self, live_client_public):
        """Test API returns valid JSON responses."""
        response = await live_client_public.get("/health")

        assert response.status_code == 200

        # Should be able to parse as JSON
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("API did not return valid JSON")

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_api_cors_headers(self, live_client_public):
        """Test API returns appropriate CORS headers."""
        response = await live_client_public.options("/health")

        # Should handle OPTIONS request (some routes return 405 on /health)
        assert response.status_code in [200, 204, 405]

        # May have CORS headers
        # This is informational, not a failure
        if "access-control-allow-origin" in response.headers:
            print(f"CORS enabled: {response.headers['access-control-allow-origin']}")


class TestLiveAPIMonitoring:
    """Tests for continuous monitoring and alerting."""

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_critical_path_health(self, live_client_public, verify_live_api_configured):
        """Test critical path: health, version, centre info (no auth required)."""
        endpoints = [
            ("/health", "Health Check"),
            ("/api/v1/versions", "Version Info"),
            ("/api/v1/translation/centre-info", "Centre Info"),
        ]

        failures = []
        for endpoint, name in endpoints:
            try:
                response = await live_client_public.get(endpoint)
                if response.status_code != 200:
                    failures.append(f"{name} ({endpoint}): Status {response.status_code}")
            except Exception as e:
                failures.append(f"{name} ({endpoint}): {str(e)}")

        assert len(failures) == 0, f"Critical path failures: {', '.join(failures)}"

    @pytest.mark.live_api
    @pytest.mark.asyncio
    async def test_response_times_acceptable(self, live_client_public):
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
            response = await live_client_public.get(endpoint)
            duration = (datetime.now() - start_time).total_seconds()

            if duration > threshold:
                slow_endpoints.append(f"{endpoint}: {duration:.2f}s > {threshold}s")

        assert len(slow_endpoints) == 0, f"Slow endpoints: {', '.join(slow_endpoints)}"
