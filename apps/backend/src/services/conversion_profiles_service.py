"""Owner-scoped CRUD for ConversionProfile rule packs (EV-933 / F7.w)."""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime
from typing import Any, NoReturn, cast
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine, delete, insert, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..schemas.conversion_profiles import RulePackCreate, RulePackOut, RulePackUpdate

logger = logging.getLogger(__name__)

RULE_PACKS_TABLE = "tac_profile_rule_packs"
_SECRET_KEY = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|uri|connection_string|dsn)")

_engine: Engine | None = None
_metadata = MetaData()
_tables: dict[str, Table] = {}


def _sync_database_url() -> str:
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
                detail=f"Field not allowed in profile persistence: {full}",
            )
        if isinstance(value, dict):
            nested = cast(dict[str, Any], value)
            _reject_secrets(nested, path=full)


def _handle_db_error(exc: Exception) -> NoReturn:
    logger.exception("conversion profiles db error: %s", exc)
    if isinstance(exc, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict saving rule pack",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Profile rule packs unavailable",
    ) from exc


def _row_to_out(row: dict[str, Any]) -> RulePackOut:
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


class ConversionProfilesService:
    """JWT-owner scoped rule pack persistence."""

    def __init__(self, user_id: str) -> None:
        """
        Parameters
        ----------
        user_id :
            JWT ``sub`` (UUID string).
        """
        try:
            self.user_id = UUID(user_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identity",
            ) from exc

    def list_rule_packs(self) -> list[RulePackOut]:
        """List rule packs owned by the caller."""
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().connect() as conn:
                rows = conn.execute(select(t).where(t.c.user_id == self.user_id).order_by(t.c.slug)).mappings().all()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return [_row_to_out(dict(r)) for r in rows]

    def get_rule_pack(self, pack_id: UUID) -> RulePackOut:
        """Fetch one rule pack by id (owner-scoped)."""
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().connect() as conn:
                row = conn.execute(select(t).where(t.c.id == pack_id, t.c.user_id == self.user_id)).mappings().first()
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Rule pack not found")
        return _row_to_out(dict(row))

    def create_rule_pack(self, payload: RulePackCreate) -> RulePackOut:
        """Insert a new rule pack."""
        data = payload.model_dump(by_alias=False)
        _reject_secrets(data)
        now = datetime.now(tz=UTC)
        pack_id = uuid4()
        t = _table(RULE_PACKS_TABLE)
        values = {
            "id": pack_id,
            "user_id": self.user_id,
            "slug": payload.slug,
            "profile": payload.profile,
            "product": payload.product,
            "stage": payload.stage,
            "severity": payload.severity,
            "when_expr": payload.when_expr,
            "message": payload.message,
            "standard_reference": payload.standard_reference,
            "created_at": now,
            "updated_at": now,
        }
        try:
            with _get_engine().begin() as conn:
                conn.execute(insert(t).values(**values))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_rule_pack(pack_id)

    def update_rule_pack(self, pack_id: UUID, payload: RulePackUpdate) -> RulePackOut:
        """Patch an existing rule pack."""
        data = payload.model_dump(exclude_unset=True, by_alias=False)
        _reject_secrets(data)
        if not data:
            return self.get_rule_pack(pack_id)
        data["updated_at"] = datetime.now(tz=UTC)
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(update(t).where(t.c.id == pack_id, t.c.user_id == self.user_id).values(**data))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Rule pack not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        return self.get_rule_pack(pack_id)

    def delete_rule_pack(self, pack_id: UUID) -> None:
        """Delete a rule pack owned by the caller."""
        t = _table(RULE_PACKS_TABLE)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(delete(t).where(t.c.id == pack_id, t.c.user_id == self.user_id))
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Rule pack not found")
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
