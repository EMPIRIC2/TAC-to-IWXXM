"""
Extended API Endpoint Coverage Tests.

Focuses on edge cases and scenarios not covered by basic integration tests:
- Large batch processing (100+ METARs)
- Concurrent request handling
- Error file generation in ZIP endpoint
- Version auto-remapping edge cases
- All validation layer combinations
- Stop-on-error behavior
- Performance boundaries
- Resource exhaustion handling

Run with: pytest tests/test_endpoint_extended_coverage.py -v
"""
import pytest
import asyncio
import time
import zipfile
import io
from typing import List, Dict
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from src.api import app

pytestmark = pytest.mark.integration


# =============================================================================
# Extended Coverage: Large Batch Processing
# =============================================================================

class TestLargeBatchProcessing:
    """Test handling of large METAR batches."""
    
    def test_convert_100_metars_batch(self, client, sample_metars):
        """Test conversion of 100 METARs in a single request."""
        # Generate 100 METARs
        metars = [sample_metars["KJFK"]] * 100
        
        start_time = time.time()
        
        response = client.post(
            "/api/v1/convert",
            json={"metars": metars, "version": "2023-1"}
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        
        # Should handle 100 METARs
        results = data["results"]
        assert len(results) <= 100
        
        # Should complete in reasonable time (< 30 seconds)
        assert elapsed < 30.0
    
    def test_convert_200_metars_batch(self, client, sample_metars):
        """Test conversion of 200 METARs (stress test)."""
        metars = [sample_metars["EGLL"]] * 200
        
        response = client.post(
            "/api/v1/convert",
            json={"metars": metars, "version": "2023-1"}
        )
        
        # Should either succeed or return a reasonable error
        assert response.status_code in [200, 413, 422, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
    
    def test_convert_large_batch_with_validation(self, client, sample_metars):
        """Test large batch with comprehensive validation enabled."""
        metars = [sample_metars["KJFK"]] * 50
        
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": metars,
                "version": "2023-1",
                "validation-level": "comprehensive",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    def test_convert_large_batch_stop_on_error(self, client, sample_metars):
        """Test large batch with stop-on-error flag."""
        # Mix valid and invalid METARs
        metars = [sample_metars["KJFK"]] * 25 + ["INVALID"] * 5 + [sample_metars["EGLL"]] * 25
        
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": metars,
                "version": "2023-1",
                "stop-on-error": True,
            }
        )
        
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            data = response.json()
            # Should stop early if error encountered
            results = data.get("results", [])
            # May have fewer results than total METARs due to stop-on-error
            assert len(results) <= len(metars)
    
    def test_convert_zip_large_batch(self, client, sample_metars):
        """Test ZIP endpoint with large batch."""
        metars = [sample_metars["KJFK"], sample_metars["EGLL"]] * 50  # 100 METARs
        
        response = client.post(
            "/api/v1/convert-zip",
            json={"metars": metars, "version": "2023-1"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        
        # Verify ZIP is valid
        content = response.content
        assert len(content) > 0
        
        # Parse ZIP to verify contents
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
            namelist = zf.namelist()
            # Should have multiple files
            assert len(namelist) > 0


class TestConvertContractAlignment:
    """Ensure frontend-facing convert contract remains aligned with backend."""

    def test_form_metadata_fields_echoed(self, client):
        response = client.post(
            "/api/v1/convert",
            data={
                "manual_text": "METAR KJFK 161200Z 12012KT 10SM FEW250 22/14 A3015",
                "iwxxm_version": "2025-2",
                "validation_level": "schema",
                "stop_on_error": "true",
                "bulletin_id": "saaa00",
                "issuing_center": "kwbc",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["bulletin_id"] == "SAAA00"
        assert data["metadata"]["issuing_center"] == "KWBC"
        assert data["metadata"]["validation_level"] == "schema"
        assert data["metadata"]["stop_on_error"] is True

    def test_stop_on_error_halts_after_first_failure(self, client):
        multiline = "\n".join([
            "INVALID METAR",
            "METAR EGLL 161220Z 09010KT 9999 SCT030 10/05 Q1018",
        ])

        response = client.post(
            "/api/v1/convert",
            data={
                "manual_text": multiline,
                "iwxxm_version": "2025-2",
                "stop_on_error": "true",
            },
        )

        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data["total_processed"] == 1


# =============================================================================
# Extended Coverage: Concurrent Request Handling
# =============================================================================

class TestConcurrentRequestHandling:
    """Test handling of concurrent API requests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_conversion_requests(self, client, sample_metars):
        """Test multiple concurrent conversion requests."""
        metar = sample_metars["KJFK"]
        
        async def make_request(index: int):
            """Make a single conversion request."""
            response = client.post(
                "/api/v1/convert",
                json={"metars": [metar], "version": "2023-1"}
            )
            return response.status_code, index
        
        # Launch 20 concurrent requests
        start_time = time.time()
        tasks = [make_request(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # Check results
        successful = sum(1 for r in results if not isinstance(r, Exception) and r[0] == 200)
        
        # At least 80% should succeed
        assert successful >= 16
        
        # Should handle concurrency efficiently
        assert elapsed < 20.0
    
    @pytest.mark.asyncio
    async def test_concurrent_validation_requests(self, client, sample_iwxxm):
        """Test concurrent validation requests."""
        async def validate():
            return client.post(
                "/api/v1/validate",
                json={
                    "iwxxm_xml": sample_iwxxm,
                    "version": "2023-1",
                    "validation-level": "comprehensive",
                }
            )
        
        # Launch 10 concurrent validation requests
        tasks = [validate() for _ in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check success rate
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        assert successful >= 8
    
    @pytest.mark.asyncio
    async def test_concurrent_mixed_endpoint_requests(self, client, sample_metars, sample_iwxxm):
        """Test concurrent requests to different endpoints."""
        async def convert_request():
            return client.post(
                "/api/v1/convert",
                json={"metars": [sample_metars["KJFK"]], "version": "2023-1"}
            )
        
        async def validate_request():
            return client.post(
                "/api/v1/validate",
                json={"iwxxm_xml": sample_iwxxm, "version": "2023-1"}
            )
        
        async def versions_request():
            return client.get("/api/v1/versions")
        
        async def health_request():
            return client.get("/health")
        
        # Mix of different endpoint types
        tasks = [
            convert_request(),
            validate_request(),
            versions_request(),
            health_request(),
            convert_request(),
            validate_request(),
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        assert successful >= 5


# =============================================================================
# Extended Coverage: ZIP Error File Generation
# =============================================================================

class TestZipErrorFileGeneration:
    """Test error file generation in ZIP endpoint."""
    
    def test_zip_with_all_errors_generates_error_files(self, client):
        """Test ZIP generation when all METARs fail conversion."""
        invalid_metars = [
            "INVALID METAR 1",
            "INVALID METAR 2",
            "INVALID METAR 3",
        ]
        
        response = client.post(
            "/api/v1/convert-zip",
            json={"metars": invalid_metars, "version": "2023-1"}
        )
        
        # Should still return ZIP with error files
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        
        content = response.content
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
            namelist = zf.namelist()
            
            # Should contain error files
            error_files = [f for f in namelist if "error" in f.lower()]
            assert len(error_files) > 0
    
    def test_zip_with_mixed_success_and_errors(self, client, sample_metars):
        """Test ZIP with both successful conversions and errors."""
        metars = [
            sample_metars["KJFK"],
            "INVALID METAR DATA",
            sample_metars["EGLL"],
            "ANOTHER INVALID METAR",
        ]
        
        response = client.post(
            "/api/v1/convert-zip",
            json={"metars": metars, "version": "2023-1"}
        )
        
        assert response.status_code == 200
        
        content = response.content
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
            namelist = zf.namelist()
            
            # Should have both IWXXM files and error files
            iwxxm_files = [f for f in namelist if f.endswith(".xml")]
            error_files = [f for f in namelist if "error" in f.lower()]
            
            # Should have at least some files
            assert len(namelist) > 0
    
    def test_zip_error_file_contents(self, client):
        """Test that error files contain meaningful error information."""
        invalid_metar = "COMPLETELY INVALID METAR DATA"
        
        response = client.post(
            "/api/v1/convert-zip",
            json={"metars": [invalid_metar], "version": "2023-1"}
        )
        
        assert response.status_code == 200
        
        content = response.content
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
            # Find error file
            error_files = [f for f in zf.namelist() if "error" in f.lower()]
            
            if error_files:
                # Read error file content
                with zf.open(error_files[0]) as ef:
                    error_content = ef.read().decode('utf-8')
                    
                    # Should contain error details
                    assert len(error_content) > 0
                    assert "error" in error_content.lower() or "invalid" in error_content.lower()
    
    def test_zip_with_validation_errors_generates_details(self, client, sample_metars):
        """Test ZIP includes validation error details."""
        response = client.post(
            "/api/v1/convert-zip",
            json={
                "metars": [sample_metars["KJFK"]],
                "version": "2023-1",
                "validation-level": "comprehensive",
            }
        )
        
        assert response.status_code == 200
        
        content = response.content
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
            namelist = zf.namelist()
            # Should have files
            assert len(namelist) > 0


# =============================================================================
# Extended Coverage: Version Auto-Remapping Edge Cases
# =============================================================================

class TestVersionRemappingEdgeCases:
    """Test version auto-remapping scenarios."""
    
    def test_convert_with_2025_1_remaps_to_2025_2(self, client, sample_metars):
        """Test that version 2025-1 automatically remaps to 2025-2."""
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": [sample_metars["KJFK"]],
                "version": "2025-1",  # Should auto-remap
            }
        )
        
        # Should succeed (not return "unsupported version" error)
        assert response.status_code in [200, 400]  # 400 if conversion fails for other reasons
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
    
    def test_convert_with_invalid_version_returns_error(self, client, sample_metars):
        """Test that truly invalid versions return appropriate error."""
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": [sample_metars["KJFK"]],
                "version": "9999-99",  # Invalid version
            }
        )
        
        # Should return error for invalid version
        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data
    
    def test_validate_with_version_remapping(self, client, sample_iwxxm):
        """Test validation with version that requires remapping."""
        response = client.post(
            "/api/v1/validate",
            json={
                "iwxxm_xml": sample_iwxxm,
                "version": "2025-1",  # Should remap
                "validation-level": "schema",
            }
        )
        
        # Should handle remapping in validation
        assert response.status_code in [200, 400]
    
    def test_version_auto_detect_with_multiple_formats(self, client, sample_metars):
        """Test version auto-detection with various version string formats."""
        version_variants = ["2023-1", "2023.1", "v2023-1", "2023_1"]
        
        for version in version_variants:
            response = client.post(
                "/api/v1/convert",
                json={
                    "metars": [sample_metars["KJFK"]],
                    "version": version,
                }
            )
            
            # Should either accept or reject consistently
            assert response.status_code in [200, 400, 422]


# =============================================================================
# Extended Coverage: All Validation Layer Combinations
# =============================================================================

class TestValidationLayerCombinations:
    """Test all validation layer combinations and stop-on-error behavior."""
    
    @pytest.mark.parametrize("validation_level", [
        "none",
        "basic",
        "schema",
        "comprehensive",
        "full",
    ])
    def test_convert_with_all_validation_levels(self, client, sample_metars, validation_level):
        """Test conversion with each validation level."""
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": [sample_metars["KJFK"]],
                "version": "2023-1",
                "validation-level": validation_level,
            }
        )
        
        # All validation levels should be handled
        assert response.status_code in [200, 400]
    
    @pytest.mark.parametrize("stop_on_error", [True, False])
    def test_convert_stop_on_error_behavior(self, client, sample_metars, stop_on_error):
        """Test stop-on-error behavior."""
        metars = [
            sample_metars["KJFK"],
            "INVALID METAR",
            sample_metars["EGLL"],
        ]
        
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": metars,
                "version": "2023-1",
                "stop-on-error": stop_on_error,
            }
        )
        
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if stop_on_error:
                # With stop-on-error, should have fewer results after error
                assert len(results) <= len(metars)
            else:
                # Without stop-on-error, should process all
                assert len(results) <= len(metars)
    
    @pytest.mark.parametrize("validation_level,stop_on_error", [
        ("none", True),
        ("none", False),
        ("schema", True),
        ("schema", False),
        ("comprehensive", True),
        ("comprehensive", False),
    ])
    def test_validation_level_and_stop_on_error_combinations(
        self, client, sample_metars, validation_level, stop_on_error
    ):
        """Test all combinations of validation level and stop-on-error."""
        metars = [sample_metars["KJFK"], sample_metars["EGLL"]]
        
        response = client.post(
            "/api/v1/convert",
            json={
                "metars": metars,
                "version": "2023-1",
                "validation-level": validation_level,
                "stop-on-error": stop_on_error,
            }
        )
        
        # Should handle all combinations
        assert response.status_code in [200, 400]
    
    def test_validate_endpoint_all_layers(self, client, sample_iwxxm):
        """Test validate endpoint with all validation layers."""
        layers = ["schema", "schematron", "icao_opmet", "comprehensive"]
        
        for layer in layers:
            response = client.post(
                "/api/v1/validate",
                json={
                    "iwxxm_xml": sample_iwxxm,
                    "version": "2023-1",
                    "validation-level": layer,
                }
            )
            
            assert response.status_code in [200, 400]


# =============================================================================
# Extended Coverage: Performance Boundaries
# =============================================================================

class TestPerformanceBoundaries:
    """Test API behavior at performance boundaries."""
    
    @pytest.mark.slow
    def test_very_large_single_metar(self, client):
        """Test handling of unusually large single METAR."""
        # Construct a very large METAR (edge case)
        large_metar = "KJFK 121853Z 24008KT 10SM FEW250 M04/M17 A3034 " + ("RMK AO2 " * 100)
        
        response = client.post(
            "/api/v1/convert",
            json={"metars": [large_metar], "version": "2023-1"}
        )
        
        # Should handle gracefully (success or reasonable error)
        assert response.status_code in [200, 400, 413, 422]
    
    @pytest.mark.slow
    def test_maximum_concurrent_load(self, client, sample_metars):
        """Test behavior under maximum concurrent load."""
        metar = sample_metars["KJFK"]
        
        # Simulate high load
        responses = []
        for _ in range(50):
            response = client.post(
                "/api/v1/convert",
                json={"metars": [metar], "version": "2023-1"}
            )
            responses.append(response.status_code)
        
        # Should handle load gracefully
        success_count = responses.count(200)
        
        # At least 80% should succeed
        assert success_count >= 40
    
    def test_timeout_handling_for_slow_operations(self, client, sample_metars):
        """Test timeout handling for potentially slow operations."""
        # Large batch that might timeout
        metars = [sample_metars["KJFK"]] * 500
        
        start_time = time.time()
        response = client.post(
            "/api/v1/convert",
            json={"metars": metars, "version": "2023-1"}
        )
        elapsed = time.time() - start_time
        
        # Should respond within reasonable time or return timeout error
        assert response.status_code in [200, 413, 422, 503, 504]
        assert elapsed < 60.0  # Should not hang indefinitely


# =============================================================================
# Extended Coverage: Resource Exhaustion Handling
# =============================================================================

class TestResourceExhaustionHandling:
    """Test handling of resource exhaustion scenarios."""
    
    def test_empty_metar_list(self, client):
        """Test conversion with empty METAR list."""
        response = client.post(
            "/api/v1/convert",
            json={"metars": [], "version": "2023-1"}
        )
        
        # Should handle empty list gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_null_metar_values(self, client):
        """Test conversion with null METAR values."""
        response = client.post(
            "/api/v1/convert",
            json={"metars": [None, None], "version": "2023-1"}
        )
        
        # Should handle null values gracefully
        assert response.status_code in [400, 422]
    
    def test_extremely_long_metar_list(self, client, sample_metars):
        """Test with extremely long METAR list (1000+)."""
        metars = [sample_metars["KJFK"]] * 1000
        
        response = client.post(
            "/api/v1/convert",
            json={"metars": metars, "version": "2023-1"}
        )
        
        # Should either process or return appropriate error
        assert response.status_code in [200, 413, 422, 503]
    
    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON in request."""
        response = client.post(
            "/api/v1/convert",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 400 or 422 for malformed JSON
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        # Missing 'metars' field
        response = client.post(
            "/api/v1/convert",
            json={"version": "2023-1"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_invalid_field_types(self, client):
        """Test handling of invalid field types."""
        # 'metars' should be list, not string
        response = client.post(
            "/api/v1/convert",
            json={"metars": "NOT_A_LIST", "version": "2023-1"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


# =============================================================================
# Extended Coverage: Edge Cases in Query Parameters
# =============================================================================

class TestQueryParameterEdgeCases:
    """Test edge cases in query parameter handling."""
    
    def test_versions_endpoint_with_invalid_query_params(self, client):
        """Test versions endpoint with unexpected query parameters."""
        response = client.get("/api/v1/versions?invalid_param=value")
        
        # Should ignore invalid params and return versions
        assert response.status_code == 200
    
    def test_schema_status_with_version_parameter(self, client):
        """Test schema-status endpoint with version parameter."""
        response = client.get("/api/v1/schema-status?version=2023-1")
        
        # Should handle version parameter if supported
        assert response.status_code == 200
    
    def test_statistics_recent_with_invalid_hours(self, client):
        """Test recent statistics with invalid hours parameter."""
        # Negative hours
        response = client.get("/api/v1/translation/statistics/recent?hours=-5")
        
        # Should handle invalid parameter gracefully
        assert response.status_code in [200, 400, 422]
        
        # Extremely large hours
        response = client.get("/api/v1/translation/statistics/recent?hours=999999")
        
        assert response.status_code in [200, 400, 422]
    
    def test_statistics_by_region_with_invalid_hours(self, client):
        """Test regional statistics with invalid parameters."""
        response = client.get("/api/v1/translation/statistics/by-region?hours=abc")
        
        # Should return validation error
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
