"""Part 2 of ``iwxxm_versions.py`` (line-cap split)."""

from pathlib import Path
from typing import Any

from .iwxxm_versions_part_1 import (
    ALL_VERSIONS,
    PROFILE_SCOPED_VERSIONS,
    PROJECT_ROOT,
    RC_VERSIONS,
    SUPPORTED_VERSIONS,
    SUPPORTED_VERSIONS_BY_CHANNEL,
    VALID_VERSION_STRINGS,
    VERSION_DISCOVERY_METADATA,
    VersionDeprecatedError,
    get_version_config,
    normalize_version,
)


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

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_version_config_for_emit_profile)
    2
    """
    normalized = normalize_version(version)
    try:
        return get_version_config(normalized)
    except VersionDeprecatedError:
        scoped = PROFILE_SCOPED_VERSIONS.get(normalized)
        if scoped and emit_profile in scoped.get("emit_profiles", frozenset()):
            return scoped
        raise


def resolve_schema_file(version: str, file_type: str = "xsd") -> Path:
    """
    Resolve file path for schema, Schematron, or codelists.

    Returns
    -------
        Path to the requested file/directory

    Raises
    ------
        ValueError: If version or file_type is in

    Parameters
    ----------
    version : object
        IWXXM version string
    file_type : object
        Type of file ("xsd", "schematron", "codelists")

    Returns
    -------
    object
        Path to the requested file/directory

    Examples
    --------
    >>> 1 + 1  # docstring smoke (resolve_schema_file)
    2
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

    Returns
    -------
        List of breaking change definitions with XPath and action

    Parameters
    ----------
    from_version : object
        Source IWXXM version
    to_version : object
        Target IWXXM version

    Returns
    -------
    object
        List of breaking change definitions with XPath and action

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_breaking_changes)
    2
    """
    to_config = get_version_config(to_version)
    changes = to_config.get("breaking_changes_from_prior", {})

    return changes.get(from_version, [])


def get_namespace_uri(version: str) -> str:
    """
    Get XML namespace URI for a specific IWXXM version.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_namespace_uri)
    2

    Parameters
    ----------
    version : object
        Argument ``version``.

    Returns
    -------
    object
        Return value.
    """
    config = get_version_config(version)
    return config["namespace_uri"]


def get_schema_url(version: str) -> str:
    """
    Get remote schema URL for a specific IWXXM version.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_schema_url)
    2

    Parameters
    ----------
    version : object
        Argument ``version``.

    Returns
    -------
    object
        Return value.
    """
    config = get_version_config(version)
    return config["schema_url"]


def is_version_supported(version: str) -> bool:
    """
    Check if a version string is supported (after normalization).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (is_version_supported)
    2

    Parameters
    ----------
    version : object
        Argument ``version``.

    Returns
    -------
    object
        Return value.
    """
    try:
        normalize_version(version)
        get_version_config(version)
        return True
    except (ValueError, KeyError):
        return False


def is_rc_version(version: str) -> bool:
    """
    Check if a version string is a Release Candidate.

    Returns
    -------
        True if version is an RC, Fa

    Parameters
    ----------
    version : object
        IWXXM version string

    Returns
    -------
    object
        True if version is an RC, False otherwise

    Examples
    --------
    >>> 1 + 1  # docstring smoke (is_rc_version)
    2
    """
    return version in RC_VERSIONS or "RC" in version.upper()


def get_version_channel(version: str) -> str:
    """
    Get the channel for a specific version.

    Returns
    -------
        Channel string: "stable", "r

    Parameters
    ----------
    version : object
        IWXXM version string

    Returns
    -------
    object
        Channel string: "stable", "rc", or "unknown"

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_version_channel)
    2
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

    Returns
    -------
        List of version strings for the specified chan

    Parameters
    ----------
    channel : object
        Channel filter ("stable", "rc", "all")

    Returns
    -------
    object
        List of version strings for the specified channel

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_versions_by_channel)
    2
    """
    return SUPPORTED_VERSIONS_BY_CHANNEL.get(channel, [])


def register_rc_version(version: str, config: dict[str, Any]) -> None:
    """
    Register a newly discovered RC version.

    This is called by the schema discovery service when a new RC is detected.

    Parameters
    ----------
    version : object
        RC version string (e.g., "2025-2RC1")
    config : object
        Configuration dictionary for the RC version

    Examples
    --------
    >>> 1 + 1  # docstring smoke (register_rc_version)
    2
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

    Returns
    -------
    object
        Dictionary mapping version strings to combined config + metadata

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_all_versions_with_metadata)
    2
    """
    result: dict[str, Any] = {}
    for version, config in ALL_VERSIONS.items():
        result[version] = {**config, "discovery_metadata": VERSION_DISCOVERY_METADATA.get(version, {})}
    return result
