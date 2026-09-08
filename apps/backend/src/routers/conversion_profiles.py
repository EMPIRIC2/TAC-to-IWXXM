"""JWT routes for ConversionProfile catalog, rule packs, and overlays (EV-933)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from ..schemas.conversion_profiles import (
    DisseminationTemplateCreate,
    DisseminationTemplateListResponse,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
    OverlayCreate,
    OverlayListResponse,
    OverlayOut,
    OverlayUpdate,
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
_bearer = HTTPBearer(auto_error=True)


def profiles_service(
    user: dict[str, Any] = Depends(verify_supabase_token),
) -> ConversionProfilesService:
    """Build owner-scoped profiles service from JWT ``sub``."""
    return ConversionProfilesService(str(user.get("sub") or user.get("user_id")))


@router.get("/catalog", response_model=ProfileCatalogResponse)
def get_catalog(
    _user: dict[str, Any] = Depends(verify_supabase_token),
    service: ConversionProfilesService = Depends(profiles_service),
) -> ProfileCatalogResponse:
    """
    Read-only ConversionProfile catalog for the authenticated Profiles inspector.

    Requires JWT so the inspector stays on the authenticated Profiles surface.
    """
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


@router.get("/rule-packs", response_model=RulePackListResponse)
def list_rule_packs(
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackListResponse:
    """List rule packs owned by the caller."""
    return RulePackListResponse(items=service.list_rule_packs())


@router.post("/rule-packs", response_model=RulePackOut, status_code=201)
def create_rule_pack(
    payload: RulePackCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """Create a rule pack."""
    return service.create_rule_pack(payload)


@router.get("/rule-packs/{pack_id}", response_model=RulePackOut)
def get_rule_pack(
    pack_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """Fetch one rule pack."""
    return service.get_rule_pack(pack_id)


@router.patch("/rule-packs/{pack_id}", response_model=RulePackOut)
def patch_rule_pack(
    pack_id: UUID,
    payload: RulePackUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """Update a rule pack."""
    return service.update_rule_pack(pack_id, payload)


@router.delete("/rule-packs/{pack_id}", status_code=204)
def delete_rule_pack(
    pack_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """Delete a rule pack."""
    service.delete_rule_pack(pack_id)


@router.get("/presets", response_model=PresetListResponse)
def list_presets(
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetListResponse:
    """List semantic presets owned by the caller (and shared presets)."""
    return PresetListResponse(items=service.list_presets())


@router.post("/presets", response_model=PresetOut, status_code=201)
def create_preset(
    payload: PresetCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """Create a semantic preset."""
    return service.create_preset(payload)


@router.get("/presets/{preset_id}", response_model=PresetOut)
def get_preset(
    preset_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """Fetch one semantic preset."""
    return service.get_preset(preset_id)


@router.patch("/presets/{preset_id}", response_model=PresetOut)
def patch_preset(
    preset_id: UUID,
    payload: PresetUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """Update a semantic preset."""
    return service.update_preset(preset_id, payload)


@router.delete("/presets/{preset_id}", status_code=204)
def delete_preset(
    preset_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """Delete a semantic preset."""
    service.delete_preset(preset_id)


@router.get("/templates", response_model=DisseminationTemplateListResponse)
def list_templates(
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateListResponse:
    """List dissemination templates owned by the caller (and shared templates)."""
    return DisseminationTemplateListResponse(items=service.list_templates())


@router.post("/templates", response_model=DisseminationTemplateOut, status_code=201)
def create_template(
    payload: DisseminationTemplateCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """Create a dissemination template."""
    return service.create_template(payload)


@router.get("/templates/{template_id}", response_model=DisseminationTemplateOut)
def get_template(
    template_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """Fetch one dissemination template."""
    return service.get_template(template_id)


@router.patch("/templates/{template_id}", response_model=DisseminationTemplateOut)
def patch_template(
    template_id: UUID,
    payload: DisseminationTemplateUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """Update a dissemination template."""
    return service.update_template(template_id, payload)


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(
    template_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """Delete an owned dissemination template."""
    service.delete_template(template_id)


@router.get("/overlays", response_model=OverlayListResponse)
def list_overlays(
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayListResponse:
    """List overlays owned by the caller (and shared overlays)."""
    return OverlayListResponse(items=service.list_overlays())


@router.post("/overlays", response_model=OverlayOut, status_code=201)
def create_overlay(
    payload: OverlayCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayOut:
    """Create a server-signed overlay."""
    return service.create_overlay(payload)


@router.get("/overlays/{overlay_id}", response_model=OverlayOut)
def get_overlay(
    overlay_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayOut:
    """Fetch one overlay."""
    return service.get_overlay(overlay_id)


@router.patch("/overlays/{overlay_id}", response_model=OverlayOut)
def patch_overlay(
    overlay_id: UUID,
    payload: OverlayUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayOut:
    """Update an owned overlay (re-signed server-side)."""
    return service.update_overlay(overlay_id, payload)


@router.delete("/overlays/{overlay_id}", status_code=204)
def delete_overlay(
    overlay_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """Delete an owned overlay."""
    service.delete_overlay(overlay_id)
