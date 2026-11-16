"""Facade for ``schema_mirror_service.py`` (line-cap split)."""

import httpx

from .schema_mirror_service_part_1 import (
    SchemaMirrorService,
    logger,
)
from .schema_mirror_service_part_2 import (
    mirror_schema_version,
)

__all__ = [
    "SchemaMirrorService",
    "httpx",
    "logger",
    "mirror_schema_version",
]

import sys
import types

from . import schema_mirror_service_part_1 as _part1

try:
    from . import schema_mirror_service_part_2 as _part2
except ImportError:  # pragma: no cover
    _part2 = None


_ORIG: dict[str, object] = {}


# Populated lazily on first setattr for unknown sync sets
class _SchemaMirrorServiceModule(types.ModuleType):
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
        if name == "httpx":
            if hasattr(_part1, "httpx"):
                _part1.httpx = value
            if _part2 is not None and hasattr(_part2, "httpx"):
                _part2.httpx = value  # type: ignore[attr-defined]
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


sys.modules[__name__].__class__ = _SchemaMirrorServiceModule
