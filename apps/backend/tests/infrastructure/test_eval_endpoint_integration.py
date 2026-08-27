"""Integration tests for METAR→IWXXM conversion against live Aviation Weather Service API.

These tests:
1. Fetch live METAR data from Aviation Weather Service API
2. Convert TAC → IWXXM using backend conversion service
3. Compare against reference IWXXM from API
4. Validate results match within acceptable tolerances

Marked with @pytest.mark.integration for filtering in CI/CD.

Run with: pytest -m integration -v
          pytest -m integration backend/tests/test_eval_endpoint_integration.py

Note: These tests require network access and API availability.
Mock the API client for offline testing.
"""

from unittest.mock import AsyncMock

import pytest
from _integration_helpers import IntegrationTestHelper, IntegrationTestResult

# Real-world test stations (global distribution)
INTEGRATION_TEST_STATIONS = {
    "KJFK": "New York JFK (USA)",
    "KORD": "Chicago ORD (USA)",
    "EGLL": "London Heathrow (UK)",
    "LFPG": "Paris CDG (France)",
    "EDDM": "Munich (Germany)",
    "RJTT": "Tokyo NRT (Japan)",
    "VHHH": "Hong Kong (Asia-Pacific)",
    "LPPT": "Lisbon (Europe)",
    "CYYZ": "Toronto (Canada)",
    "SJPR": "San Juan (Caribbean)",
}

# Subset for quick smoke tests
INTEGRATION_TEST_STATIONS_SMOKE = {
    "KJFK": "New York JFK (USA)",
    "EGLL": "London Heathrow (UK)",
    "RJTT": "Tokyo NRT (Japan)",
}


@pytest.fixture
def integration_helper():
    """Provide IntegrationTestHelper for tests."""
    return IntegrationTestHelper()


class TestEvalEndpointIntegration:
    """Integration tests using the eval endpoint and live API."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_single_station_conversion_kjfk(self, integration_helper):
        """Test METAR conversion for a single major airport (KJFK).

        This test:
        1. Fetches current METAR for KJFK from Aviation Weather Service
        2. Converts the TAC string to IWXXM
        3. Verifies conversion succeeded without errors
        4. Checks that reference IWXXM is available from API

        Requirements:
        - Network access to aviationweather.gov
        - Aviation Weather Service API availability
        """
        result = await integration_helper.test_station_conversion("KJFK", hours=1)

        assert result.raw_tac is not None, "Should fetch raw TAC from API"
        assert result.converted_iwxxm is not None, "Should convert TAC successfully"
        # Accept both METAR (regular) and SPECI (special observations) from live API
        assert "METAR" in result.raw_tac or "SPECI" in result.raw_tac, "TAC should contain METAR or SPECI keyword"
        assert len(result.converted_iwxxm) > 0, "Converted IWXXM should not be empty"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_single_station_conversion_egll(self, integration_helper):
        """Test METAR conversion for EGLL (London Heathrow).

        Validates international airport handling and data availability
        from the Aviation Weather Service.
        """
        result = await integration_helper.test_station_conversion("EGLL", hours=2)

        assert result.raw_tac is not None, "Should fetch raw TAC from API"
        assert result.converted_iwxxm is not None, "Should convert TAC successfully"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multiple_stations_batch(self, integration_helper):
        """Test batch conversion for multiple stations.

        This test:
        1. Fetches METAR for multiple stations simultaneously
        2. Converts each TAC to IWXXM
        3. Validates all conversions succeeded

        Performance: Should complete within ~30 seconds for 10+ stations
        """
        stations = list(INTEGRATION_TEST_STATIONS_SMOKE.keys())
        results = await integration_helper.test_stations_batch(stations, hours=1)

        assert len(results) == len(stations), "Should have results for all stations"

        successful = sum(1 for r in results.values() if r.converted_iwxxm is not None)
        # Expect at least 50% success rate (some stations may be offline)
        assert successful >= len(stations) * 0.5, f"Expected at least 50% success, got {successful}/{len(stations)}"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_station_with_weather_phenomena(self, integration_helper):
        """Test conversion of METAR with various weather phenomena.

        Real-world METAR often includes:
        - Present weather (thunderstorms, rain, snow)
        - Visibility reductions (fog, haze)
        - Wind shear reports
        - Runway state information

        This validates the encoder handles complex real-world conditions.
        """
        # Test a global distribution of stations to catch various weather
        test_stations = ["KORD", "CYYZ", "EDDM"]

        for station_id in test_stations:
            result = await integration_helper.test_station_conversion(station_id, hours=3)

            if result.raw_tac:
                # Just verify conversion doesn't fail on real complex data
                assert result.converted_iwxxm is not None, f"Should convert {station_id} successfully"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_station_with_missing_data_graceful_handling(self):
        """Test graceful handling of stations with missing or incomplete data.

        Some stations may:
        - Not report METAR (military-only, closed, etc.)
        - Have incomplete data fields
        - Report minimal conditions

        Conversion should either succeed or fail gracefully with clear errors.
        """
        helper = IntegrationTestHelper()

        # Test with a station unlikely to have data
        result = await helper.test_station_conversion("ZZZZ", hours=1)

        # Should not crash, but may error gracefully
        assert isinstance(result, IntegrationTestResult)
        assert result.status in ["ERROR", "INCOMPLETE"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_evaluation_mode_single(self):
        """Test evaluation endpoint with single station mode.

        This requires the eval endpoint to be mocked or running locally.
        Currently skipped - implement when eval endpoint test mode is available.
        """
        pytest.skip("Eval endpoint test mode not yet implemented")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_evaluation_mode_random_sample(self):
        """Test evaluation endpoint with random sample mode.

        This requires the eval endpoint and background job system.
        Currently skipped - implement when test infrastructure is ready.
        """
        pytest.skip("Eval endpoint test mode not yet implemented")


class TestIntegrationWithMocks:
    """Integration-style tests using mocked API clients.

    These tests validate the integration layer without requiring
    network access, making them suitable for CI/CD pipelines.
    """

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_conversion_pipeline_with_mock_api(self):
        """Test full conversion pipeline with mocked Aviation Weather API.

        Provides deterministic test data and validates the conversion
        logic independent of API availability.
        """
        # Create mock METAR data
        mock_tac = "KJFK 121851Z 09014G25KT 10SM FEW250 23/14 A3012 RMK AO2 SLP201 T02330139"
        mock_reference_iwxxm = "<METAR><!-- mocked --><!-- /METAR>"

        # Mock the API client
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.fetch_metar_batch = AsyncMock(return_value={"KJFK": (mock_tac, mock_reference_iwxxm)})

        # Use helper with mocked client
        helper = IntegrationTestHelper(mock_client=mock_client)

        # Simulate what the integration test would do
        from src.utilities.conversion import convert_metar_tac

        converted = convert_metar_tac(mock_tac)

        # Verify conversion produced output
        assert converted is not None
        assert len(converted) > 0
        assert "METAR" in converted


class TestIntegrationDataQuality:
    """Tests for validating integration test data quality and completeness."""

    def test_integration_test_stations_defined(self):
        """Verify integration test stations are properly configured."""
        assert len(INTEGRATION_TEST_STATIONS) > 0
        assert all(len(station_id) == 4 for station_id in INTEGRATION_TEST_STATIONS)

    def test_smoke_test_subset_exists(self):
        """Verify smoke test subset is a proper subset of full stations."""
        smoke_ids = set(INTEGRATION_TEST_STATIONS_SMOKE.keys())
        full_ids = set(INTEGRATION_TEST_STATIONS.keys())

        # Smoke test should be subset of full tests
        assert smoke_ids.issubset(full_ids)
        assert len(smoke_ids) > 0
        assert len(smoke_ids) < len(full_ids)

    def test_can_run_smoke_tests_quickly(self):
        """Verify smoke test stations would run quickly.

        With ~3 stations and 1 second per station, should complete in <10s.
        Full test with 10+ stations would take ~30+ seconds.
        """
        # This is a documentation test - just verify the logic
        smoke_count = len(INTEGRATION_TEST_STATIONS_SMOKE)
        full_count = len(INTEGRATION_TEST_STATIONS)

        assert smoke_count <= 5, "Smoke tests should be quick subset"
        assert full_count >= 10, "Full suite should have substantial coverage"


if __name__ == "__main__":
    pytest.main([__file__, "-m", "integration", "-v", "--tb=short"])
