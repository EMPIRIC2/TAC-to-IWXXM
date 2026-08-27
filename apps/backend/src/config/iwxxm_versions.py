"""
IWXXM Version Configuration

Defines supported IWXXM versions, their namespaces, schema locations,
and version-specific metadata for dynamic version switching.
"""

import os
from pathlib import Path
from typing import Any


# Custom exception for deprecated versions
class VersionDeprecatedError(ValueError):
    """Raised when attempting to use a deprecated IWXXM version."""

    pass


def _versioned_schema_dir(root: Path, version: str) -> Path:
    """Return the IWXXM schema directory for a version under root."""
    vendor_path = root / "vendor" / "schemas" / "iwxxm" / version / "IWXXM"
    if vendor_path.exists():
        return vendor_path
    return root / "schemas" / "iwxxm" / version / "IWXXM"


def _local_schema_base(version: str) -> Path:
    """Resolve schema base for a version (vendor snapshot preferred over legacy symlink)."""
    return _versioned_schema_dir(PROJECT_ROOT, version)


# Project root path
def _detect_project_root() -> Path:
    """Detect project root across local/devcontainer and deployment layouts."""

    def has_versioned_schemas(root: Path) -> bool:
        return _versioned_schema_dir(root, "2025-2").exists()

    env_project_root = os.getenv("IWXXM_PROJECT_ROOT")
    if env_project_root:
        candidate = Path(env_project_root).expanduser().resolve()
        if candidate.exists() and has_versioned_schemas(candidate):
            return candidate

    env_schemas_root = os.getenv("IWXXM_SCHEMAS_ROOT")
    if env_schemas_root:
        schemas_candidate = Path(env_schemas_root).expanduser().resolve()
        if schemas_candidate.exists():
            if schemas_candidate.name == "iwxxm" and schemas_candidate.parent.name == "schemas":
                root_candidate = schemas_candidate.parent.parent
                if has_versioned_schemas(root_candidate):
                    return root_candidate
            if (schemas_candidate / "iwxxm").exists():
                root_candidate = schemas_candidate.parent
                if has_versioned_schemas(root_candidate):
                    return root_candidate

    current_file = Path(__file__).resolve()
    parents = [current_file.parent, *current_file.parents]

    # Prefer roots that contain actual versioned IWXXM schema directories.
    for parent in parents:
        if has_versioned_schemas(parent):
            return parent

    # Next prefer canonical IWXXM layout (vendor snapshot or legacy symlink).
    for parent in parents:
        if (parent / "vendor" / "schemas" / "iwxxm" / "IWXXM").exists():
            return parent
        if (parent / "schemas" / "iwxxm" / "IWXXM").exists():
            return parent

    # Fallback: any vendor or legacy schemas/iwxxm folder.
    for parent in parents:
        if (parent / "vendor" / "schemas" / "iwxxm").exists():
            return parent
        if (parent / "schemas" / "iwxxm").exists():
            return parent

    return current_file.parent.parent.parent.parent


PROJECT_ROOT = _detect_project_root()

# Default IWXXM version (highest/latest priority)
DEFAULT_VERSION = "2025-2"

# Supported IWXXM versions (in priority order)
SUPPORTED_VERSIONS: dict[str, dict[str, Any]] = {
    "2025-2": {
        "name": "IWXXM 2025-2",
        "release_date": "2025-11-25",
        "wmo_amendment": 82,
        "namespace_uri": "http://icao.int/iwxxm/2025-2",
        "schema_url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        "local_schema_base": _local_schema_base("2025-2"),
        "schema_file": "iwxxm.xsd",
        "schematron_file": "rule/iwxxm.sch",
        "codelists_dir": "rule",
        "has_measures_xsd": False,
        "split_nil_codelists": True,
        "status": "latest",
        "breaking_changes_from_prior": {
            "2023-1": [
                {
                    "element": "iwxxm:runwayState",
                    "xpath": ".//iwxxm:runwayState",
                    "action": "remove",
                    "reason": "Runway state removed from METAR product in 2025-2",
                },
                {
                    "element": "iwxxm:AerodromeRunwayState",
                    "xpath": ".//iwxxm:AerodromeRunwayState",
                    "action": "remove",
                    "reason": "Runway state complex type removed",
                },
            ]
        },
    },
    "2023-1": {
        "name": "IWXXM 2023-1",
        "release_date": "2023-06-02",
        "wmo_amendment": 78,
        "namespace_uri": "http://icao.int/iwxxm/2023-1",
        "schema_url": "https://schemas.wmo.int/iwxxm/2023-1/iwxxm.xsd",
        "local_schema_base": _local_schema_base("2023-1"),
        "schema_file": "iwxxm.xsd",
        "schematron_file": "rule/iwxxm.sch",
        "codelists_dir": "rule",
        "has_measures_xsd": True,
        "split_nil_codelists": False,
        "status": "previous",
        "breaking_changes_from_prior": {},
    },
}

# Deprecated versions (no longer supported)
DEPRECATED_VERSIONS: dict[str, dict[str, str]] = {
    "2021-2": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2018": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2018-2": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2016": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2016-1": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "3.0.0": {"deprecated_date": "2026-02-13", "reason": "Legacy 3.x versions no longer supported"},
    "3.0-dev": {"deprecated_date": "2026-02-13", "reason": "Legacy 3.x versions no longer supported"},
}

# Profile-scoped IWXXM lines (EV-064 / CA_ECCC) - not in general version picker.
PROFILE_SCOPED_VERSIONS: dict[str, dict[str, Any]] = {
    "3.0.0": {
        "name": "IWXXM 3.0.0 (MSC operational)",
        "namespace_uri": "http://icao.int/iwxxm/3.0",
        "schema_url": "https://schemas.wmo.int/iwxxm/3.0.0/iwxxm.xsd",
        "local_schema_base": _local_schema_base("3.0.0"),
        "schema_file": "iwxxm.xsd",
        "schematron_file": "rule/iwxxm.sch",
        "codelists_dir": "rule",
        "has_measures_xsd": True,
        "split_nil_codelists": False,
        "emit_profiles": frozenset({"ca_eccc"}),
    },
}

# Version remapping (for non-existent or deprecated versions)
VERSION_REMAPPING = {
    "2025-1": "2025-2",  # 2025-1 doesn't exist; remap to 2025-2
}

# RC (Release Candidate) versions - dynamically populated by discovery service
RC_VERSIONS: dict[str, dict[str, Any]] = {
    "2025-2RC2": {
        "name": "IWXXM 2025-2 RC2",
        "release_date": "2026-02-15",  # Current date (detected)
        "wmo_amendment": 82,
        "namespace_uri": "http://icao.int/iwxxm/2025-2",
        "schema_url": "https://schemas.wmo.int/iwxxm/2025-2RC2/iwxxm.xsd",
        "local_schema_base": _local_schema_base("2025-2RC2"),
        "schema_file": "iwxxm.xsd",
        "schematron_file": "rule/iwxxm.sch",
        "codelists_dir": "rule",
        "has_measures_xsd": False,
        "split_nil_codelists": True,
        "status": "rc",
        "base_version": "2025-2",
        "promoted_to_stable": None,
        "breaking_changes_from_prior": {},
    },
    "2025-2RC1": {
        "name": "IWXXM 2025-2 RC1",
        "release_date": "2026-02-10",  # Estimated
        "wmo_amendment": 82,
        "namespace_uri": "http://icao.int/iwxxm/2025-2",
        "schema_url": "https://schemas.wmo.int/iwxxm/2025-2RC1/iwxxm.xsd",
        "local_schema_base": _local_schema_base("2025-2RC1"),
        "schema_file": "iwxxm.xsd",
        "schematron_file": "rule/iwxxm.sch",
        "codelists_dir": "rule",
        "has_measures_xsd": False,
        "split_nil_codelists": True,
        "status": "rc",
        "base_version": "2025-2",
        "promoted_to_stable": None,
        "breaking_changes_from_prior": {},
    },
}

# Version discovery metadata (tracking when versions were discovered)
VERSION_DISCOVERY_METADATA: dict[str, dict[str, Any]] = {
    "2025-2": {
        "discovered": "2025-11-25T00:00:00Z",
        "source": "wmo-im/iwxxm git repository",
        "source_url": "https://github.com/wmo-im/iwxxm/tree/v2025-2",
        "mirrored": True,
        "channel": "stable",
    },
    "2023-1": {
        "discovered": "2023-06-02T00:00:00Z",
        "source": "wmo-im/iwxxm git repository",
        "source_url": "https://github.com/wmo-im/iwxxm/tree/v2023-1",
        "mirrored": True,
        "channel": "stable",
    },
    "2025-2RC2": {
        "discovered": "2026-02-15T00:00:00Z",
        "source": "WMO IWXXM schema directory",
        "source_url": "https://schemas.wmo.int/iwxxm/2025-2RC2/",
        "mirrored": False,
        "channel": "rc",
    },
    "2025-2RC1": {
        "discovered": "2026-02-10T00:00:00Z",
        "source": "WMO IWXXM schema directory",
        "source_url": "https://schemas.wmo.int/iwxxm/2025-2RC1/",
        "mirrored": False,
        "channel": "rc",
    },
}

# Versions grouped by channel (stable, rc, all)
SUPPORTED_VERSIONS_BY_CHANNEL: dict[str, list[str]] = {
    "stable": list(SUPPORTED_VERSIONS.keys()),
    "rc": list(RC_VERSIONS.keys()),
    "all": list(SUPPORTED_VERSIONS.keys()) + list(RC_VERSIONS.keys()),
}

# Combined version registry (stable + RC)
ALL_VERSIONS: dict[str, dict[str, Any]] = {**SUPPORTED_VERSIONS, **RC_VERSIONS}

# API endpoint constants
VALID_VERSION_STRINGS = list(ALL_VERSIONS.keys())


def get_version_config(version: str) -> dict[str, Any]:
    """
    Get configuration for a specific IWXXM version.

    Args:
        version: IWXXM version string (e.g., "2025-2", "2023-1", "2025-2RC1")

    Returns:
        Configuration dictionary for the version

    Raises:
        VersionDeprecatedError: If version is deprecated
        ValueError: If version is not supported or invalid
    """
    # Check if version is deprecated FIRST (immediate rejection)
    if version in DEPRECATED_VERSIONS:
        dep_info = DEPRECATED_VERSIONS[version]
        raise VersionDeprecatedError(
            f"IWXXM version '{version}' is no longer supported as of "
            f"{dep_info['deprecated_date']}. {dep_info['reason']}. "
            f"Supported versions: {VALID_VERSION_STRINGS}"
        )

    # Normalize version (handle remapping)
    normalized = normalize_version(version)

    # Check again after normalization
    if normalized in DEPRECATED_VERSIONS:
        dep_info = DEPRECATED_VERSIONS[normalized]
        raise VersionDeprecatedError(
            f"IWXXM version '{normalized}' is no longer supported as of "
            f"{dep_info['deprecated_date']}. {dep_info['reason']}. "
            f"Supported versions: {VALID_VERSION_STRINGS}"
        )

    # Check both stable and RC versions
    if normalized not in ALL_VERSIONS:
        raise ValueError(f"IWXXM version '{version}' is not supported. Supported versions: {VALID_VERSION_STRINGS}")

    return ALL_VERSIONS[normalized]


def get_version_config_for_emit_profile(version: str, emit_profile: str | None = None) -> dict[str, Any]:
    """
    Resolve IWXXM version config, allowing profile-scoped lines when appropriate.

    Parameters
    ----------
    version :
        IWXXM version string (e.g. ``2025-2``, ``3.0.0``).
    emit_profile :
        tac2iwxxm / iwxxm-validate emit key (e.g. ``ca_eccc``).

    Returns
    -------
    dict
        Version configuration dictionary.

    Raises
    ------
    VersionDeprecatedError
        When the version is deprecated and not allowed for ``emit_profile``.
    ValueError
        When the version is unknown.
    """
    normalized = normalize_version(version)
    try:
        return get_version_config(normalized)
    except VersionDeprecatedError:
        scoped = PROFILE_SCOPED_VERSIONS.get(normalized)
        if scoped and emit_profile in scoped.get("emit_profiles", frozenset()):
            return scoped
        raise


def normalize_version(version: str) -> str:
    """
    Normalize version string, applying remapping rules.

    Args:
        version: Raw version string from user input

    Returns:
        Normalized version string
    """
    if not version:
        return DEFAULT_VERSION

    # Strip whitespace and check again
    version = str(version).strip()
    if not version:
        return DEFAULT_VERSION

    # Apply remapping if exists
    if version in VERSION_REMAPPING:
        return VERSION_REMAPPING[version]

    return version


def get_supported_versions() -> list[str]:
    """Get list of supported IWXXM versions in priority order."""
    return VALID_VERSION_STRINGS


def resolve_schema_file(version: str, file_type: str = "xsd") -> Path:
    """
    Resolve file path for schema, Schematron, or codelists.

    Args:
        version: IWXXM version string
        file_type: Type of file ("xsd", "schematron", "codelists")

    Returns:
        Path to the requested file/directory

    Raises:
        ValueError: If version or file_type is invalid
        FileNotFoundError: If file doesn't exist
    """
    config = get_version_config(version)

    if file_type == "xsd":
        filepath = config["local_schema_base"] / config["schema_file"]
    elif file_type == "schematron":
        filepath = config["local_schema_base"] / config["schematron_file"]
    elif file_type == "codelists":
        filepath = config["local_schema_base"] / config["codelists_dir"]
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    if not filepath.exists():
        fallback_bases = [
            PROJECT_ROOT / "vendor" / "schemas" / "iwxxm" / "IWXXM",
            PROJECT_ROOT / "schemas" / "iwxxm" / "IWXXM",
        ]
        for fallback_base in fallback_bases:
            if file_type == "xsd":
                fallback_path = fallback_base / config["schema_file"]
            elif file_type == "schematron":
                fallback_path = fallback_base / config["schematron_file"]
            else:
                # codelists (only remaining type after outer validation)
                fallback_path = fallback_base / config["codelists_dir"]

            if fallback_path.exists():
                return fallback_path

        raise FileNotFoundError(
            f"Schema file not found: {filepath}. Run vendor sync or set IWXXM_SCHEMAS_ROOT to vendor/schemas/iwxxm."
        )

    return filepath


def get_breaking_changes(from_version: str, to_version: str) -> list[dict[str, Any]]:
    """
    Get list of breaking changes when migrating from one version to another.

    Args:
        from_version: Source IWXXM version
        to_version: Target IWXXM version

    Returns:
        List of breaking change definitions with XPath and action
    """
    to_config = get_version_config(to_version)
    changes = to_config.get("breaking_changes_from_prior", {})

    return changes.get(from_version, [])


def get_namespace_uri(version: str) -> str:
    """Get XML namespace URI for a specific IWXXM version."""
    config = get_version_config(version)
    return config["namespace_uri"]


def get_schema_url(version: str) -> str:
    """Get remote schema URL for a specific IWXXM version."""
    config = get_version_config(version)
    return config["schema_url"]


def is_version_supported(version: str) -> bool:
    """Check if a version string is supported (after normalization)."""
    try:
        normalize_version(version)
        get_version_config(version)
        return True
    except (ValueError, KeyError):
        return False


def is_rc_version(version: str) -> bool:
    """
    Check if a version string is a Release Candidate.

    Args:
        version: IWXXM version string

    Returns:
        True if version is an RC, False otherwise
    """
    return version in RC_VERSIONS or "RC" in version.upper()


def get_version_channel(version: str) -> str:
    """
    Get the channel for a specific version.

    Args:
        version: IWXXM version string

    Returns:
        Channel string: "stable", "rc", or "unknown"
    """
    if version in SUPPORTED_VERSIONS:
        return "stable"
    elif version in RC_VERSIONS:
        return "rc"
    else:
        return "unknown"


def get_versions_by_channel(channel: str = "all") -> list[str]:
    """
    Get list of versions filtered by channel.

    Args:
        channel: Channel filter ("stable", "rc", "all")

    Returns:
        List of version strings for the specified channel
    """
    return SUPPORTED_VERSIONS_BY_CHANNEL.get(channel, [])


def get_version_discovery_date(version: str) -> str:
    """
    Get the discovery/release date for a version.

    Args:
        version: IWXXM version string

    Returns:
        ISO 8601 timestamp of discovery, or empty string if unknown
    """
    metadata = VERSION_DISCOVERY_METADATA.get(version, {})
    return metadata.get("discovered", "")


def register_rc_version(version: str, config: dict[str, Any]) -> None:
    """
    Register a newly discovered RC version.

    This is called by the schema discovery service when a new RC is detected.

    Args:
        version: RC version string (e.g., "2025-2RC1")
        config: Configuration dictionary for the RC version
    """
    RC_VERSIONS[version] = config
    ALL_VERSIONS[version] = config
    SUPPORTED_VERSIONS_BY_CHANNEL["rc"] = list(RC_VERSIONS.keys())
    SUPPORTED_VERSIONS_BY_CHANNEL["all"] = list(ALL_VERSIONS.keys())

    # Update valid version strings
    VALID_VERSION_STRINGS.clear()
    VALID_VERSION_STRINGS.extend(ALL_VERSIONS.keys())


def get_all_versions_with_metadata() -> dict[str, dict[str, Any]]:
    """
    Get all versions with their full configuration and discovery metadata.

    Returns:
        Dictionary mapping version strings to combined config + metadata
    """
    result: dict[str, Any] = {}
    for version, config in ALL_VERSIONS.items():
        result[version] = {**config, "discovery_metadata": VERSION_DISCOVERY_METADATA.get(version, {})}
    return result
