"""Facade for ``dissemination_ops_service.py`` (line-cap split)."""

import sys
import types

from sqlalchemy import MetaData, Table, create_engine, insert, select

from . import dissemination_ops_service_part_1 as _part1
from . import dissemination_ops_service_part_2 as _part2
from .dissemination_ops_service_part_1 import (
    _SECRET_KEY,
    AUDIT_TABLE,
    MAPPINGS_TABLE,
    PLANS_TABLE,
    _engine,
    _get_engine,
    _handle_db_error,
    _metadata,
    _raise_db,
    _reject_secrets,
    _sync_database_url,
    _table,
    _tables,
    logger,
)
from .dissemination_ops_service_part_2 import (
    DisseminationOpsService,
)

_ORIG: dict[str, object] = {}


# Populated lazily on first setattr for unknown sync sets
class _DisseminationOpsModule(types.ModuleType):
    def __setattr__(self, name: str, value: object) -> None:
        if name == "_engine":
            _part1._engine = value  # type: ignore[attr-defined]
        elif name in {"insert", "select"}:
            setattr(_part2, name, value)
        elif name in {"Table", "create_engine", "MetaData"}:
            setattr(_part1, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        super().__delattr__(name)


sys.modules[__name__].__class__ = _DisseminationOpsModule

__all__ = [
    "AUDIT_TABLE",
    "MAPPINGS_TABLE",
    "PLANS_TABLE",
    "_SECRET_KEY",
    "DisseminationOpsService",
    "MetaData",
    "Table",
    "_engine",
    "_get_engine",
    "_handle_db_error",
    "_metadata",
    "_raise_db",
    "_reject_secrets",
    "_sync_database_url",
    "_table",
    "_tables",
    "create_engine",
    "insert",
    "logger",
    "select",
]
