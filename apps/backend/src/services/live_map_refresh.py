"""Facade for ``live_map_refresh.py`` (line-cap split)."""

import sys
import types

from . import live_map_refresh_part_1 as _part1
from . import live_map_refresh_part_2 as _part2
from .live_map_refresh_part_1 import (
    REFRESH_TILES,
    _mapping,
    _number,
    _observed_at,
    _pairs,
    _point,
    _product,
    _report_from_row,
    _sequence,
    _tasks,
    _text,
    convert_mod,
    fetch_bbox,
    import_limit,
    logger,
    pause_seconds,
    reports_from_feed,
    stop_live_map_refresh,
    translate_report,
)
from .live_map_refresh_part_2 import (
    refresh_one,
    refresh_region,
    refresh_until,
    start_live_map_refresh,
)

_SYNC = {
    "convert_mod",
    "translate_report",
    "fetch_bbox",
    "import_limit",
    "pause_seconds",
    "reports_from_feed",
    "REFRESH_TILES",
}


_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (
        _part1,
        _part2,
    ):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _LiveMapRefreshModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in _SYNC:
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


sys.modules[__name__].__class__ = _LiveMapRefreshModule

__all__ = [
    "REFRESH_TILES",
    "_mapping",
    "_number",
    "_observed_at",
    "_pairs",
    "_point",
    "_product",
    "_report_from_row",
    "_sequence",
    "_tasks",
    "_text",
    "convert_mod",
    "fetch_bbox",
    "import_limit",
    "logger",
    "pause_seconds",
    "refresh_one",
    "refresh_region",
    "refresh_until",
    "reports_from_feed",
    "start_live_map_refresh",
    "stop_live_map_refresh",
    "translate_report",
]
