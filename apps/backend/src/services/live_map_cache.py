"""Facade for ``live_map_cache.py`` (line-cap split)."""

import sys
import types
from datetime import UTC, datetime, timedelta

from . import live_map_cache_part_1 as _part1
from . import live_map_cache_part_2 as _part2
from .live_map_cache_part_1 import (
    _KEEP,
    RETENTION_HOURS,
    LiveMapReport,
    _cache_url,
    _geometry,
    _geometry_json,
    _geometry_kind,
    _id,
    _issues,
    _issues_json,
    _iwxxm,
    _latitude,
    _longitude,
    _metadata,
    _observed_at,
    _place_key,
    _PlaceJson,
    _product,
    _radius_m,
    _ReportJson,
    _stamp,
    _tac,
    _translation_status,
    _utc_now,
    engine_for_url,
    live_map_reports,
    retention_cutoff,
)
from .live_map_cache_part_2 import (
    LiveMapCache,
    apply_refresh,
    cache_from_env,
)

_SYNC = {"datetime", "UTC", "timedelta"}
_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (_part1, _part2):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


# Populated lazily on first setattr for unknown sync sets
class _LiveMapCacheModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in _SYNC:
            setattr(_part1, name, value)
            if hasattr(_part2, name):
                setattr(_part2, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        super().__delattr__(name)


sys.modules[__name__].__class__ = _LiveMapCacheModule

__all__ = [
    "RETENTION_HOURS",
    "UTC",
    "_KEEP",
    "LiveMapCache",
    "LiveMapReport",
    "_PlaceJson",
    "_ReportJson",
    "_cache_url",
    "_geometry",
    "_geometry_json",
    "_geometry_kind",
    "_id",
    "_issues",
    "_issues_json",
    "_iwxxm",
    "_latitude",
    "_longitude",
    "_metadata",
    "_observed_at",
    "_place_key",
    "_product",
    "_radius_m",
    "_stamp",
    "_tac",
    "_translation_status",
    "_utc_now",
    "apply_refresh",
    "cache_from_env",
    "datetime",
    "engine_for_url",
    "live_map_reports",
    "retention_cutoff",
    "timedelta",
]
