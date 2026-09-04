"""Load docs/domain/profiles/catalog.yaml for ConversionProfile inspector (EV-933)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import yaml
from fastapi import HTTPException, status

from ..schemas.conversion_profiles import ProfileCatalogEntry, ProfileCatalogResponse

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_CATALOG = _REPO_ROOT / "docs" / "domain" / "profiles" / "catalog.yaml"


def catalog_path() -> Path:
    """
    Resolve catalog.yaml path.

    Returns
    -------
    Path
        Absolute path to the profile catalog.
    """
    override = (os.environ.get("PROFILE_CATALOG_PATH") or "").strip()
    if override:
        return Path(override)
    return _DEFAULT_CATALOG


@lru_cache(maxsize=1)
def _load_raw(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile catalog unavailable",
        )
    loaded: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile catalog malformed",
        )
    return cast(dict[str, Any], loaded)


def _as_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in cast(list[object], value)]


def _as_str_dict(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(k): v for k, v in cast(dict[object, object], value).items()}


def load_profile_catalog() -> ProfileCatalogResponse:
    """
    Project catalog.yaml into the ConversionProfile inspector response shape.

    Returns
    -------
    ProfileCatalogResponse
        Read-only catalog entries (no secrets).
    """
    raw = _load_raw(str(catalog_path().resolve()))
    profiles_obj: object = raw.get("profiles") or []
    if not isinstance(profiles_obj, list):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile catalog malformed",
        )
    profiles_raw = cast(list[object], profiles_obj)
    entries: list[ProfileCatalogEntry] = []
    for item in profiles_raw:
        if not isinstance(item, dict):
            continue
        row = cast(dict[str, Any], item)
        entry_id = _as_str(row.get("id")) or ""
        entries.append(
            ProfileCatalogEntry(
                id=entry_id,
                kind=_as_str(row.get("kind")) or "",
                status=_as_str(row.get("status")),
                priority=_as_str(row.get("priority")),
                products=_as_str_list(row.get("products")),
                legacy_alias=_as_str(row.get("legacy_alias")),
                emit_key=_as_str(row.get("emit_key")),
                vendor_pins=_as_str_dict(row.get("vendor_pins")),
                implementation=_as_str_dict(row.get("implementation")),
            )
        )
    return ProfileCatalogResponse(
        schema_version=cast(int | str | None, raw.get("schema_version")),
        profiles=[e for e in entries if e.id],
    )


def clear_catalog_cache() -> None:
    """Clear LRU cache (tests)."""
    _load_raw.cache_clear()
