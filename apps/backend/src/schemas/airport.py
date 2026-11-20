"""HTTP schema adapters for airport (re-export from ``src.models``)."""

from src.models.airport import (
    _AIRPORT_DATA_DIR,
    Airport,
    AirportCoordinates,
    AirportValidator,
    get_airport_validator,
    reset_airport_validator_for_tests,
)

__all__ = [
    "_AIRPORT_DATA_DIR",
    "Airport",
    "AirportCoordinates",
    "AirportValidator",
    "get_airport_validator",
    "reset_airport_validator_for_tests",
]
