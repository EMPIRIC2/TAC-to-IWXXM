"""Part 1 of ``dissemination_ops_service.py`` (line-cap split)."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, NoReturn, cast

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

PLANS_TABLE = "tac_dissemination_plans"

AUDIT_TABLE = "tac_dissemination_audit"

MAPPINGS_TABLE = "tac_mapping_configs"

_SECRET_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|uri|connection_string|dsn)")

_engine: Engine | None = None

_metadata = MetaData()

_tables: dict[str, Table] = {}


def _sync_database_url() -> str:
    """
    Internal helper ``_sync_database_url``.

    Returns
    -------
    object
        Return value.
    """
    raw = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dissemination ops unavailable - missing DATABASE_URL",
        )
    if raw.startswith("postgresql+asyncpg://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    elif raw.startswith("postgresql+psycopg2://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    elif raw.startswith("postgresql://"):
        url = "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    else:
        url = raw
    if "ssl=require" in url and "sslmode=" not in url:
        url = url.replace("ssl=require", "sslmode=require")
    return url


def _get_engine() -> Engine:
    """
    Internal helper ``_get_engine``.

    Returns
    -------
    object
        Return value.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    return _engine


def _table(name: str) -> Table:
    """
    Internal helper ``_table``.

    Parameters
    ----------
    name : object
        Argument ``name``.

    Returns
    -------
    object
        Return value.
    """
    if name not in _tables:
        _tables[name] = Table(name, _metadata, autoload_with=_get_engine())
    return _tables[name]


def _reject_secrets(payload: dict[str, Any], *, path: str = "") -> None:
    """
    Internal helper ``_reject_secrets``.

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    path : object
        Argument ``path``.
    """
    for key, value in payload.items():
        full = f"{path}.{key}" if path else key
        if _SECRET_KEY.search(key):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Field not allowed in dissemination ops persistence: {full}",
            )
        if isinstance(value, dict):
            nested = cast(dict[str, Any], value)
            _reject_secrets(nested, path=full)
        elif isinstance(value, list):
            items = cast(list[Any], value)
            for i, item in enumerate(items):
                if isinstance(item, dict):
                    child = cast(dict[str, Any], item)
                    _reject_secrets(child, path=f"{full}[{i}]")


def _handle_db_error(exc: Exception) -> NoReturn:
    """
    Internal helper ``_handle_db_error``.

    Parameters
    ----------
    exc : object
        Argument ``exc``.

    Returns
    -------
    object
        Return value.
    """
    logger.exception("dissemination ops db error: %s", exc)
    if isinstance(exc, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict saving dissemination ops row",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Dissemination ops database error",
    ) from exc


def _raise_db(exc: Exception) -> NoReturn:
    """
    Internal helper ``_raise_db``.

    Parameters
    ----------
    exc : object
        Argument ``exc``.

    Returns
    -------
    object
        Return value.
    """
    _handle_db_error(exc)
