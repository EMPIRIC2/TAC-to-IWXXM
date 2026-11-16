"""Facade for ``observability.py`` (line-cap split)."""

import queue
import sys
import types

from . import observability_part_1 as _part1
from . import observability_part_2 as _part2
from .observability_part_1 import (
    _ALLOWED_LOG_LEVELS,
    _JWT_RE,
    _METRICS,
    _REQUEST_LOG_LEVEL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    METAR_CONVERSION_DURATION_SECONDS,
    METAR_CONVERSIONS_TOTAL,
    TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL,
    TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL,
    TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL,
    JsonLogFormatter,
    LokiHandler,
    _get_or_create_counter,
    _get_or_create_histogram,
    _metric_profile_id,
    record_profile_wire_metrics,
    record_translation_metric,
)
from .observability_part_2 import (
    _AUTH_RE,
    _REQUEST_LOGGERS,
    RequestLogLevelFilter,
    SecretRedactFilter,
    _filters_installed,
    _reset_request_log_level,
    ensure_request_log_filters,
    install_fastapi_observability,
    set_request_log_level,
    setup_logging,
)

_SYNC = {
    "queue",
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "METAR_CONVERSIONS_TOTAL",
    "METAR_CONVERSION_DURATION_SECONDS",
    "TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL",
    "TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL",
    "TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL",
    "LokiHandler",
    "record_translation_metric",
    "record_profile_wire_metrics",
}


_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (
        _part1,
        _part2,
    ):
        if _mod is not None and hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _ObservabilityModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name in _SYNC:
            if hasattr(_part1, name):
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


sys.modules[__name__].__class__ = _ObservabilityModule

__all__ = [
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "METAR_CONVERSIONS_TOTAL",
    "METAR_CONVERSION_DURATION_SECONDS",
    "TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL",
    "TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL",
    "TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL",
    "_ALLOWED_LOG_LEVELS",
    "_AUTH_RE",
    "_JWT_RE",
    "_METRICS",
    "_REQUEST_LOGGERS",
    "_REQUEST_LOG_LEVEL",
    "JsonLogFormatter",
    "LokiHandler",
    "RequestLogLevelFilter",
    "SecretRedactFilter",
    "_filters_installed",
    "_get_or_create_counter",
    "_get_or_create_histogram",
    "_metric_profile_id",
    "_reset_request_log_level",
    "ensure_request_log_filters",
    "install_fastapi_observability",
    "queue",
    "record_profile_wire_metrics",
    "record_translation_metric",
    "set_request_log_level",
    "setup_logging",
]
