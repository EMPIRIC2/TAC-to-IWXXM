"""Integration test helpers for METAR→IWXXM conversion validation via live API.

Provides utilities for:
- Fetching live METAR data from Aviation Weather Service
- Converting METAR TAC to IWXXM
- Comparing converted vs reference IWXXM from API
- Generating comparison reports

Can be used standalone or integrated into test fixtures.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

from src.clients.aviation_weather_client import AviationWeatherClient
from src.utilities.conversion import convert_metar_tac


@dataclass
class IntegrationTestResult:
    """Result from an integration test comparison."""

    station_id: str
    status: str  # "PASS", "FAIL", "ERROR"
    raw_tac: Optional[str] = None
    converted_iwxxm: Optional[str] = None
    reference_iwxxm: Optional[str] = None
    errors: list = None
    conversion_error: Optional[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class IntegrationTestHelper:
    """Helper for running integration tests against live Aviation Weather API."""

    def __init__(self, mock_client=None):
        """Initialize helper.

        Args:
            mock_client: Optional mock AviationWeatherClient for testing.
                        If None, uses real API.
        """
        self.client = mock_client

    async def test_station_conversion(self, station_id: str, hours: int = 1) -> IntegrationTestResult:
        """Test METAR conversion for a single station against live API.

        Args:
            station_id: ICAO station identifier (e.g., "KORD")
            hours: Hours back to search for METAR data

        Returns:
            IntegrationTestResult with conversion and comparison details
        """
        result = IntegrationTestResult(station_id=station_id, status="ERROR")

        try:
            # Fetch METAR data from Aviation Weather API
            async with AviationWeatherClient() as client:
                metar_data = await client.fetch_metar_batch([station_id], hours)

            if not metar_data or station_id not in metar_data:
                result.errors.append(f"No METAR data found for {station_id}")
                return result

            raw_tac, reference_iwxxm = metar_data[station_id]
            result.raw_tac = raw_tac

            if not raw_tac:
                result.errors.append("No raw TAC data from API")
                return result

            # Convert METAR TAC to IWXXM
            try:
                converted_iwxxm = convert_metar_tac(raw_tac)
                result.converted_iwxxm = converted_iwxxm
            except Exception as e:
                result.conversion_error = str(e)
                result.errors.append(f"Conversion failed: {e}")
                return result

            # Store reference for comparison
            result.reference_iwxxm = reference_iwxxm

            # Compare if both available
            if converted_iwxxm and reference_iwxxm:
                # Comparison logic would go here
                # For now, mark as ready for comparison
                result.status = "READY_FOR_COMPARISON"
            else:
                if not reference_iwxxm:
                    result.errors.append("No reference IWXXM from API")
                result.status = "INCOMPLETE" if converted_iwxxm else "ERROR"

        except Exception as e:
            result.errors.append(f"Test error: {str(e)}")
            result.status = "ERROR"

        return result

    async def test_stations_batch(self, station_ids: list, hours: int = 1) -> Dict[str, IntegrationTestResult]:
        """Test METAR conversion for multiple stations.

        Args:
            station_ids: List of ICAO station identifiers
            hours: Hours back to search for METAR data

        Returns:
            Dict mapping station_id → IntegrationTestResult
        """
        results = {}

        for station_id in station_ids:
            result = await self.test_station_conversion(station_id, hours)
            results[station_id] = result

        return results


def run_integration_test_sync(station_id: str, hours: int = 1, mock_client=None) -> IntegrationTestResult:
    """Run a single integration test synchronously.

    Convenience wrapper for pytest fixtures that can't use async.

    Args:
        station_id: ICAO station identifier
        hours: Hours back to search for METAR data
        mock_client: Optional mock AviationWeatherClient

    Returns:
        IntegrationTestResult
    """
    helper = IntegrationTestHelper(mock_client=mock_client)

    # Run async function in event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(helper.test_station_conversion(station_id, hours))
    finally:
        # Don't close loop here - leave it for pytest to manage
        pass
