"""Pydantic schemas and validators for airport ICAO codes."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AirportCoordinates(BaseModel):
    """Geographic coordinates for an airport."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": -26.140081,
                "longitude": 28.246801,
                "elevation_ft": 5558,
                "vertical_datum": "EGM_96",
            }
        }
    )

    latitude: float = Field(..., description="Latitude in decimal degrees", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude in decimal degrees", ge=-180, le=180)
    elevation_ft: Optional[int] = Field(None, description="Elevation in feet", ge=-1500)
    vertical_datum: Optional[str] = Field(
        "EGM_96", description="Vertical datum for elevation (EGM_96, NAVD88, AHD, etc.)"
    )


class Airport(BaseModel):
    """Airport data model with ICAO and metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "icao": "KJFK",
                "iata": "JFK",
                "name": "John F Kennedy International Airport",
                "city": "New York",
                "country": "United States",
                "type": "large_airport",
                "coordinates": {
                    "latitude": 40.63975111,
                    "longitude": -73.77892556,
                    "elevation_ft": 13,
                },
            }
        }
    )

    icao: str = Field(
        ...,
        description="ICAO airport code (4 characters)",
        min_length=4,
        max_length=4,
        examples=["KJFK", "EGLL", "FAOR"],
    )
    iata: Optional[str] = Field(
        None,
        description="IATA airport code (3 characters)",
        min_length=3,
        max_length=3,
        examples=["JFK", "LHR", "JNB"],
    )
    name: str = Field(..., description="Full airport name", min_length=1)
    city: Optional[str] = Field(None, description="City or municipality")
    country: Optional[str] = Field(None, description="Country name")
    type: str = Field(
        ...,
        description="Airport type",
        examples=["large_airport", "medium_airport", "small_airport", "heliport"],
    )
    coordinates: Optional[AirportCoordinates] = Field(None, description="Geographic coordinates")

    @field_validator("icao")
    @classmethod
    def validate_icao_format(cls, v: str) -> str:
        """Validate ICAO code format: 4 uppercase alphanumeric characters."""
        if not re.match(r"^[A-Z0-9]{4}$", v.upper()):
            raise ValueError(f"ICAO code must be 4 uppercase alphanumeric characters, got: {v}")
        return v.upper()

    @field_validator("iata")
    @classmethod
    def validate_iata_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate IATA code format: 3 uppercase alphanumeric characters."""
        if v is None:
            return None
        if not re.match(r"^[A-Z0-9]{3}$", v.upper()):
            raise ValueError(f"IATA code must be 3 uppercase alphanumeric characters, got: {v}")
        return v.upper()


class AirportValidator:
    """
    Singleton validator for airport ICAO codes.

    Loads airport data from airports.json and provides validation methods.
    """

    _instance: Optional[AirportValidator] = None
    _airports: dict[str, Airport] = {}
    _loaded: bool = False

    def __new__(cls) -> AirportValidator:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize validator (loads data on first instantiation)."""
        if not self._loaded:
            self.load_airports()

    def load_airports(self) -> None:
        """Load airports from airports.json into memory."""
        # Determine path to airports.json relative to this file
        current_file = Path(__file__)
        data_path = current_file.parent.parent / "data" / "airports.json"

        if not data_path.exists():
            raise FileNotFoundError(
                f"Airport data not found at {data_path}. Please run: python scripts/parse_airports_csv.py"
            )

        with open(data_path, "r", encoding="utf-8") as f:
            airports_data = json.load(f)

        # Build lookup map (case-insensitive)
        self._airports.clear()
        for airport_data in airports_data:
            try:
                airport = Airport(**airport_data)
                self._airports[airport.icao.upper()] = airport
            except Exception as e:
                # Skip invalid airport entries
                print(f"Warning: Failed to load airport {airport_data.get('icao', 'UNKNOWN')}: {e}")
                continue

        self._loaded = True
        print(f"Loaded {len(self._airports)} airports for validation")

    def validate_icao(self, icao_code: str) -> bool:
        """
        Check if an ICAO code is valid.

        Args:
            icao_code: ICAO code to validate (case-insensitive)

        Returns:
            True if valid, False otherwise
        """
        if not icao_code:
            return False
        # Validate format: exactly 4 uppercase letters
        if len(icao_code) != 4 or not icao_code.isalpha():
            return False
        return icao_code.upper() in self._airports

    def get_airport(self, icao_code: str) -> Optional[Airport]:
        """
        Get airport data for an ICAO code.

        Args:
            icao_code: ICAO code to look up (case-insensitive)

        Returns:
            Airport object if found, None otherwise
        """
        if not icao_code:
            return None
        return self._airports.get(icao_code.upper())

    def search_by_prefix(self, prefix: str, limit: int = 10) -> list[Airport]:
        """
        Search airports by ICAO code prefix.

        Args:
            prefix: ICAO code prefix (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching airports
        """
        if not prefix:
            return []

        prefix_upper = prefix.upper()
        matches = [airport for icao, airport in self._airports.items() if icao.startswith(prefix_upper)]
        return matches[:limit]

    def search_by_name(self, query: str, limit: int = 10) -> list[Airport]:
        """
        Search airports by name or city (case-insensitive).

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching airports
        """
        if not query:
            return []

        query_lower = (query or "").lower()
        matches = [
            airport
            for airport in self._airports.values()
            if query_lower in (airport.name or "").lower() or query_lower in (airport.city or "").lower()
        ]
        return matches[:limit]

    def get_all_airports(self) -> list[Airport]:
        """Get all loaded airports."""
        return list(self._airports.values())

    def count(self) -> int:
        """Get count of loaded airports."""
        return len(self._airports)


# Global validator instance
_validator_instance: Optional[AirportValidator] = None


def get_airport_validator() -> AirportValidator:
    """
    Get the global AirportValidator instance.

    Returns:
        Singleton AirportValidator instance
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = AirportValidator()
    return _validator_instance
