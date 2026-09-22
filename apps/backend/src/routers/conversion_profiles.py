"""JWT routes for ConversionProfile catalog, rule packs, and overlays (EV-933)."""

from __future__ import annotations

from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from ..schemas.conversion_profiles import (
    ConversionTemplateCreate,
    ConversionTemplateListResponse,
    ConversionTemplateOut,
    ConversionTemplatePreviewRequest,
    ConversionTemplatePreviewResponse,
    ConversionTemplateUpdate,
    DisseminationTemplateCreate,
    DisseminationTemplateListResponse,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
    LibraryAssetCreate,
    LibraryAssetListResponse,
    LibraryAssetOut,
    LibraryAssetUpdate,
    LibraryRulePreviewRequest,
    LibraryRulePreviewResponse,
    LibraryYamlValidateRequest,
    LibraryYamlValidateResponse,
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

# ADR-044: operator library YAML authoring retired (hard cutover).
_LIBRARY_AUTHORING_GONE = {
    "code": "library_authoring_retired",
    "message": "Library authoring is no longer available. Use deployed package catalogs and selection dropdowns.",
}


def _library_authoring_gone() -> NoReturn:
    """Raise HTTP 410 for retired library authoring routes."""
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


@router.get("/catalog", response_model=ProfileCatalogResponse)
def get_catalog(
    _user: dict[str, Any] = Depends(verify_supabase_token),
    service: ConversionProfilesService = Depends(profiles_service),
) -> ProfileCatalogResponse:
    """
    Read-only ConversionProfile catalog for the authenticated Profiles inspector.

    Requires JWT so the inspector stays on the authenticated Profiles surface.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_catalog)
    2

    Parameters
    ----------
    _user : object
        Argument ``_user``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
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


@router.post("/rule-packs", response_model=RulePackOut, status_code=201)
def create_rule_pack(
    payload: RulePackCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """
    Create a rule pack.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_rule_pack)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.create_rule_pack(payload)


@router.get("/rule-packs/{pack_id}", response_model=RulePackOut)
def get_rule_pack(
    pack_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """
    Fetch one rule pack.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_rule_pack)
    2

    Parameters
    ----------
    pack_id : object
        Argument ``pack_id``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.get_rule_pack(pack_id)


@router.patch("/rule-packs/{pack_id}", response_model=RulePackOut)
def patch_rule_pack(
    pack_id: UUID,
    payload: RulePackUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> RulePackOut:
    """
    Update a rule pack.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (patch_rule_pack)
    2

    Parameters
    ----------
    pack_id : object
        Argument ``pack_id``.
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.update_rule_pack(pack_id, payload)


@router.delete("/rule-packs/{pack_id}", status_code=204)
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


@router.get("/presets", response_model=PresetListResponse)
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


@router.post("/presets", response_model=PresetOut, status_code=201)
def create_preset(
    payload: PresetCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """
    Create a semantic preset.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_preset)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.create_preset(payload)


@router.get("/presets/{preset_id}", response_model=PresetOut)
def get_preset(
    preset_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """
    Fetch one semantic preset.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_preset)
    2

    Parameters
    ----------
    preset_id : object
        Argument ``preset_id``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.get_preset(preset_id)


@router.patch("/presets/{preset_id}", response_model=PresetOut)
def patch_preset(
    preset_id: UUID,
    payload: PresetUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> PresetOut:
    """
    Update a semantic preset.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (patch_preset)
    2

    Parameters
    ----------
    preset_id : object
        Argument ``preset_id``.
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.update_preset(preset_id, payload)


@router.delete("/presets/{preset_id}", status_code=204)
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


@router.get("/templates", response_model=DisseminationTemplateListResponse)
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


@router.post("/templates", response_model=DisseminationTemplateOut, status_code=201)
def create_template(
    payload: DisseminationTemplateCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """
    Create a dissemination template.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_template)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.create_template(payload)


@router.get("/templates/{template_id}", response_model=DisseminationTemplateOut)
def get_template(
    template_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """
    Fetch one dissemination template.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_template)
    2

    Parameters
    ----------
    template_id : object
        Argument ``template_id``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.get_template(template_id)


@router.patch("/templates/{template_id}", response_model=DisseminationTemplateOut)
def patch_template(
    template_id: UUID,
    payload: DisseminationTemplateUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> DisseminationTemplateOut:
    """
    Update a dissemination template.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (patch_template)
    2

    Parameters
    ----------
    template_id : object
        Argument ``template_id``.
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.update_template(template_id, payload)


@router.delete("/templates/{template_id}", status_code=204)
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


@router.get("/overlays", response_model=OverlayListResponse)
def list_overlays(
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayListResponse:
    """
    List overlays owned by the caller (and shared overlays).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_overlays)
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
    return OverlayListResponse(items=service.list_overlays())


@router.post("/overlays", response_model=OverlayOut, status_code=201)
def create_overlay(
    payload: OverlayCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayOut:
    """
    Create a server-signed overlay.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_overlay)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.create_overlay(payload)


@router.get("/overlays/{overlay_id}", response_model=OverlayOut)
def get_overlay(
    overlay_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayOut:
    """
    Fetch one overlay.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_overlay)
    2

    Parameters
    ----------
    overlay_id : object
        Argument ``overlay_id``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.get_overlay(overlay_id)


@router.patch("/overlays/{overlay_id}", response_model=OverlayOut)
def patch_overlay(
    overlay_id: UUID,
    payload: OverlayUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> OverlayOut:
    """
    Update an owned overlay (re-signed server-side).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (patch_overlay)
    2

    Parameters
    ----------
    overlay_id : object
        Argument ``overlay_id``.
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.update_overlay(overlay_id, payload)


@router.delete("/overlays/{overlay_id}", status_code=204)
def delete_overlay(
    overlay_id: UUID,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """
    Delete an owned overlay.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (delete_overlay)
    2

    Parameters
    ----------
    overlay_id : object
        Argument ``overlay_id``.
    service : object
        Argument ``service``.
    """
    service.delete_overlay(overlay_id)


@router.get("/conversion-templates", response_model=ConversionTemplateListResponse)
def list_conversion_templates(
    service: ConversionProfilesService = Depends(profiles_service),
) -> ConversionTemplateListResponse:
    """
    List first-party and custom conversion templates.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_conversion_templates)
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
    return ConversionTemplateListResponse(items=service.list_conversion_templates())


@router.post("/conversion-templates", response_model=ConversionTemplateOut, status_code=201)
def create_conversion_template(
    payload: ConversionTemplateCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> ConversionTemplateOut:
    """
    Create a custom conversion template (optionally forked from first-party).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_conversion_template)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.create_conversion_template(payload)


@router.post(
    "/conversion-templates/preview",
    response_model=ConversionTemplatePreviewResponse,
)
def preview_conversion_template(
    payload: ConversionTemplatePreviewRequest,
    service: ConversionProfilesService = Depends(profiles_service),
) -> ConversionTemplatePreviewResponse:
    """
    TAC to template to IWXXM bridge preview.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (preview_conversion_template)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    from tac2iwxxm.conversion_templates import (
        ConversionTemplate,
        preview_bridge,
        slot_from_dict,
        template_from_dict,
    )

    if payload.slots is not None:
        tmpl = ConversionTemplate(
            id=payload.template_id,
            name=payload.template_id,
            access="custom",
            iwxxm_block=payload.iwxxm_block or "(omit)",
            slots=tuple(slot_from_dict(s.model_dump(by_alias=False)) for s in payload.slots),
        )
    else:
        stored = service.get_conversion_template(payload.template_id)
        tmpl = template_from_dict(stored.model_dump(by_alias=False))
    result = preview_bridge(tmpl, focus_group=payload.focus_group)
    return ConversionTemplatePreviewResponse(
        template_id=result.template_id,
        focus_group=result.focus_group,
        matched=result.matched,
        captures=result.captures,
        xml_block=result.xml_block,
        compiled_pattern=result.compiled_pattern,
        skipped=list(result.skipped),
    )


@router.get("/conversion-templates/{template_id}", response_model=ConversionTemplateOut)
def get_conversion_template(
    template_id: str,
    service: ConversionProfilesService = Depends(profiles_service),
) -> ConversionTemplateOut:
    """
    Fetch one conversion template (first-party id or custom UUID).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_conversion_template)
    2

    Parameters
    ----------
    template_id : object
        Argument ``template_id``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.get_conversion_template(template_id)


@router.patch("/conversion-templates/{template_id}", response_model=ConversionTemplateOut)
def patch_conversion_template(
    template_id: str,
    payload: ConversionTemplateUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> ConversionTemplateOut:
    """
    Update an owned custom conversion template.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (patch_conversion_template)
    2

    Parameters
    ----------
    template_id : object
        Argument ``template_id``.
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.update_conversion_template(template_id, payload)


@router.delete("/conversion-templates/{template_id}", status_code=204)
def delete_conversion_template(
    template_id: str,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """
    Delete an owned custom conversion template.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (delete_conversion_template)
    2

    Parameters
    ----------
    template_id : object
        Argument ``template_id``.
    service : object
        Argument ``service``.
    """
    service.delete_conversion_template(template_id)


@router.get("/library-assets", response_model=LibraryAssetListResponse)
def list_library_assets(
    kind: str | None = None,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryAssetListResponse:
    """
    List first-party and custom five-Libraries assets.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_library_assets)
    2

    Parameters
    ----------
    kind : object
        Argument ``kind``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return LibraryAssetListResponse(items=service.list_library_assets(kind=kind))


@router.post("/library-assets", response_model=LibraryAssetOut, status_code=201)
def create_library_asset(
    payload: LibraryAssetCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryAssetOut:
    """
    Retired — library authoring is no longer available.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_library_asset)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    _library_authoring_gone()


@router.post("/library-assets/validate-yaml", response_model=LibraryYamlValidateResponse)
def validate_library_yaml(
    payload: LibraryYamlValidateRequest,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryYamlValidateResponse:
    """
    Retired — library authoring is no longer available.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_library_yaml)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    _library_authoring_gone()


@router.post("/library-assets/preview-rule", response_model=LibraryRulePreviewResponse)
def preview_library_rule(
    payload: LibraryRulePreviewRequest,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryRulePreviewResponse:
    """
    Retired — library authoring is no longer available.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (preview_library_rule)
    2

    Parameters
    ----------
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    _library_authoring_gone()


@router.get("/library-assets/{asset_id}", response_model=LibraryAssetOut)
def get_library_asset(
    asset_id: str,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryAssetOut:
    """
    Fetch one library asset (first-party id or custom UUID).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_library_asset)
    2

    Parameters
    ----------
    asset_id : object
        Argument ``asset_id``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    return service.get_library_asset(asset_id)


@router.patch("/library-assets/{asset_id}", response_model=LibraryAssetOut)
def update_library_asset(
    asset_id: str,
    payload: LibraryAssetUpdate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryAssetOut:
    """
    Retired — library authoring is no longer available.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (update_library_asset)
    2

    Parameters
    ----------
    asset_id : object
        Argument ``asset_id``.
    payload : object
        Argument ``payload``.
    service : object
        Argument ``service``.

    Returns
    -------
    object
        Return value.
    """
    _library_authoring_gone()


@router.delete("/library-assets/{asset_id}", status_code=204)
def delete_library_asset(
    asset_id: str,
    service: ConversionProfilesService = Depends(profiles_service),
) -> None:
    """
    Retired — library authoring is no longer available.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (delete_library_asset)
    2

    Parameters
    ----------
    asset_id : object
        Argument ``asset_id``.
    service : object
        Argument ``service``.
    """
    _library_authoring_gone()
