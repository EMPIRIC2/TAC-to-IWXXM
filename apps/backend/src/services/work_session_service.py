"""SQLAlchemy CRUD for ``tac_work_sessions`` on ``DATABASE_URL`` (F31 / ADR-033)."""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any, NoReturn, Sequence
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import MetaData, Table, create_engine, select, text, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)

logger = logging.getLogger(__name__)

TABLE = "tac_work_sessions"
WIP_CONFLICT = "23505"

_engine: Engine | None = None
_metadata = MetaData()
_sessions_table: Table | None = None


def _sync_database_url() -> str:
    raw = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Work session service unavailable — missing DATABASE_URL",
        )
    if raw.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql+asyncpg://")
    if raw.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql+psycopg2://")
    if raw.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw.removeprefix("postgresql://")
    return raw


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(_sync_database_url(), pool_pre_ping=True)
    return _engine


def _table() -> Table:
    global _sessions_table
    if _sessions_table is None:
        _sessions_table = Table(TABLE, _metadata, autoload_with=_get_engine())
    return _sessions_table


def _parse_row(row: dict[str, Any]) -> WorkSession:
    return WorkSession.model_validate(row)


def _payload_dict(
    payload: WorkSessionCreate | WorkSessionUpdate,
    *,
    user_id: str | None = None,
) -> dict[str, Any]:
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    if user_id is not None:
        data["user_id"] = user_id
    if "status" in data and data["status"] is not None:
        status_val = data["status"]
        data["status"] = status_val.value if hasattr(status_val, "value") else status_val
    if "product" in data and data["product"] is not None:
        product_val = data["product"]
        data["product"] = product_val.value if hasattr(product_val, "value") else product_val
    if "pending_files" in data:
        data["pending_files"] = [f.model_dump() if hasattr(f, "model_dump") else f for f in data["pending_files"]]
    return data


def _handle_db_error(exc: Exception) -> NoReturn:
    message = str(exc)
    if WIP_CONFLICT in message or "tac_work_sessions_one_wip_per_user" in message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only one WIP session is allowed per user",
        ) from exc
    if isinstance(exc, IntegrityError) and "one_wip" in message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only one WIP session is allowed per user",
        ) from exc
    if TABLE in message and ("does not exist" in message.lower() or "42P01" in message):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Work sessions unavailable — run `make db-migrate` (Alembic upgrade head)",
        ) from exc
    logger.exception("Work session database error")
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Work session database error",
    ) from exc


class WorkSessionService:
    """Owner-scoped CRUD against DigitalOcean Postgres ``tac_work_sessions``."""

    def __init__(self, user_id: str) -> None:
        self.user_id = str(user_id)

    def list_sessions(
        self,
        *,
        status_filter: WorkSessionStatus | None = None,
        products: Sequence[WorkSessionProduct] | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        include_deleted: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[WorkSession], int]:
        table = _table()
        try:
            with _get_engine().connect() as conn:
                stmt = select(table).where(table.c.user_id == UUID(self.user_id))
                if not include_deleted:
                    stmt = stmt.where(table.c.deleted_at.is_(None))
                if status_filter is not None:
                    stmt = stmt.where(table.c.status == status_filter.value)
                if products:
                    stmt = stmt.where(table.c.product.in_([p.value for p in products]))
                if from_dt is not None:
                    stmt = stmt.where(table.c.updated_at >= from_dt)
                if to_dt is not None:
                    stmt = stmt.where(table.c.updated_at <= to_dt)

                count_stmt = select(text("count(*)")).select_from(stmt.subquery())
                total = int(conn.execute(count_stmt).scalar_one())
                rows = conn.execute(
                    stmt.order_by(table.c.updated_at.desc()).offset((page - 1) * limit).limit(limit)
                ).mappings()
                items = [_parse_row(dict(row)) for row in rows]
                return items, total
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def get_session(self, session_id: UUID) -> WorkSession:
        table = _table()
        try:
            with _get_engine().connect() as conn:
                row = (
                    conn.execute(
                        select(table).where(
                            table.c.id == session_id,
                            table.c.user_id == UUID(self.user_id),
                        )
                    )
                    .mappings()
                    .first()
                )
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
        if row is None:
            raise HTTPException(status_code=404, detail="Work session not found")
        return _parse_row(dict(row))

    def create_session(self, user_id: str, payload: WorkSessionCreate) -> WorkSession:
        table = _table()
        data = _payload_dict(payload, user_id=user_id)
        data.setdefault("id", uuid4())
        data.setdefault("status", WorkSessionStatus.DRAFT.value)
        data.setdefault("title", "")
        now = datetime.now(UTC)
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        try:
            with _get_engine().begin() as conn:
                conn.execute(table.insert().values(**data))
                row = conn.execute(select(table).where(table.c.id == data["id"])).mappings().one()
                return _parse_row(dict(row))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def update_session(self, session_id: UUID, payload: WorkSessionUpdate) -> WorkSession:
        self.get_session(session_id)
        table = _table()
        data = _payload_dict(payload)
        data["updated_at"] = datetime.now(UTC)
        try:
            with _get_engine().begin() as conn:
                result = conn.execute(
                    update(table)
                    .where(
                        table.c.id == session_id,
                        table.c.user_id == UUID(self.user_id),
                    )
                    .values(**data)
                )
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Work session not found")
                row = conn.execute(select(table).where(table.c.id == session_id)).mappings().one()
                return _parse_row(dict(row))
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            _handle_db_error(exc)

    def soft_delete(self, session_id: UUID) -> WorkSession:
        return self._set_deleted(session_id, deleted=True)

    def restore_session(self, session_id: UUID) -> WorkSession:
        return self._set_deleted(session_id, deleted=False)

    def _set_deleted(self, session_id: UUID, *, deleted: bool) -> WorkSession:
        self.get_session(session_id)
        table = _table()
        stamp = datetime.now(UTC) if deleted else None
        try:
            with _get_engine().begin() as conn:
                conn.execute(
                    update(table)
                    .where(
                        table.c.id == session_id,
                        table.c.user_id == UUID(self.user_id),
                    )
                    .values(deleted_at=stamp, updated_at=datetime.now(UTC))
                )
                row = conn.execute(select(table).where(table.c.id == session_id)).mappings().one()
                return _parse_row(dict(row))
        except SQLAlchemyError as exc:
            _handle_db_error(exc)
