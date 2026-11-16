"""Facade for ``aviation_weather_client.py`` (line-cap split)."""

import asyncio
import sys
import types

import httpx

from . import aviation_weather_client_part_2 as _part2
from . import aviation_weather_client_part_3 as _part3
from .aviation_weather_client_part_1 import (
    AviationWeatherAPIError,
)
from .aviation_weather_client_part_2 import (
    AviationWeatherClient,
)
from .aviation_weather_client_part_3 import (
    CachedAviationWeatherClient,
)

_ORIG: dict[str, object] = {}


# Populated lazily on first setattr for unknown sync sets
class _AviationWeatherClientModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in {"httpx", "asyncio"}:
            for mod in (_part2, _part3):
                if hasattr(mod, name):
                    setattr(mod, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in _ORIG and hasattr(_part2, name):
            setattr(_part2, name, _ORIG[name])
        if name in _ORIG and hasattr(_part3, name):
            setattr(_part3, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _AviationWeatherClientModule

__all__ = [
    "AviationWeatherAPIError",
    "AviationWeatherClient",
    "CachedAviationWeatherClient",
    "asyncio",
    "httpx",
]
