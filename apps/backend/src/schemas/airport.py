"""HTTP schema adapters for airport (re-export from ``src.models``)."""

from src.models.airport import (
    Airport,
    AirportCoordinates,
    AirportValidator,
    get_airport_validator,
)

__all__ = [
    "Airport",
    "AirportCoordinates",
    "AirportValidator",
    "get_airport_validator",
]
