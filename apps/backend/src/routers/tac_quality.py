"""Facade for ``tac_quality.py`` (line-cap split)."""

import sys
import types

from . import tac_quality_part_2 as _part2
from .tac_quality_part_1 import (
    _advisory_explanation,
    _DecodedResidual,
    _DecodedRow,
    _enrich_advisory_decode,
    _ensure_airport_location_resolver,
    _location_resolver_ready,
    decode_tac_endpoint,
    lint_issue_catalog,
    router,
)
from .tac_quality_part_2 import (
    get_airport_validator,
    lint_tac,
    station_point,
)

_SYNC = {"get_airport_validator"}
_ORIG: dict[str, object] = {}
for _n in _SYNC:
    if hasattr(_part2, _n):
        _ORIG.setdefault(_n, getattr(_part2, _n))


class _TacQualityModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in _SYNC and hasattr(_part2, name):
            setattr(_part2, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        super().__delattr__(name)


sys.modules[__name__].__class__ = _TacQualityModule

__all__ = [
    "_DecodedResidual",
    "_DecodedRow",
    "_advisory_explanation",
    "_enrich_advisory_decode",
    "_ensure_airport_location_resolver",
    "_location_resolver_ready",
    "decode_tac_endpoint",
    "get_airport_validator",
    "lint_issue_catalog",
    "lint_tac",
    "router",
    "station_point",
]
