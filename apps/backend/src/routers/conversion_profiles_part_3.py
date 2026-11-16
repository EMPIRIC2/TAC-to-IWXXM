"""Part 3 of ``conversion_profiles.py`` (line-cap split)."""

from __future__ import annotations

from fastapi import Depends

from ..schemas.conversion_profiles import (
    LibraryAssetCreate,
    LibraryAssetListResponse,
    LibraryAssetOut,
    LibraryAssetUpdate,
    LibraryRulePreviewRequest,
    LibraryRulePreviewResponse,
    LibraryYamlValidateRequest,
    LibraryYamlValidateResponse,
)
from ..services.conversion_profiles_service import ConversionProfilesService
from .conversion_profiles_part_1 import _library_authoring_gone, profiles_service, router


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
    Library authoring is no longer available.


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
    Library authoring is no longer available.


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


@router.post("/library-assets/validate-yaml", response_model=LibraryYamlValidateResponse)
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


@router.post("/library-assets/preview-rule", response_model=LibraryRulePreviewResponse)
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
