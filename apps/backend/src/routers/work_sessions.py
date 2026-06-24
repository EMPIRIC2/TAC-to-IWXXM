"""REST routes for F5 METAR work sessions."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from auth.admin_api import require_admin
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionListResponse,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from ..services.work_session_service import WorkSessionService
from ..utilities.security import verify_supabase_token

router = APIRouter()
_bearer = HTTPBearer(auto_error=True)


def work_session_service(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> WorkSessionService:
    return WorkSessionService(credentials.credentials)


def _user_id(user: dict[str, Any]) -> str:
    return str(user.get("sub") or user.get("user_id"))


@router.get("", response_model=WorkSessionListResponse)
def list_work_sessions(
    status_filter: Optional[WorkSessionStatus] = Query(None, alias="status"),
    from_dt: Optional[datetime] = Query(None, alias="from"),
    to_dt: Optional[datetime] = Query(None, alias="to"),
    include_deleted: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSessionListResponse:
    items, total = service.list_sessions(
        status_filter=status_filter,
        from_dt=from_dt,
        to_dt=to_dt,
        include_deleted=include_deleted,
        page=page,
        limit=limit,
    )
    return WorkSessionListResponse(items=items, total=total, page=page, limit=limit)


@router.post("", response_model=WorkSession, status_code=status.HTTP_201_CREATED)
def create_work_session(
    payload: WorkSessionCreate,
    user: dict[str, Any] = Depends(verify_supabase_token),
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    return service.create_session(_user_id(user), payload)


@router.get("/{session_id}", response_model=WorkSession)
def get_work_session(
    session_id: UUID,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    return service.get_session(session_id)


@router.patch("/{session_id}", response_model=WorkSession)
def update_work_session(
    session_id: UUID,
    payload: WorkSessionUpdate,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    return service.update_session(session_id, payload)


@router.delete("/{session_id}", response_model=WorkSession)
def delete_work_session(
    session_id: UUID,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    return service.soft_delete(session_id)


@router.post("/{session_id}/restore", response_model=WorkSession)
def restore_work_session(
    session_id: UUID,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    return service.restore_session(session_id)


admin_router = APIRouter(prefix="/admin/work-sessions", tags=["Admin"])


@admin_router.get("", response_model=WorkSessionListResponse)
def admin_list_work_sessions(
    status_filter: Optional[WorkSessionStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _admin: dict[str, Any] = Depends(require_admin),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> WorkSessionListResponse:
    service = WorkSessionService(credentials.credentials)
    items, total = service.list_sessions(status_filter=status_filter, page=page, limit=limit)
    return WorkSessionListResponse(items=items, total=total, page=page, limit=limit)
