"""Part 2 of ``conversion_profiles.py`` (line-cap split)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends

from src.routers.conversion_profiles_part_1 import _library_authoring_gone, profiles_service

from ..schemas.conversion_profiles import (
    ConversionTemplateCreate,
    ConversionTemplateListResponse,
    ConversionTemplateOut,
    ConversionTemplatePreviewRequest,
    ConversionTemplatePreviewResponse,
    ConversionTemplateUpdate,
    DisseminationTemplateOut,
    DisseminationTemplateUpdate,
    LibraryAssetCreate,
    LibraryAssetListResponse,
    LibraryAssetOut,
    LibraryRulePreviewRequest,
    LibraryRulePreviewResponse,
    LibraryYamlValidateRequest,
    LibraryYamlValidateResponse,
    OverlayCreate,
    OverlayListResponse,
    OverlayOut,
    OverlayUpdate,
)
from ..services.conversion_profiles_service import ConversionProfilesService


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


def create_library_asset(
    payload: LibraryAssetCreate,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryAssetOut:
    """
    Library authoring is no longer available.


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


def validate_library_yaml(
    payload: LibraryYamlValidateRequest,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryYamlValidateResponse:
    """
    Library authoring is no longer available.


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


def preview_library_rule(
    payload: LibraryRulePreviewRequest,
    service: ConversionProfilesService = Depends(profiles_service),
) -> LibraryRulePreviewResponse:
    """
    Library authoring is no longer available.


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
