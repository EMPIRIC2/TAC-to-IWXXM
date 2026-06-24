"""Supabase-backed CRUD for METAR work sessions (F5)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, NoReturn, Optional, cast
from uuid import UUID

from fastapi import HTTPException, status
from metar_shared.supabase_env import get_supabase_publishable_key, get_supabase_url
from supabase import Client, create_client

from ..schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionStatus,
    WorkSessionUpdate,
)

logger = logging.getLogger(__name__)

TABLE = "metar_work_sessions"
WIP_CONFLICT = "23505"


def _client_for_token(access_token: str) -> Client:
    url = get_supabase_url()
    key = get_supabase_publishable_key()
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Work session service unavailable — missing Supabase configuration",
        )
    client = create_client(url, key)
    client.postgrest.auth(access_token)
    return client


def _row_dict(data: object) -> dict[str, Any] | None:
    if isinstance(data, dict):
        return cast(dict[str, Any], data)
    return None


def _row_list(data: object) -> list[dict[str, Any]]:
    if not isinstance(data, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in cast(list[object], data):
        row = _row_dict(item)
        if row is not None:
            rows.append(row)
    return rows


def _parse_row(row: dict[str, Any]) -> WorkSession:
    return WorkSession.model_validate(row)


def _payload_dict(payload: WorkSessionCreate | WorkSessionUpdate, *, user_id: str | None = None) -> dict[str, Any]:
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    if user_id is not None:
        data["user_id"] = user_id
    if "status" in data and data["status"] is not None:
        data["status"] = data["status"].value if hasattr(data["status"], "value") else data["status"]
    if "pending_files" in data:
        data["pending_files"] = [f.model_dump() if hasattr(f, "model_dump") else f for f in data["pending_files"]]
    return data


def _handle_db_error(exc: Exception) -> NoReturn:
    message = str(exc)
    if WIP_CONFLICT in message or "metar_work_sessions_one_wip_per_user" in message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only one WIP session is allowed per user",
        ) from exc
    if "metar_work_sessions" in message and (
        "does not exist" in message.lower() or "42P01" in message or "PGRST205" in message
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=("Work sessions unavailable — apply Supabase migration 20250623000007_metar_work_sessions.sql"),
        ) from exc
    logger.exception("Work session database error")
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Work session database error") from exc


def _single_row(data: object) -> dict[str, Any]:
    row = _row_dict(data)
    if row is not None:
        return row
    rows = _row_list(data)
    if rows:
        return rows[0]
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Work session database error")


class WorkSessionService:
    """CRUD helpers using Supabase PostgREST with caller JWT (RLS enforced)."""

    def __init__(self, access_token: str) -> None:
        self._token = access_token
        self._client = _client_for_token(access_token)

    def list_sessions(
        self,
        *,
        status_filter: Optional[WorkSessionStatus] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
        include_deleted: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[WorkSession], int]:
        query = self._client.table(TABLE).select("*", count="exact")  # type: ignore[arg-type]
        if not include_deleted:
            query = query.is_("deleted_at", "null")
        if status_filter is not None:
            query = query.eq("status", status_filter.value)
        if from_dt is not None:
            query = query.gte("updated_at", from_dt.isoformat())
        if to_dt is not None:
            query = query.lte("updated_at", to_dt.isoformat())
        offset = max(page - 1, 0) * limit
        query = query.order("updated_at", desc=True).range(offset, offset + limit - 1)
        try:
            response = query.execute()
        except Exception as exc:
            _handle_db_error(exc)
        rows = _row_list(response.data)
        total = int(response.count or len(rows))
        return [_parse_row(row) for row in rows], total

    def get_session(self, session_id: UUID) -> WorkSession:
        try:
            response = (
                self._client.table(TABLE)
                .select("*")
                .eq("id", str(session_id))
                .is_("deleted_at", "null")
                .maybe_single()
                .execute()
            )
        except Exception as exc:
            _handle_db_error(exc)
        if response is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work session not found")
        row = _row_dict(response.data)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work session not found")
        return _parse_row(row)

    def create_session(self, user_id: str, payload: WorkSessionCreate) -> WorkSession:
        data = _payload_dict(payload, user_id=user_id)
        if "status" not in data:
            data["status"] = WorkSessionStatus.DRAFT.value
        if not data.get("title"):
            data["title"] = f"METAR {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC"
        try:
            response = self._client.table(TABLE).insert(data).select("*").execute()
        except Exception as exc:
            _handle_db_error(exc)
        return _parse_row(_single_row(response.data))

    def update_session(self, session_id: UUID, payload: WorkSessionUpdate) -> WorkSession:
        data = _payload_dict(payload)
        if not data:
            return self.get_session(session_id)
        try:
            response = (
                self._client.table(TABLE)
                .update(data)
                .eq("id", str(session_id))
                .is_("deleted_at", "null")
                .select("*")
                .execute()
            )
        except Exception as exc:
            _handle_db_error(exc)
        try:
            return _parse_row(_single_row(response.data))
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work session not found") from None

    def soft_delete(self, session_id: UUID) -> WorkSession:
        now = datetime.now(timezone.utc).isoformat()
        try:
            response = (
                self._client.table(TABLE)
                .update({"deleted_at": now})
                .eq("id", str(session_id))
                .is_("deleted_at", "null")
                .select("*")
                .execute()
            )
        except Exception as exc:
            _handle_db_error(exc)
        try:
            return _parse_row(_single_row(response.data))
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work session not found") from None

    def restore_session(self, session_id: UUID) -> WorkSession:
        try:
            response = (
                self._client.table(TABLE)
                .update({"deleted_at": None})
                .eq("id", str(session_id))
                .not_.is_("deleted_at", "null")
                .select("*")
                .execute()
            )
        except Exception as exc:
            _handle_db_error(exc)
        try:
            return _parse_row(_single_row(response.data))
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work session not found or not deleted",
            ) from None
