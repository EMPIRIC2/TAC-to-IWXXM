"""Part 1 of ``conversion_profiles_service.py`` (line-cap split)."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, NoReturn, cast

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from ..schemas.conversion_profiles import (
    DisseminationTemplateOut,
    PresetOut,
    RulePackOut,
)

logger = logging.getLogger(__name__)

RULE_PACKS_TABLE = "tac_profile_rule_packs"

OVERLAYS_TABLE = "tac_profile_overlays"

PRESETS_TABLE = "tac_profile_presets"

TEMPLATES_TABLE = "tac_dissemination_templates"

CONVERSION_TEMPLATES_TABLE = "tac_conversion_templates"

LIBRARY_ASSETS_TABLE = "tac_library_assets"

_SECRET_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|uri|connection_string|dsn)")

_URI_VALUE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)

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
            detail="Profile rule packs unavailable - missing DATABASE_URL",
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
                detail=f"Field not allowed in profile persistence: {full}",
            )
        if isinstance(value, dict):
            nested = cast(dict[str, Any], value)
            _reject_secrets(nested, path=full)


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
    logger.exception("conversion profiles db error: %s", exc)
    if isinstance(exc, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict saving profile row",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile storage unavailable",
    ) from exc


def _row_to_out(row: dict[str, Any]) -> RulePackOut:
    """
    Internal helper ``_row_to_out``.

    Parameters
    ----------
    row : object
        Argument ``row``.

    Returns
    -------
    object
        Return value.
    """
    return RulePackOut(
        id=row["id"],
        user_id=row["user_id"],
        slug=row["slug"],
        profile=row["profile"],
        product=row["product"],
        stage=row["stage"],
        severity=row["severity"],
        when_expr=str(row.get("when_expr") or ""),
        message=str(row.get("message") or ""),
        standard_reference=str(row.get("standard_reference") or ""),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _preset_row_to_out(row: dict[str, Any]) -> PresetOut:
    """
    Internal helper ``_preset_row_to_out``.

    Parameters
    ----------
    row : object
        Argument ``row``.

    Returns
    -------
    object
        Return value.
    """
    raw_extensions = row.get("extensions")
    extensions = [str(item) for item in cast(list[object], raw_extensions)] if isinstance(raw_extensions, list) else []
    return PresetOut(
        id=row["id"],
        user_id=row["user_id"],
        slug=row["slug"],
        name=row["name"],
        semantic_profile=str(row["semantic_profile"]),
        iwxxm_version=str(row["iwxxm_version"]),
        extensions=extensions,
        report_variant=str(row["report_variant"]) if row.get("report_variant") else None,
        overlay_id=row.get("overlay_id"),
        shared=bool(row.get("shared")),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _template_row_to_out(row: dict[str, Any]) -> DisseminationTemplateOut:
    """
    Internal helper ``_template_row_to_out``.

    Parameters
    ----------
    row : object
        Argument ``row``.

    Returns
    -------
    object
        Return value.
    """
    raw_params = row.get("params")
    params: dict[str, Any] = cast(dict[str, Any], raw_params) if isinstance(raw_params, dict) else {}
    return DisseminationTemplateOut(
        id=row["id"],
        user_id=row["user_id"],
        slug=row["slug"],
        name=row["name"],
        sink_type=str(row["sink_type"]),
        product=str(row["product"]) if row.get("product") else None,
        ddl=bool(row.get("ddl")),
        params=params,
        shared=bool(row.get("shared")),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _reject_template_values(value: object, *, path: str) -> None:
    """
    Internal helper ``_reject_template_values``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    path : object
        Argument ``path``.
    """
    if isinstance(value, dict):
        _reject_secrets(cast(dict[str, Any], value), path=path)
        for key, nested in cast(dict[str, Any], value).items():
            nested_path = f"{path}.{key}" if path else str(key)
            _reject_template_values(nested, path=nested_path)
        return
    if isinstance(value, list):
        for index, nested in enumerate(cast(list[object], value)):
            _reject_template_values(nested, path=f"{path}[{index}]")
        return
    if isinstance(value, str) and _URI_VALUE.match(value.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Field not allowed in template persistence: {path}",
        )
