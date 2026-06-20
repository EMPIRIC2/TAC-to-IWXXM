"""
GIFTs LocationDB adapter - provides geolocation data in format GIFTs expects.

GIFTs encoder expects a dictionary-like object with:
- .get(icao_code) method returning "name|iata|designator|latitude,longitude"
"""

import logging
from typing import Optional

try:
    from ..services.openaip_service import OpenAIPService
except ImportError:
    from services.openaip_service import OpenAIPService

try:
    from .airport_record_builder import AirportRecordBuilder
except ImportError:
    from airport_record_builder import AirportRecordBuilder

try:
    from ..schemas.airport import get_airport_validator
except ImportError:
    from schemas.airport import get_airport_validator

logger = logging.getLogger(__name__)


class GiftsLocationDBAdapter:
    """
    Adapter providing airport location data in GIFTs-compatible format.

    This adapter bridges multiple airport data sources and presents them
    in the format required by GIFTs encoder.
    """

    def __init__(self, openaip_service: Optional[OpenAIPService] = None):
        """
        Initialize the adapter.

        Args:
            openaip_service: OpenAIPService instance (created if not provided)
        """
        self.openaip_service = openaip_service or OpenAIPService()
        self.record_builder = AirportRecordBuilder()
        self.airport_validator = None

        # Try to load airport validator (optional)
        try:
            self.airport_validator = get_airport_validator()
            logger.info("Loaded AirportValidator for fallback lookups")
        except Exception as e:
            logger.debug(f"AirportValidator not available: {e}")

    def get(self, icao_code: str) -> Optional[str]:
        """
        Get airport data in GIFTs format.

        Args:
            icao_code: 4-letter ICAO airport code

        Returns:
            String in format "name|iata|designator|lat,lon" or None if not found
        """
        icao = icao_code.upper().strip() if icao_code else None
        if not icao:
            return None

        # Get OpenAIP data if available
        openaip_data = self.openaip_service.get_airport(icao)

        # Build complete record from all sources
        record = self.record_builder.build_record(
            icao, openaip_data=openaip_data, airport_validator=self.airport_validator
        )

        # Convert to GIFTs format
        gifts_str = self.record_builder.get_gifts_format(record)

        if gifts_str:
            logger.debug(f"Found {icao}: {gifts_str[:50]}...")
            return gifts_str
        else:
            logger.warning(f"No complete airport data for {icao}")
            return None

    def validate_airport(self, icao_code: str) -> bool:
        """
        Check if airport exists.

        Args:
            icao_code: 4-letter ICAO code

        Returns:
            True if airport found in any data source
        """
        return self.get(icao_code) is not None

    def get_cached_airports(self) -> dict:
        """Get all cached airports from OpenAIP."""
        return self.openaip_service.get_all_airports()
