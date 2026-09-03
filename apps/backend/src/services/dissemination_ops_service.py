"""Owner-scoped CRUD for dissemination plans, audit, and mappings (EV-936)."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime
from typing import Any, NoReturn, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..schemas.dissemination_ops import (
    AuditRecordOut,
    DisseminationPlanCreate,
    DisseminationPlanOut,
    DisseminationPlanUpdate,
    MappingConfigCreate,
    MappingConfigOut,
    MappingConfigUpdate,
)

logger = logging.getLogger(__name__)

PLANS_TABLE = "tac_dissemination_plans"
AUDIT_TABLE = "tac_dissemination_audit"
MAPPINGS_TABLE = "tac_mapping_configs"

_SECRET_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|uri|connection_string|dsn)")

_engine: Engine | None = None
_metadata = MetaData()
_tables: dict[str, Table] = {}


def _sync_database_url() -> str:
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
    global _engine
    if _engine is None:
        _engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    return _engine


def _table(name: str) -> Table:
    if name not in _tables:
        _tables[name] = Table(name, _metadata, autoload_with=_get_engine())
    return _tables[name]


def _reject_secrets(payload: dict[str, Any], *, path: str = "") -> None:
    """Raise 422 if payload keys look like secrets or URIs."""
    for key, value in payload.items():
        full = f"{path}.{key}" if path else key
        if _SECRET_KEY.search(key):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
    """Always raises — narrows type checkers after except handlers."""
    _handle_db_error(exc)


class DisseminationOpsService:
    """JWT owner-scoped persistence for plans, audit, and MappingConfig."""

    def __init__(self, user_id: str) -> None:
        self.user_id = UUID(user_id)

    def create_plan(self, payload: DisseminationPlanCreate) -> DisseminationPlanOut:
        _reject_secrets(payload.model_dump())
        row: dict[str, Any] = {
            "id": uuid4(),
            "user_id": self.user_id,
            "slug": payload.slug,
            "validity_policy": payload.validity_policy,
            "destination_refs": payload.destination_refs,
            "transforms": payload.transforms,
            "retry": payload.retry,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(_table(PLANS_TABLE)).values(**row))
        except SQLAlchemyError as exc:
            _raise_db(exc)
        return DisseminationPlanOut.model_validate(row)

    def get_plan(self, plan_id: UUID) -> DisseminationPlanOut:
        t = _table(PLANS_TABLE)
        result: Any | None
        try:
            with _get_engine().connect() as conn:
                result = (
                    conn.execute(select(t).where(t.c.id == plan_id, t.c.user_id == self.user_id)).mappings().first()
                )
        except SQLAlchemyError as exc:
            _raise_db(exc)
        if result is None:
            raise HTTPException(status_code=404, detail="Plan not found")
        return DisseminationPlanOut.model_validate(dict(result))

    def update_plan(self, plan_id: UUID, payload: DisseminationPlanUpdate) -> DisseminationPlanOut:
        data = payload.model_dump(exclude_unset=True)
        _reject_secrets(data)
        existing = self.get_plan(plan_id)
        merged = existing.model_dump()
        merged.update(data)
        merged["updated_at"] = datetime.now(UTC)
        t = _table(PLANS_TABLE)
        try:
            with _get_engine().begin() as conn:
                conn.execute(
                    t.update()
                    .where(t.c.id == plan_id, t.c.user_id == self.user_id)
                    .values(**{k: merged[k] for k in data}, updated_at=merged["updated_at"])
                )
        except SQLAlchemyError as exc:
            _raise_db(exc)
        return DisseminationPlanOut.model_validate(merged)

    def record_audit(
        self,
        *,
        status_value: str,
        gateway: str,
        detail: str | None = None,
        message_id: str | None = None,
        station: str | None = None,
        profile: str | None = None,
        iwxxm_version: str | None = None,
        product: str | None = None,
        destinations: dict[str, Any] | None = None,
    ) -> AuditRecordOut:
        dest = destinations or {}
        _reject_secrets(dest)
        row: dict[str, Any] = {
            "id": uuid4(),
            "user_id": self.user_id,
            "message_id": message_id,
            "station": station,
            "profile": profile,
            "iwxxm_version": iwxxm_version,
            "product": product,
            "status": status_value,
            "gateway": gateway,
            "detail": detail,
            "destinations": dest,
            "created_at": datetime.now(UTC),
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(_table(AUDIT_TABLE)).values(**row))
        except SQLAlchemyError as exc:
            _raise_db(exc)
        return AuditRecordOut.model_validate(row)

    def list_audit(
        self,
        *,
        product: str | None = None,
        station: str | None = None,
        profile: str | None = None,
        status_filter: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[AuditRecordOut], int]:
        t = _table(AUDIT_TABLE)
        stmt = select(t).where(t.c.user_id == self.user_id)
        if product:
            stmt = stmt.where(t.c.product == product)
        if station:
            stmt = stmt.where(t.c.station == station)
        if profile:
            stmt = stmt.where(t.c.profile == profile)
        if status_filter:
            stmt = stmt.where(t.c.status == status_filter)
        rows: list[Any]
        total: int
        try:
            with _get_engine().connect() as conn:
                mapped = (
                    conn.execute(stmt.order_by(t.c.created_at.desc()).offset((page - 1) * limit).limit(limit))
                    .mappings()
                    .all()
                )
                rows = list(mapped)
                total = len(rows) if page == 1 and len(rows) < limit else (page - 1) * limit + len(rows)
        except SQLAlchemyError as exc:
            _raise_db(exc)
        return [AuditRecordOut.model_validate(dict(r)) for r in rows], total

    def get_audit(self, audit_id: UUID) -> AuditRecordOut:
        t = _table(AUDIT_TABLE)
        result: Any | None
        try:
            with _get_engine().connect() as conn:
                result = (
                    conn.execute(select(t).where(t.c.id == audit_id, t.c.user_id == self.user_id)).mappings().first()
                )
        except SQLAlchemyError as exc:
            _raise_db(exc)
        if result is None:
            raise HTTPException(status_code=404, detail="Audit record not found")
        return AuditRecordOut.model_validate(dict(result))

    def create_mapping(self, payload: MappingConfigCreate) -> MappingConfigOut:
        _reject_secrets(payload.model_dump())
        row: dict[str, Any] = {
            "id": uuid4(),
            "user_id": self.user_id,
            "name": payload.name,
            "mode": payload.mode,
            "config": payload.config,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(_table(MAPPINGS_TABLE)).values(**row))
        except SQLAlchemyError as exc:
            _raise_db(exc)
        return MappingConfigOut.model_validate(row)

    def get_mapping(self, mapping_id: UUID) -> MappingConfigOut:
        t = _table(MAPPINGS_TABLE)
        result: Any | None
        try:
            with _get_engine().connect() as conn:
                result = (
                    conn.execute(select(t).where(t.c.id == mapping_id, t.c.user_id == self.user_id)).mappings().first()
                )
        except SQLAlchemyError as exc:
            _raise_db(exc)
        if result is None:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return MappingConfigOut.model_validate(dict(result))

    def update_mapping(self, mapping_id: UUID, payload: MappingConfigUpdate) -> MappingConfigOut:
        data = payload.model_dump(exclude_unset=True)
        _reject_secrets(data)
        existing = self.get_mapping(mapping_id)
        merged = existing.model_dump()
        merged.update(data)
        merged["updated_at"] = datetime.now(UTC)
        t = _table(MAPPINGS_TABLE)
        try:
            with _get_engine().begin() as conn:
                conn.execute(
                    t.update()
                    .where(t.c.id == mapping_id, t.c.user_id == self.user_id)
                    .values(**{k: merged[k] for k in data}, updated_at=merged["updated_at"])
                )
        except SQLAlchemyError as exc:
            _raise_db(exc)
        return MappingConfigOut.model_validate(merged)
