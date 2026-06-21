"""Admin API routes — settings, user monitoring, and admin role management.

Served on the merged API host at ``/admin/*`` (M4). Replaces Supabase Edge
Function URLs previously hard-coded in admin dashboard panels.
"""

from __future__ import annotations

import copy
import logging
import os
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from supabase import Client, create_client

from api_supabase import get_token_from_header
from supabase_proxy import SupabaseAuthProxy, get_supabase_proxy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

DEFAULT_SETTINGS: dict[str, Any] = {
    "defaultBulletinId": "SAAA00",
    "defaultIssuingCenter": "KWBC",
    "defaultIwxxmVersion": "2025-2",
    "defaultStrictValidation": True,
    "defaultIncludeNilReasons": True,
    "defaultOnError": "warn",
    "defaultLogLevel": "INFO",
    "allowedIcaoCodes": [],
}

_system_settings: dict[str, Any] = copy.deepcopy(DEFAULT_SETTINGS)


class ToggleAdminRequest(BaseModel):
    """Request body for granting or revoking admin status."""

    userId: str = Field(min_length=1)
    isAdmin: bool


class SystemSettingsPayload(BaseModel):
    """Wrapper for system settings POST body."""

    settings: dict[str, Any]


def _get_service_client() -> Client:
    """Return a Supabase client authenticated with the service role key."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable — missing Supabase service configuration",
        )
    return create_client(url, key)


def _profile_row(data: object) -> dict[str, Any] | None:
    """Return a profile row dict when Supabase JSON is a mapping."""
    if isinstance(data, dict):
        return cast(dict[str, Any], data)
    return None


def _profile_rows(data: object) -> list[dict[str, Any]]:
    """Return profile row dicts from a Supabase list response."""
    if not isinstance(data, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in cast(list[object], data):
        row = _profile_row(item)
        if row is not None:
            rows.append(row)
    return rows


def _profile_to_user_info(row: dict[str, Any]) -> dict[str, Any]:
    """Map a ``user_profiles`` row to the frontend monitoring panel shape."""
    return {
        "user_id": row.get("id") or row.get("user_id"),
        "email": row.get("email", ""),
        "username": row.get("username", ""),
        "approval_status": row.get("approval_status", "pending"),
        "is_admin": bool(row.get("is_admin")),
        "created_at": row.get("created_at"),
        "approved_at": row.get("approved_at"),
        "last_login": row.get("last_login"),
    }


def require_admin(
    token: str = Depends(get_token_from_header),
    proxy: SupabaseAuthProxy = Depends(get_supabase_proxy),
) -> dict[str, Any]:
    """Validate bearer token and ensure the caller has admin privileges."""
    user = proxy.get_user(token)
    user_id = user["id"]

    client = _get_service_client()
    result = client.table("user_profiles").select("is_admin").eq("id", user_id).maybe_single().execute()

    profile = None if result is None else _profile_row(result.data)
    if profile is None or not profile.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user


@router.get("/settings")
def get_settings(_admin: dict[str, Any] = Depends(require_admin)) -> dict[str, Any]:
    """Return current system settings (defaults when none saved yet)."""
    return {"settings": copy.deepcopy(_system_settings)}


@router.post("/settings")
def save_settings(
    payload: SystemSettingsPayload,
    _admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """Persist system settings for the current process."""
    global _system_settings
    if not payload.settings:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Settings payload must not be empty",
        )
    unknown_keys = set(payload.settings) - set(DEFAULT_SETTINGS)
    if unknown_keys:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown settings keys: {sorted(unknown_keys)}",
        )
    merged = copy.deepcopy(DEFAULT_SETTINGS)
    merged.update(payload.settings)
    _system_settings = merged
    logger.info("[ADMIN] System settings updated")
    return {"message": "Settings saved successfully", "settings": copy.deepcopy(_system_settings)}


@router.get("/all-users")
def list_all_users(_admin: dict[str, Any] = Depends(require_admin)) -> dict[str, Any]:
    """List all user profiles for the monitoring panel."""
    client = _get_service_client()
    result = client.table("user_profiles").select("*").order("created_at", desc=True).execute()
    users = [_profile_to_user_info(row) for row in _profile_rows(result.data)]
    return {"users": users}


@router.get("/stats")
def get_stats(_admin: dict[str, Any] = Depends(require_admin)) -> dict[str, Any]:
    """Return aggregate user statistics for the monitoring dashboard."""
    client = _get_service_client()
    result = client.table("user_profiles").select("*").execute()
    rows = _profile_rows(result.data)

    stats = {
        "totalUsers": len(rows),
        "pendingUsers": sum(1 for r in rows if r.get("approval_status") == "pending"),
        "approvedUsers": sum(1 for r in rows if r.get("approval_status") == "approved"),
        "rejectedUsers": sum(1 for r in rows if r.get("approval_status") == "rejected"),
        "adminUsers": sum(1 for r in rows if r.get("is_admin")),
        "totalConversions": 0,
        "totalStorageUsed": "0 MB",
    }
    return {"stats": stats}


@router.post("/toggle-admin")
def toggle_admin(
    payload: ToggleAdminRequest,
    _admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    """Grant or revoke admin status on a user profile."""
    client = _get_service_client()
    update = client.table("user_profiles").update({"is_admin": payload.isAdmin}).eq("id", payload.userId).execute()

    if not update.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    row = _profile_row(update.data[0])
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(
        "[ADMIN] Admin status %s for user %s",
        "granted" if payload.isAdmin else "revoked",
        payload.userId,
    )
    return {
        "message": f"Admin status {'granted' if payload.isAdmin else 'revoked'}",
        "profile": _profile_to_user_info(row),
    }
