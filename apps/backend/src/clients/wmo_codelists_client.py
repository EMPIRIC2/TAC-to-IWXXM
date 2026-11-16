"""Facade for ``wmo_codelists_client.py`` (line-cap split)."""

import sys
import types
from typing import Any

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


def _load_requests() -> tuple[Any, bool]:
    """
    Internal helper ``_load_requests``.

    Returns
    -------
    object
        Return value.
    """
    # Statement import so builtins.__import__ monkeypatches still work;
    # importlib.import_module bypasses that hook.
    try:
        import requests as requests_mod

        return requests_mod, True
    except ImportError:
        return None, False


requests, REQUESTS_AVAILABLE = _load_requests()

_part1.REQUESTS_AVAILABLE = REQUESTS_AVAILABLE
_part1.requests = requests
_part2.REQUESTS_AVAILABLE = REQUESTS_AVAILABLE
_part2.requests = requests


_ORIG: dict[str, object] = {}


class _WmoCodelistsModule(types.ModuleType):
    """Sync facade attribute patches into split part modules."""

    def __setattr__(self, name: str, value: object) -> None:
        """
        Internal helper ``__setattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        value : object
            Argument ``value``.
        """
        if name in {"REQUESTS_AVAILABLE", "requests", "CodeListParser"}:
            setattr(_part1, name, value)
            if hasattr(_part2, name):
                setattr(_part2, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """
        Internal helper ``__delattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        """
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
