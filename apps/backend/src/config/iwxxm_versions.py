"""Facade for ``iwxxm_versions.py`` (line-cap split)."""

import sys
import types

from . import iwxxm_versions_part_1 as _part1
from . import iwxxm_versions_part_2 as _part2
from .iwxxm_versions_part_1 import (
    ALL_VERSIONS,
    DEFAULT_VERSION,
    DEPRECATED_VERSIONS,
    PROFILE_SCOPED_VERSIONS,
    PROJECT_ROOT,
    RC_VERSIONS,
    SUPPORTED_MIGRATE_PAIRS,
    SUPPORTED_VERSIONS,
    SUPPORTED_VERSIONS_BY_CHANNEL,
    VALID_VERSION_STRINGS,
    VERSION_DISCOVERY_METADATA,
    VERSION_REMAPPING,
    VersionDeprecatedError,
    _detect_project_root,
    _local_schema_base,
    _versioned_schema_dir,
    get_supported_versions,
    get_version_config,
    get_version_discovery_date,
    is_migration_supported,
    normalize_version,
)
from .iwxxm_versions_part_2 import (
    get_all_versions_with_metadata,
    get_breaking_changes,
    get_namespace_uri,
    get_schema_url,
    get_version_channel,
    get_version_config_for_emit_profile,
    get_versions_by_channel,
    is_rc_version,
    is_version_supported,
    register_rc_version,
    resolve_schema_file,
)

__all__ = [
    "ALL_VERSIONS",
    "DEFAULT_VERSION",
    "DEPRECATED_VERSIONS",
    "PROFILE_SCOPED_VERSIONS",
    "PROJECT_ROOT",
    "RC_VERSIONS",
    "SUPPORTED_MIGRATE_PAIRS",
    "SUPPORTED_VERSIONS",
    "SUPPORTED_VERSIONS_BY_CHANNEL",
    "VALID_VERSION_STRINGS",
    "VERSION_DISCOVERY_METADATA",
    "VERSION_REMAPPING",
    "VersionDeprecatedError",
    "_detect_project_root",
    "_local_schema_base",
    "_versioned_schema_dir",
    "get_all_versions_with_metadata",
    "get_breaking_changes",
    "get_namespace_uri",
    "get_schema_url",
    "get_supported_versions",
    "get_version_channel",
    "get_version_config",
    "get_version_config_for_emit_profile",
    "get_version_discovery_date",
    "get_versions_by_channel",
    "is_migration_supported",
    "is_rc_version",
    "is_version_supported",
    "normalize_version",
    "register_rc_version",
    "resolve_schema_file",
]


_SYNC = {
    "PROJECT_ROOT",
    "VERSION_REMAPPING",
    "RC_VERSIONS",
    "SUPPORTED_VERSIONS",
    "get_version_config",
}


_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (
        _part1,
        _part2,
    ):
        if _mod is not None and hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _IwxxmVersionsModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name == "__file__":
            # Keep part_1 Path(__file__) fallbacks and detectors in sync for tests.
            object.__setattr__(self, name, value)
            return
        if name in _SYNC:
            setattr(_part1, name, value)
            if hasattr(_part2, name):
                setattr(_part2, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        super().__delattr__(name)


sys.modules[__name__].__class__ = _IwxxmVersionsModule
