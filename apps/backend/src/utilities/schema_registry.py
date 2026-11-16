"""Facade for ``schema_registry.py`` (line-cap split)."""

import sys
import types

from ..config.iwxxm_versions import (
    SUPPORTED_VERSIONS,
    get_all_versions_with_metadata,
    get_breaking_changes,
    get_namespace_uri,
    get_schema_url,
    get_version_channel,
    get_version_config,
    get_version_discovery_date,
    get_versions_by_channel,
    is_rc_version,
    normalize_version,
    resolve_schema_file,
)
from . import schema_registry_part_2 as _part2
from . import schema_registry_part_3 as _part3
from .schema_registry_part_1 import (
    logger,
)
from .schema_registry_part_2 import (
    SchemaRegistry,
)
from .schema_registry_part_3 import (
    _registry_instance,
    clear_registry_cache,
    get_schema_registry,
)

_SYNC_NAMES = {
    "SUPPORTED_VERSIONS",
    "get_all_versions_with_metadata",
    "get_breaking_changes",
    "get_namespace_uri",
    "get_schema_url",
    "get_version_channel",
    "get_version_config",
    "get_version_discovery_date",
    "get_versions_by_channel",
    "is_rc_version",
    "normalize_version",
    "resolve_schema_file",
}


_ORIG: dict[str, object] = {}
for _n in _SYNC_NAMES:
    for _mod in (
        _part2,
        _part3,
    ):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _SchemaRegistryModule(types.ModuleType):
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
        if name in _SYNC_NAMES:
            setattr(_part2, name, value)
        elif name == "_registry_instance":
            _part3._registry_instance = value  # type: ignore[attr-defined]
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """
        Internal helper ``__delattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        """
        if name in _ORIG and hasattr(_part2, name):
            setattr(_part2, name, _ORIG[name])
        if name in _ORIG and hasattr(_part3, name):
            setattr(_part3, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _SchemaRegistryModule

__all__ = [
    "SUPPORTED_VERSIONS",
    "SchemaRegistry",
    "_registry_instance",
    "clear_registry_cache",
    "get_all_versions_with_metadata",
    "get_breaking_changes",
    "get_namespace_uri",
    "get_schema_registry",
    "get_schema_url",
    "get_version_channel",
    "get_version_config",
    "get_version_discovery_date",
    "get_versions_by_channel",
    "is_rc_version",
    "logger",
    "normalize_version",
    "resolve_schema_file",
]
