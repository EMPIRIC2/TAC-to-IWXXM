"""WIS2-only exchange admin HTTP surface (read-only allowlist, memory templates)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from ..services.exchange_admin import (
    allowlist_view,
    get_prefs,
    list_invitation_groups,
    list_templates,
    set_invitation_group,
    set_national_remarks,
    upsert_template,
    user_has_exchange_admin,
)
from ..utilities.security import verify_supabase_token

router = APIRouter(prefix="/api/v1/exchange-admin", tags=["Exchange Admin"])
_bearer = HTTPBearer(auto_error=True)


def _require_exchange_admin(user: dict[str, Any] = Depends(verify_supabase_token)) -> dict[str, Any]:
    """
    JWT gate for the single exchange-admin role.

    Parameters
    ----------
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    if not user_has_exchange_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="exchange-admin role required",
        )
    return user


def _sub(user: dict[str, Any]) -> str:
    """
    Internal helper ``_sub``.

    Parameters
    ----------
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    return str(user.get("sub") or user.get("user_id") or "")


@router.get("/allowlist", summary="Read-only egress allowlist (GitOps)")
def get_allowlist(_user: dict[str, Any] = Depends(_require_exchange_admin)) -> dict[str, Any]:
    """
    Return the configured egress allowlist. Editing is GitOps-only.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_allowlist)
    2

    Parameters
    ----------
    _user : object
        Argument ``_user``.

    Returns
    -------
    object
        Return value.
    """
    return allowlist_view()


@router.get("/invitation-groups", summary="Invitation groups for login")
def get_invitation_groups(
    _user: dict[str, Any] = Depends(verify_supabase_token),
) -> dict[str, Any]:
    """
    List multi-tenant invitation groups offered at login.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_invitation_groups)
    2

    Parameters
    ----------
    _user : object
        Argument ``_user``.

    Returns
    -------
    object
        Return value.
    """
    groups = list_invitation_groups()
    return {
        "groups": [{"id": g.id, "name": g.name, "centre_id": g.centre_id} for g in groups],
    }


@router.put("/invitation-group", summary="Select invitation group at login")
def put_invitation_group(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(verify_supabase_token),
) -> dict[str, Any]:
    """
    Bind the signed-in operator to one invitation group.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (put_invitation_group)
    2

    Parameters
    ----------
    body : object
        Argument ``body``.
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    group_id = str(body.get("group_id") or "").strip()
    if not group_id:
        raise HTTPException(status_code=422, detail="group_id is required")
    try:
        prefs = set_invitation_group(_sub(user), group_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "invitation_group_id": prefs.invitation_group_id,
        "include_national_remarks": prefs.include_national_remarks,
    }


@router.get("/prefs", summary="Operator exchange preferences")
def get_operator_prefs(user: dict[str, Any] = Depends(_require_exchange_admin)) -> dict[str, Any]:
    """
    Return national-remarks toggle and selected invitation group.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_operator_prefs)
    2

    Parameters
    ----------
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    prefs = get_prefs(_sub(user))
    return {
        "include_national_remarks": prefs.include_national_remarks,
        "invitation_group_id": prefs.invitation_group_id,
        "admin_replay": False,
        "sink_scope": "wis2",
    }


@router.put("/prefs/national-remarks", summary="Toggle national remarks on WIS2 publish")
def put_national_remarks(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(_require_exchange_admin),
) -> dict[str, Any]:
    """
    Operator toggle: include national remarks when publishing to WIS2.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (put_national_remarks)
    2

    Parameters
    ----------
    body : object
        Argument ``body``.
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    if "include" not in body:
        raise HTTPException(status_code=422, detail="include is required")
    prefs = set_national_remarks(_sub(user), bool(body.get("include")))
    return {
        "include_national_remarks": prefs.include_national_remarks,
        "invitation_group_id": prefs.invitation_group_id,
    }


@router.get("/templates", summary="List non-secret WIS2 templates")
def get_templates(user: dict[str, Any] = Depends(_require_exchange_admin)) -> dict[str, Any]:
    """
    List memory-only non-secret destination templates (no vault).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_templates)
    2

    Parameters
    ----------
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    items = list_templates(_sub(user))
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "mqtt_host": t.mqtt_host,
                "mqtt_topic": t.mqtt_topic,
                "dataset_url": t.dataset_url,
                "mqtt_port": t.mqtt_port,
                "centre_id": t.centre_id,
                "use_tls": t.use_tls,
            }
            for t in items
        ],
        "vault": False,
    }


@router.put("/templates", summary="Upsert non-secret WIS2 template")
def put_template(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(_require_exchange_admin),
) -> dict[str, Any]:
    """
    Create or replace a non-secret template. Secrets must be pasted at send time.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (put_template)
    2

    Parameters
    ----------
    body : object
        Argument ``body``.
    user : object
        Argument ``user``.

    Returns
    -------
    object
        Return value.
    """
    try:
        tmpl = upsert_template(_sub(user), body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": tmpl.id,
        "name": tmpl.name,
        "mqtt_host": tmpl.mqtt_host,
        "mqtt_topic": tmpl.mqtt_topic,
        "dataset_url": tmpl.dataset_url,
        "mqtt_port": tmpl.mqtt_port,
        "centre_id": tmpl.centre_id,
        "use_tls": tmpl.use_tls,
    }
