"""REST routes for F5/F7/F31 unified TAC work sessions (ADR-020 / ADR-033)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from ..schemas.work_session import (
    WorkSession,
    WorkSessionCreate,
    WorkSessionListResponse,
    WorkSessionProduct,
    WorkSessionStatus,
    WorkSessionUpdate,
)
from ..services.work_session_service import WorkSessionService
from ..utilities.security import verify_supabase_token

router = APIRouter()
_bearer = HTTPBearer(auto_error=True)


def work_session_service(
    user: dict[str, Any] = Depends(verify_supabase_token),
) -> WorkSessionService:
    """Build an owner-scoped session service from the verified JWT ``sub``."""
    return WorkSessionService(_user_id(user))


def _user_id(user: dict[str, Any]) -> str:
    return str(user.get("sub") or user.get("user_id"))


def _parse_product_filter(raw: str | None) -> list[WorkSessionProduct] | None:
    """
    Parse ``product`` query param (comma-separated product ids).

    Parameters
    ----------
    raw : str or None
        e.g. ``metar,speci`` for My METARs.

    Returns
    -------
    list[WorkSessionProduct] or None
        Parsed products, or None when the filter is omitted.

    Raises
    ------
    HTTPException
        422 when any token is not a known product.
    """
    if raw is None or not raw.strip():
        return None
    products: list[WorkSessionProduct] = []
    for token in raw.split(","):
        token = token.strip().lower()
        if not token:
            continue
        try:
            products.append(WorkSessionProduct(token))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid product filter value: {token!r}",
            ) from exc
    return products or None


@router.get("", response_model=WorkSessionListResponse)
def list_work_sessions(
    status_filter: WorkSessionStatus | None = Query(None, alias="status"),
    product: str | None = Query(
        None,
        description="Comma-separated product filter (e.g. metar,speci for My METARs)",
    ),
    from_dt: datetime | None = Query(None, alias="from"),
    to_dt: datetime | None = Query(None, alias="to"),
    include_deleted: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSessionListResponse:
    """List work sessions for the authenticated user with optional filters."""
    items, total = service.list_sessions(
        status_filter=status_filter,
        products=_parse_product_filter(product),
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
    """Create a new work session owned by the authenticated user."""
    return service.create_session(_user_id(user), payload)


@router.get("/{session_id}", response_model=WorkSession)
def get_work_session(
    session_id: UUID,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    """Return a single work session by id."""
    return service.get_session(session_id)


@router.patch("/{session_id}", response_model=WorkSession)
def update_work_session(
    session_id: UUID,
    payload: WorkSessionUpdate,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    """Update mutable fields on an existing work session."""
    return service.update_session(session_id, payload)


@router.delete("/{session_id}", response_model=WorkSession)
def delete_work_session(
    session_id: UUID,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    """Soft-delete a work session (sets ``deleted_at``)."""
    return service.soft_delete(session_id)


@router.post("/{session_id}/restore", response_model=WorkSession)
def restore_work_session(
    session_id: UUID,
    service: WorkSessionService = Depends(work_session_service),
) -> WorkSession:
    """Restore a previously soft-deleted work session."""
    return service.restore_session(session_id)


# Silence unused import of HTTPBearer helper (reserved for OpenAPI security schemes).
_ = _bearer
