"""JWT routes for ConversionProfile catalog, rule packs, and overlays (EV-933)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from ..schemas.conversion_profiles import (
    OverlayCreate,
    OverlayListResponse,
    OverlayOut,
    OverlayUpdate,
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
) -> ProfileCatalogResponse:
    """
    Read-only ConversionProfile catalog for the authenticated Profiles inspector.

    Requires JWT so the inspector stays on the authenticated Profiles surface.
    """
    return load_profile_catalog()


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
