"""Tests for the evaluation system."""
# Mock the imports before importing the module
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))


@pytest.fixture
def mock_station_sampler():
    """Mock StationSampler."""
    with patch("src.utilities.station_sampler.StationSampler") as mock:
        instance = Mock()
        instance.sample_random_stations.return_value = ["KJFK", "KLAX", "KORD"]
        instance.get_all_major_airports.return_value = ["KJFK", "KLAX", "KORD", "KATL", "KDFW"]
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_aviation_weather_client():
    """Mock AviationWeatherClient."""
    with patch("src.clients.aviation_weather_client.AviationWeatherClient") as mock:
        instance = AsyncMock()
        instance.fetch_metar_batch.return_value = {
            "KJFK": (
                "METAR KJFK 101851Z 24008KT 10SM FEW250 M04/M17 A3034",
                '<?xml version="1.0"?><METAR>test</METAR>'
            ),
            "KLAX": (
                "METAR KLAX 101853Z 26010KT 10SM FEW015 16/12 A2990",
                '<?xml version="1.0"?><METAR>test</METAR>'
            ),
        }
        instance.__aenter__.return_value = instance
        instance.__aexit__.return_value = None
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_evaluation_service():
    """Mock EvaluationService."""
    with patch("src.services.evaluation_service.EvaluationService") as mock:
        from src.services.evaluation_service import ComparisonResult

        instance = Mock()
        instance.compare_iwxxm.return_value = ComparisonResult(
            passed=True,
            our_elements=50,
            their_elements=50,
            missing_elements=[],
            extra_elements=[],
            value_mismatches=[],
            error_message=None
        )
        mock.return_value = instance
        yield instance


class TestStationSampler:
    """Tests for StationSampler utility."""

    def test_sample_random_stations(self, tmp_path):
        """Test random station sampling."""
        from src.utilities.station_sampler import StationSampler

        # Create test CSV
        csv_file = tmp_path / "airports.csv"
        csv_file.write_text(
            "id,ident,type,name,icao_code,scheduled_service\n"
            "1,KJFK,large_airport,JFK,KJFK,1\n"
            "2,KLAX,large_airport,LAX,KLAX,1\n"
            "3,KORD,large_airport,ORD,KORD,1\n"
            "4,KSMX,small_airport,SMX,KSMX,0\n"
        )

        sampler = StationSampler(csv_path=csv_file)
        stations = sampler.sample_random_stations(2, large_airports_only=True, seed=42)

        assert len(stations) == 2
        assert all(s in ["KJFK", "KLAX", "KORD"] for s in stations)

    def test_get_all_major_airports(self, tmp_path):
        """Test getting all major airports."""
        from src.utilities.station_sampler import StationSampler

        csv_file = tmp_path / "airports.csv"
        csv_file.write_text(
            "id,ident,type,name,icao_code,scheduled_service\n"
            "1,KJFK,large_airport,JFK,KJFK,1\n"
            "2,KLAX,large_airport,LAX,KLAX,1\n"
            "3,KSMX,small_airport,SMX,KSMX,0\n"
        )

        sampler = StationSampler(csv_path=csv_file)
        airports = sampler.get_all_major_airports(large_only=True, scheduled_service_only=True)

        assert len(airports) == 2
        assert set(airports) == {"KJFK", "KLAX"}


class TestEvaluationService:
    """Tests for EvaluationService."""

    def test_compare_iwxxm_identical(self):
        """Test comparing identical IWXXM documents."""
        from src.services.evaluation_service import EvaluationService

        xml = '<?xml version="1.0"?><METAR><temp>15</temp></METAR>'
        service = EvaluationService()

        result = service.compare_iwxxm(xml, xml)

        assert result.passed is True
        assert result.our_elements == result.their_elements
        assert len(result.missing_elements) == 0
        assert len(result.extra_elements) == 0

    def test_compare_iwxxm_different(self):
        """Test comparing different IWXXM documents."""
        from src.services.evaluation_service import EvaluationService

        xml1 = '<?xml version="1.0"?><METAR><temp>15</temp></METAR>'
        xml2 = '<?xml version="1.0"?><METAR><temp>15</temp><dewpoint>10</dewpoint></METAR>'

        service = EvaluationService()
        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is False
        assert result.our_elements < result.their_elements

    def test_compare_iwxxm_strips_dynamic_attrs(self):
        """Test that dynamic attributes are stripped during comparison."""
        from src.services.evaluation_service import EvaluationService

        xml1 = '<?xml version="1.0"?><METAR id="uuid-123"><temp>15</temp></METAR>'
        xml2 = '<?xml version="1.0"?><METAR id="uuid-456"><temp>15</temp></METAR>'

        service = EvaluationService()
        result = service.compare_iwxxm(xml1, xml2)

        # Should pass since IDs are stripped
        assert result.passed is True

    def test_compare_iwxxm_invalid_xml(self):
        """Test handling of invalid XML."""
        from src.services.evaluation_service import EvaluationService

        xml1 = "not xml"
        xml2 = '<?xml version="1.0"?><METAR><temp>15</temp></METAR>'

        service = EvaluationService()
        result = service.compare_iwxxm(xml1, xml2)

        assert result.passed is False
        assert result.error_message is not None
        assert "parse error" in result.error_message.lower()


class TestAviationWeatherClient:
    """Tests for AviationWeatherClient."""

    @pytest.mark.asyncio
    async def test_fetch_metar_batch(self):
        """Test fetching METAR batch data."""
        from src.clients.aviation_weather_client import AviationWeatherClient

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock raw response
            raw_response = Mock()
            raw_response.text = "METAR KJFK 101851Z 24008KT 10SM FEW250 M04/M17 A3034"
            raw_response.raise_for_status = Mock()

            # Mock IWXXM response
            iwxxm_response = Mock()
            iwxxm_response.text = '<?xml version="1.0"?><METAR designator="KJFK">test</METAR>'
            iwxxm_response.raise_for_status = Mock()

            mock_client.get.side_effect = [raw_response, iwxxm_response]

            async with AviationWeatherClient() as client:
                result = await client.fetch_metar_batch(["KJFK"], hours=1.5)

            assert "KJFK" in result
            assert result["KJFK"][0] is not None  # Raw TAC
            assert result["KJFK"][1] is not None  # IWXXM

    @pytest.mark.asyncio
    async def test_fetch_metar_batch_handles_404(self):
        """Test handling of 404 responses."""
        import httpx

        from src.clients.aviation_weather_client import AviationWeatherClient

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock 404 response
            response = Mock()
            response.status_code = 404
            response.text = "Not found"
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "404", request=Mock(), response=response
            )

            async with AviationWeatherClient() as client:
                result = await client.fetch_metar_batch(["INVALID"], hours=1.5)

            # Should return dict with station and None values for 404
            assert result == {"INVALID": (None, None)}


@pytest.mark.asyncio
async def test_evaluation_endpoint_integration(mock_station_sampler, mock_aviation_weather_client, mock_evaluation_service):
    """Integration test for evaluation endpoint."""
    # This would be expanded with actual FastAPI TestClient usage
    # For now, just test the core logic

    from src.schemas.evaluation import EvaluationMode, EvaluationRequest

    request = EvaluationRequest(
        mode=EvaluationMode.RANDOM,
        sample_size=3,
        hours=1.5
    )

    # Verify request validates correctly
    assert request.mode == EvaluationMode.RANDOM
    assert request.sample_size == 3
    assert request.hours == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
