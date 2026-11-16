"""Facade for ``conversion_profiles_service.py`` (line-cap split)."""

import sys
import types

from sqlalchemy import MetaData, Table, create_engine, delete, insert, or_, select, update

from . import conversion_profiles_service_part_1 as _part1
from .conversion_profiles_service_part_1 import (
    _SECRET_KEY,
    _URI_VALUE,
    CONVERSION_TEMPLATES_TABLE,
    LIBRARY_ASSETS_TABLE,
    OVERLAYS_TABLE,
    PRESETS_TABLE,
    RULE_PACKS_TABLE,
    TEMPLATES_TABLE,
    _engine,
    _get_engine,
    _handle_db_error,
    _metadata,
    _preset_row_to_out,
    _reject_secrets,
    _reject_template_values,
    _row_to_out,
    _sync_database_url,
    _table,
    _tables,
    _template_row_to_out,
    logger,
)
from .conversion_profiles_service_part_2 import (
    ConversionProfilesService,
)

_SYNC = {
    "Table",
    "MetaData",
    "create_engine",
    "delete",
    "insert",
    "or_",
    "select",
    "update",
    "_engine",
    "_get_engine",
    "_table",
    "_handle_db_error",
}
_ORIG: dict[str, object] = {}
for _n in _SYNC:
    if hasattr(_part1, _n):
        _ORIG.setdefault(_n, getattr(_part1, _n))


class _ConversionProfilesServiceModule(types.ModuleType):
    """Keep facade patches in sync with part_1 call sites."""

    def __setattr__(self, name: str, value: object) -> None:
        if (name == "_engine" or name in _SYNC) and hasattr(_part1, name):
            setattr(_part1, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in _ORIG and hasattr(_part1, name):
            setattr(_part1, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _ConversionProfilesServiceModule

__all__ = [
    "CONVERSION_TEMPLATES_TABLE",
    "LIBRARY_ASSETS_TABLE",
    "OVERLAYS_TABLE",
    "PRESETS_TABLE",
    "RULE_PACKS_TABLE",
    "TEMPLATES_TABLE",
    "_SECRET_KEY",
    "_URI_VALUE",
    "ConversionProfilesService",
    "MetaData",
    "Table",
    "_engine",
    "_get_engine",
    "_handle_db_error",
    "_metadata",
    "_preset_row_to_out",
    "_reject_secrets",
    "_reject_template_values",
    "_row_to_out",
    "_sync_database_url",
    "_table",
    "_tables",
    "_template_row_to_out",
    "create_engine",
    "delete",
    "insert",
    "logger",
    "or_",
    "select",
    "update",
]
