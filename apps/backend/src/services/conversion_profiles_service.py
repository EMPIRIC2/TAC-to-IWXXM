"""Facade for ``conversion_profiles_service.py`` (line-cap split)."""

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
    "logger",
]

import sys
import types

from . import conversion_profiles_service_part_1 as _part1

_ORIG: dict[str, object] = {}


# Populated lazily on first setattr for unknown sync sets
class _ConversionProfilesServiceModule(types.ModuleType):
    """Keep ``_engine`` assignments on the facade in sync with part_1."""

    def __setattr__(self, name: str, value: object) -> None:
        if name == "_engine":
            _part1._engine = value  # type: ignore[attr-defined]
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        super().__delattr__(name)


sys.modules[__name__].__class__ = _ConversionProfilesServiceModule
