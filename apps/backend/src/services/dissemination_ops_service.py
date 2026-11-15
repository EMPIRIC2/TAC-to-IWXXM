"""Facade for ``dissemination_ops_service.py`` (line-cap split)."""

from src.services.dissemination_ops_service_part_1 import (
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
from src.services.dissemination_ops_service_part_2 import (
    DisseminationOpsService,
)

__all__ = [
    "AUDIT_TABLE",
    "MAPPINGS_TABLE",
    "PLANS_TABLE",
    "_SECRET_KEY",
    "DisseminationOpsService",
    "_engine",
    "_get_engine",
    "_handle_db_error",
    "_metadata",
    "_raise_db",
    "_reject_secrets",
    "_sync_database_url",
    "_table",
    "_tables",
    "logger",
]
