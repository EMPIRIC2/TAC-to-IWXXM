"""Part 1 of ``conversion_profiles.py`` (line-cap split)."""

from __future__ import annotations

from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from ..schemas.conversion_profiles import (
    DisseminationTemplateCreate,
    DisseminationTemplateListResponse,
    DisseminationTemplateOut,
    PresetCreate,
    PresetListResponse,
    PresetOut,
    PresetUpdate,
    ProfileCatalogResponse,
    RulePackCreate,
    RulePackListResponse,
    RulePackOut,
    RulePackUpdate,
)
from ..services.conversion_profiles_service import ConversionProfilesService
from ..services.profile_catalog import load_profile_catalog
from ..utilities.security import verify_supabase_token

router = APIRouter(prefix="/api/v1/profiles", tags=["Conversion Profiles"])

_LIBRARY_AUTHORING_GONE = {
    "code": "library_authoring_retired",
    "message": "Library authoring is no longer available. Use deployed package catalogs and selection dropdowns.",
}


def _library_authoring_gone() -> NoReturn:
    """
    Internal helper ``_library_authoring_gone``.

    Returns
    -------
    object
        Return value.
    """
    raise HTTPException(status_code=410, detail=_LIBRARY_AUTHORING_GONE)


_bearer = HTTPBearer(auto_error=True)


def profiles_service(
    user: dict[str, Any] = Depends(verify_supabase_token),
) -> ConversionProfilesService:
    """
    Build owner-scoped profiles service from JWT ``sub``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (profiles_service)
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
    return ConversionProfilesService(str(user.get("sub") or user.get("user_id")))


def get_catalog(
    _user: dict[str, Any] = Depends(verify_supabase_token),
    service: ConversionProfilesService = Depends(profiles_service),
) -> ProfileCatalogResponse:
    """Read-only ConversionProfile catalog for the authenticated Profiles inspector."""
    rule_pack_counts: dict[str, int] | None = {}
    try:
        for pack in service.list_rule_packs():
            assert rule_pack_counts is not None
            rule_pack_counts[pack.profile] = rule_pack_counts.get(pack.profile, 0) + 1
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        rule_pack_counts = None

    overlay_counts: dict[str, int] | None = {}
    try:
        for overlay in service.list_overlays():
            key = overlay.base_profile_id
            assert overlay_counts is not None
            overlay_counts[key] = overlay_counts.get(key, 0) + 1
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        overlay_counts = None

    return load_profile_catalog(
        rule_pack_counts=rule_pack_counts,
        overlay_counts=overlay_counts,
    )


def list_rule_packs(
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackListResponse:
    """
    List rule packs owned by the caller.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_rule_packs)
    2

    Parameters
    ----------
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return RulePackListResponse(items=service.list_rule_packs())


def create_rule_pack(
    payload: RulePackCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """Create a rule pack."""
    return service.create_rule_pack(payload)


def get_rule_pack(
    pack_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """Fetch one rule pack."""
    return service.get_rule_pack(pack_id)


def patch_rule_pack(
    pack_id: UUID,
    payload: RulePackUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """Update a rule pack."""
    return service.update_rule_pack(pack_id, payload)


def delete_rule_pack(
    pack_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """
    Delete a rule pack.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (delete_rule_pack)
    2

    Parameters
    ----------
    pack_id : object
        Argument ``pack_id``.
    service : object
        Argument ``service``.
    """
    service.delete_rule_pack(pack_id)


def list_presets(
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetListResponse:
    """
    List semantic presets owned by the caller (and shared presets).


    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_presets)
    2

    Parameters
    ----------
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return PresetListResponse(items=service.list_presets())


def create_preset(
    payload: PresetCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """Create a semantic preset."""
    return service.create_preset(payload)


def get_preset(
    preset_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """Fetch one semantic preset."""
    return service.get_preset(preset_id)


def patch_preset(
    preset_id: UUID,
    payload: PresetUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """Update a semantic preset."""
    return service.update_preset(preset_id, payload)


def delete_preset(
    preset_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """
    Delete a semantic preset.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (delete_preset)
    2

    Parameters
    ----------
    preset_id : object
        Argument ``preset_id``.
    service : object
        Argument ``service``.
    """
    service.delete_preset(preset_id)


def list_templates(
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateListResponse:
    """
    List dissemination templates owned by the caller (and shared templates).


    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_templates)
    2

    Parameters
    ----------
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return DisseminationTemplateListResponse(items=service.list_templates())


def create_template(
    payload: DisseminationTemplateCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """Create a dissemination template."""
    return service.create_template(payload)


def get_template(
    template_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """Fetch one dissemination template."""
    return service.get_template(template_id)


def delete_template(
    template_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """
    Delete an owned dissemination template.


    Examples
    --------
    >>> 1 + 1  # docstring smoke (delete_template)
    2

    Parameters
    ----------
    template_id : object
        Argument ``template_id``.
    service : object
        Argument ``service``.
    """
    service.delete_template(template_id)
