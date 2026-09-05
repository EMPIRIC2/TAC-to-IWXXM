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


_DELTA_MAP: dict[str, list[str]] = {
    "ICAO_2025": [
        "Baseline ICAO/WMO line used for cross-profile comparison.",
    ],
    "US_FAA_NWS": [
        "Adds FAA/NWS national differences on top of the ICAO baseline.",
        "Uses the iwxxm-us schema catalog for United States IWXXM extensions.",
        "Current product slice is METAR, SPECI, SIGMET, and AIRMET.",
    ],
    "CA_ECCC": [
        "Adds Canadian MANOBS and MANAIR rules on top of the ICAO baseline.",
        "Pins the Canadian operational IWXXM 3.0.0 line with iwxxm-ca product schemas.",
        "Covers METAR, SPECI, TAF, AIRMET, SIGMET, and VAA in the current slice.",
    ],
    "AU_BOM": [
        "Thin pack in progress: compare from the ICAO baseline first.",
    ],
    "NZ_CAA_MET": [
        "Thin pack in progress: compare from the ICAO baseline first.",
    ],
}


def _deltas_vs_icao(profile_id: str) -> list[str]:
    return list(
        _DELTA_MAP.get(profile_id, ["Thin pack: reuses the ICAO baseline until a profile-specific extension lands."])
    )[:3]


def _iwxxm_line(profile_id: str, vendor_pins: dict[str, Any]) -> str | None:
    if profile_id == "ICAO_2025":
        return str(vendor_pins.get("iwxxm") or "WMO IWXXM 2025-2")
    if profile_id == "US_FAA_NWS":
        return "WMO IWXXM 2025-2 core + iwxxm-us 3.0"
    if profile_id == "CA_ECCC":
        return "WMO IWXXM 3.0.0 core + iwxxm-ca 3.0"
    if vendor_pins:
        return "; ".join(str(value) for value in vendor_pins.values())
    return None


def load_profile_catalog(
    *,
    rule_pack_counts: dict[str, int] | None = None,
    overlay_counts: dict[str, int] | None = None,
) -> ProfileCatalogResponse:
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
        vendor_pins = _as_str_dict(row.get("vendor_pins"))
        entries.append(
            ProfileCatalogEntry(
                id=entry_id,
                kind=_as_str(row.get("kind")) or "",
                status=_as_str(row.get("status")),
                priority=_as_str(row.get("priority")),
                products=_as_str_list(row.get("products")),
                legacy_alias=_as_str(row.get("legacy_alias")),
                emit_key=_as_str(row.get("emit_key")),
                vendor_pins=vendor_pins,
                implementation=_as_str_dict(row.get("implementation")),
                deltas_vs_icao=_deltas_vs_icao(entry_id),
                iwxxm_line=_iwxxm_line(entry_id, vendor_pins),
                rule_pack_count=None if rule_pack_counts is None else rule_pack_counts.get(entry_id, 0),
                overlay_count=None if overlay_counts is None else overlay_counts.get(entry_id, 0),
            )
        )
    return ProfileCatalogResponse(
        schema_version=cast(int | str | None, raw.get("schema_version")),
        profiles=[e for e in entries if e.id],
    )


def clear_catalog_cache() -> None:
    """Clear LRU cache (tests)."""
    _load_raw.cache_clear()
