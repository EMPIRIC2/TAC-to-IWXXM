"""Facade for ``schema_discovery_poller.py`` (line-cap split)."""

import asyncio
import re
import sys
import types

import httpx

from . import schema_discovery_poller_part_1 as _part1
from . import schema_discovery_poller_part_2 as _part2
from .schema_discovery_poller_part_1 import (
    RC_PATTERN,
    VERSION_PATTERN,
    WMO_SCHEMA_DIRECTORIES,
    VersionCallback,
    extract_version_from_url,
    logger,
)
from .schema_discovery_poller_part_2 import (
    SchemaDiscoveryPoller,
    analyze_xmi_versions,
)
from .schema_discovery_poller_part_3 import (
    discover_schemas,
    discover_schemas_with_retry,
)

_SYNC = {
    "RC_PATTERN",
    "VERSION_PATTERN",
    "analyze_xmi_versions",
    "asyncio",
    "httpx",
    "re",
    "SUPPORTED_VERSIONS",
}


_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (
        _part1,
        _part2,
    ):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _SchemaDiscoveryPollerModule(types.ModuleType):
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
        if name in _SYNC:
            if hasattr(_part1, name):
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


sys.modules[__name__].__class__ = _SchemaDiscoveryPollerModule

__all__ = [
    "RC_PATTERN",
    "VERSION_PATTERN",
    "WMO_SCHEMA_DIRECTORIES",
    "SchemaDiscoveryPoller",
    "VersionCallback",
    "analyze_xmi_versions",
    "asyncio",
    "discover_schemas",
    "discover_schemas_with_retry",
    "extract_version_from_url",
    "httpx",
    "logger",
    "re",
]
