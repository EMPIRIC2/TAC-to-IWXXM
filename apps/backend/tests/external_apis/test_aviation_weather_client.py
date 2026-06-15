"""Unit tests for aviation weather API client."""
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.clients.aviation_weather_client import AviationWeatherClient


@pytest.mark.unit
@pytest.mark.asyncio
class TestAviationWeatherClient:
    """Unit tests for AviationWeatherClient."""

    async def test_context_manager(self):
        """Test async context manager."""
        async with AviationWeatherClient() as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

    async def test_fetch_metar_batch_success(self):
        """Test successful METAR batch fetch."""
        async with AviationWeatherClient() as client:
            with patch.object(client._client, 'get', new_callable=AsyncMock) as mock_get:
                raw_response = Mock()
                raw_response.text = "METAR KJFK 101851Z 24008KT 10SM FEW250 M04/M17 A3034\nMETAR KLAX 101853Z 26010KT 10SM FEW015 16/12 A2990"
                raw_response.raise_for_status = Mock()

                iwxxm_response = Mock()
                iwxxm_response.text = '<?xml version="1.0"?><METAR designator="KJFK">test1</METAR>\n<?xml version="1.0"?><METAR designator="KLAX">test2</METAR>'
                iwxxm_response.raise_for_status = Mock()

                mock_get.side_effect = [raw_response, iwxxm_response]

                result = await client.fetch_metar_batch(["KJFK", "KLAX"], hours=1.5)

                assert len(result) == 2
                assert "KJFK" in result
                assert "KLAX" in result
                assert "24008KT" in result["KJFK"][0]
                assert "test1" in result["KJFK"][1]

    async def test_fetch_metar_batch_handles_404(self):
        """Test handling of 404 responses."""
        async with AviationWeatherClient() as client:
            with patch.object(client._client, 'get', new_callable=AsyncMock) as mock_get:
                response = Mock()
                response.status_code = 404
                response.text = "Not found"

                mock_get.side_effect = httpx.HTTPStatusError(
                    "404 Not Found",
                    request=Mock(),
                    response=response
                )

                result = await client.fetch_metar_batch(["INVALID"], hours=1.5)

                # Should return dict with station and None values for 404
                assert result == {"INVALID": (None, None)}

    async def test_fetch_metar_batch_request_error(self):
        """Test handling of request errors."""
        async with AviationWeatherClient() as client:
            with patch.object(client._client, 'get', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = httpx.RequestError("Connection failed")

                # Request errors are returned as empty dict (exception caught in parallel gather)
                result = await client.fetch_metar_batch(["KJFK"], hours=1.5)
                assert result == {"KJFK": (None, None)}

    async def test_extract_station_from_xml_designator(self):
        """Test extracting station ID from XML with designator attribute."""
        client = AviationWeatherClient()

        xml = '<?xml version="1.0"?><METAR designator="KJFK">content</METAR>'

        station_id = client._extract_station_from_xml(xml)

        assert station_id == "KJFK"

    async def test_extract_station_from_xml_not_found(self):
        """Test extraction returns None when station not found."""
        client = AviationWeatherClient()

        xml = '<METAR>no station info</METAR>'

        station_id = client._extract_station_from_xml(xml)

        assert station_id is None

    async def test_parse_response_raw_format(self):
        """Test parsing raw format response."""
        client = AviationWeatherClient()

        content = "METAR KJFK 101851Z 24008KT 10SM FEW250 M04/M17 A3034\nMETAR KLAX 101853Z 26010KT 10SM FEW015 16/12 A2990"

        result = client._parse_response(content, "raw", ["KJFK", "KLAX"])

        assert len(result) == 2
        assert "KJFK" in result
        assert "KLAX" in result
        assert "24008KT" in result["KJFK"]

    async def test_parse_response_iwxxm_format(self):
        """Test parsing IWXXM format response."""
        client = AviationWeatherClient()

        content = '<?xml version="1.0"?><METAR designator="KJFK">test1</METAR>\n<?xml version="1.0"?><METAR designator="KLAX">test2</METAR>'

        result = client._parse_response(content, "iwxxm", ["KJFK", "KLAX"])

        assert len(result) == 2
        assert "test1" in result["KJFK"]
        assert "test2" in result["KLAX"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit and asyncio"])
