"""Part 2 of ``conversion_profiles.py`` (line-cap split)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends

from src.routers.conversion_profiles_part_1 import profiles_service, router

from ..schemas.conversion_profiles import (
    ConversionTemplateCreate,
    ConversionTemplateListResponse,
    ConversionTemplateOut,
    ConversionTemplatePreviewRequest,
    ConversionTemplatePreviewResponse,
    ConversionTemplateUpdate,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
    OverlayCreate,
    OverlayListResponse,
    OverlayOut,
    OverlayUpdate,
)
from ..services.conversion_profiles_service import ConversionProfilesService


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
