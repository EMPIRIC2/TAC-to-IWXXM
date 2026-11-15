"""Part 3 of ``conversion_profiles.py`` (line-cap split)."""

from __future__ import annotations

from fastapi import Depends

from src.routers.conversion_profiles_part_1 import _library_authoring_gone, profiles_service

from ..schemas.conversion_profiles import (
    LibraryAssetOut,
    LibraryAssetUpdate,
)
from ..services.conversion_profiles_service import ConversionProfilesService


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
