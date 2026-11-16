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

_SYNC = {"_engine", "insert", "select", "Table", "create_engine", "MetaData"}
_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (_part1, _part2):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


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
        if name in _ORIG and hasattr(_part1, name):
            setattr(_part1, name, _ORIG[name])
        if name in _ORIG and hasattr(_part2, name):
            setattr(_part2, name, _ORIG[name])
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
