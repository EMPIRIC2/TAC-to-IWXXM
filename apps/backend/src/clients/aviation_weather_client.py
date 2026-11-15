"""Facade for ``aviation_weather_client.py`` (line-cap split)."""

from src.clients.aviation_weather_client_part_1 import (
    AviationWeatherAPIError,
)
from src.clients.aviation_weather_client_part_2 import (
    AviationWeatherClient,
)
from src.clients.aviation_weather_client_part_3 import (
    CachedAviationWeatherClient,
)

__all__ = [
    "AviationWeatherAPIError",
    "AviationWeatherClient",
    "CachedAviationWeatherClient",
]
