"""IWXXM version and schema metadata routes (EV-037 TD-3b)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["Conversion"])


@router.get("/versions")
def get_supported_versions() -> object:
    """Get list of supported IWXXM versions."""
    try:
        from src.config.iwxxm_versions import DEFAULT_VERSION, DEPRECATED_VERSIONS, SUPPORTED_VERSIONS
    except ImportError:  # pragma: no cover - Docker/local import path mirror
        from config.iwxxm_versions import DEFAULT_VERSION, DEPRECATED_VERSIONS, SUPPORTED_VERSIONS

    versions_list: list[Any] = []
    for version, config in SUPPORTED_VERSIONS.items():
        versions_list.append(
            {
                "version": version,
                "name": config.get("name", ""),
                "status": config.get("status", ""),
                "release_date": config.get("release_date", ""),
                "wmo_amendment": config.get("wmo_amendment", 0),
            }
        )

    return {
        "default_version": DEFAULT_VERSION,
        "supported_versions": sorted(versions_list, key=lambda x: x["release_date"], reverse=True),
        "notes": {"2025-1": "Version 2025-1 does not exist; requests are auto-remapped to 2025-2"},
        "deprecated_versions": list(DEPRECATED_VERSIONS.keys()),
    }


@router.get("/schema-status")
def get_schema_status() -> object:
    """Get comprehensive schema status including RC versions and mirroring info."""
    try:
        from src.config.iwxxm_versions import DEFAULT_VERSION, get_all_versions_with_metadata, get_versions_by_channel
    except ImportError:  # pragma: no cover - Docker/local import path mirror
        from config.iwxxm_versions import DEFAULT_VERSION, get_all_versions_with_metadata, get_versions_by_channel

    stable_versions = get_versions_by_channel("stable")
    rc_versions = get_versions_by_channel("rc")
    all_versions = get_versions_by_channel("all")
    all_metadata = get_all_versions_with_metadata()

    metadata_summary: dict[str, Any] = {}
    for version, data in all_metadata.items():
        discovery_meta = data.get("discovery_metadata", {})
        metadata_summary[version] = {
            "name": data.get("name", f"IWXXM {version}"),
            "channel": discovery_meta.get("channel", "stable"),
            "status": data.get("status", "unknown"),
            "discovered": discovery_meta.get("discovered", ""),
            "source_url": discovery_meta.get("source_url", ""),
            "mirrored": discovery_meta.get("mirrored", False),
        }
        if "RC" in version.upper():
            metadata_summary[version]["promoted_to_stable"] = data.get("promoted_to_stable")

    try:
        from iwxxm_validate.ca_eccc_bundle import (
            CA_ECCC_IWXXM_VERSION,
            ca_eccc_bundle_available,
        )
    except ImportError:  # pragma: no cover - Docker/local import path mirror
        ca_eccc_iwxxm_version = "3.0.0"

        def ca_eccc_bundle_available(
            *,
            iwxxm_version: str = ca_eccc_iwxxm_version,
            extension_tag: str = "3.0",
        ) -> bool:
            """Return False when the Canadian extension bundle cannot be imported."""
            return False
    else:
        ca_eccc_iwxxm_version = CA_ECCC_IWXXM_VERSION

    return {
        "stable": stable_versions,
        "rc": rc_versions,
        "all": all_versions,
        "default": DEFAULT_VERSION,
        "metadata": metadata_summary,
        "profile_pins": {
            "ca_eccc": {
                "iwxxm_version": ca_eccc_iwxxm_version,
                "extension_bundle_available": ca_eccc_bundle_available(),
            },
        },
    }
