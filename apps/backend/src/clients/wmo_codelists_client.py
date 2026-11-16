"""Facade for ``wmo_codelists_client.py`` (line-cap split)."""

import sys
import types
from importlib import import_module

from . import wmo_codelists_client_part_1 as _part1
from . import wmo_codelists_client_part_2 as _part2
from .wmo_codelists_client_part_1 import (
    WMOCodelistCache,
    WMOCodelistInfo,
    logger,
)
from .wmo_codelists_client_part_2 import (
    CodeListParser,
    WMOCodelistsClient,
)


def _load_requests() -> tuple[object | None, bool]:
    try:
        return import_module("requests"), True
    except ImportError:  # pragma: no cover
        return None, False


requests, REQUESTS_AVAILABLE = _load_requests()

_part1.REQUESTS_AVAILABLE = REQUESTS_AVAILABLE
_part1.requests = requests
_part2.REQUESTS_AVAILABLE = REQUESTS_AVAILABLE
_part2.requests = requests


_ORIG: dict[str, object] = {}


class _WmoCodelistsModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in {"REQUESTS_AVAILABLE", "requests", "CodeListParser"}:
            setattr(_part1, name, value)
            if hasattr(_part2, name):
                setattr(_part2, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in _ORIG and hasattr(_part1, name):
            setattr(_part1, name, _ORIG[name])
        if name in _ORIG and hasattr(_part2, name):
            setattr(_part2, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _WmoCodelistsModule

__all__ = [
    "REQUESTS_AVAILABLE",
    "CodeListParser",
    "WMOCodelistCache",
    "WMOCodelistInfo",
    "WMOCodelistsClient",
    "logger",
    "requests",
]
