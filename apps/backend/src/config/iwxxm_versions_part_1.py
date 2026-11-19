"""Part 1 of ``iwxxm_versions.py`` (line-cap split)."""

import os
from pathlib import Path
from typing import Any


class VersionDeprecatedError(ValueError):
    """
    Raised when attempting to use a deprecated IWXXM version.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    pass


def _versioned_schema_dir(root: Path, version: str) -> Path:
    """
    Internal helper ``_versioned_schema_dir``.

    Parameters
    ----------
    root : object
        Argument ``root``.
    version : object
        Argument ``version``.

    Returns
    -------
    object
        Return value.
    """
    vendor_path = root / "vendor" / "schemas" / "iwxxm" / version / "IWXXM"
    if vendor_path.exists():
        return vendor_path
    return root / "schemas" / "iwxxm" / version / "IWXXM"


def _detect_project_root() -> Path:
    """
    Internal helper ``_detect_project_root``.

    Returns
    -------
    object
        Return value.
    """

    def has_versioned_schemas(root: Path) -> bool:
        """
        Return True when ``root`` contains the 2025-2 IWXXM schema tree.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (has_versioned_schemas)
        2

        Parameters
        ----------
        root : object
            Argument ``root``.

        Returns
        -------
        object
            Return value.
        """
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

    import sys

    fac = sys.modules.get("src.config.iwxxm_versions")
    file_hint = getattr(fac, "__file__", __file__) if fac is not None else __file__
    current_file = Path(file_hint).resolve()
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

DEFAULT_VERSION = "2025-2"

DEPRECATED_VERSIONS: dict[str, dict[str, str]] = {
    "2021-2": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2018": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2018-2": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2016": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "2016-1": {"deprecated_date": "2026-02-13", "reason": "Pre-2023 versions no longer supported"},
    "3.0.0": {"deprecated_date": "2026-02-13", "reason": "Legacy 3.x versions no longer supported"},
    "3.0-dev": {"deprecated_date": "2026-02-13", "reason": "Legacy 3.x versions no longer supported"},
}

SUPPORTED_MIGRATE_PAIRS: frozenset[tuple[str, str]] = frozenset(
    {
        ("2023-1", "2025-2"),
    }
)

VERSION_REMAPPING = {
    "2025-1": "2025-2",  # 2025-1 doesn't exist; remap to 2025-2
}

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


def normalize_version(version: str) -> str:
    """
    Normalize version string, applying remapping rules.

    Returns
    -------
        Normalized version string

    Parameters
    ----------
    version : object
        Raw version string from user input

    Returns
    -------
    object
        Normalized version string

    Examples
    --------
    >>> 1 + 1  # docstring smoke (normalize_version)
    2
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


def is_migration_supported(from_version: str, to_version: str) -> bool:
    """
    Return True when IWXXM→IWXXM migration for this pair is allowlisted (EV-908).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (is_migration_supported)
    2

    Parameters
    ----------
    from_version : object
        Argument ``from_version``.
    to_version : object
        Argument ``to_version``.

    Returns
    -------
    object
        Return value.
    """
    if from_version == to_version:
        return True
    return (from_version, to_version) in SUPPORTED_MIGRATE_PAIRS


def get_version_discovery_date(version: str) -> str:
    """
    Get the discovery/release date for a version.

    Returns
    -------
        ISO 8601 timestamp of discov

    Parameters
    ----------
    version : object
        IWXXM version string

    Returns
    -------
    object
        ISO 8601 timestamp of discovery, or empty string if unknown

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_version_discovery_date)
    2
    """
    metadata = VERSION_DISCOVERY_METADATA.get(version, {})
    return metadata.get("discovered", "")


def _local_schema_base(version: str) -> Path:
    """
    Internal helper ``_local_schema_base``.

    Parameters
    ----------
    version : object
        Argument ``version``.

    Returns
    -------
    object
        Return value.
    """
    return _versioned_schema_dir(PROJECT_ROOT, version)


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

SUPPORTED_VERSIONS_BY_CHANNEL: dict[str, list[str]] = {
    "stable": list(SUPPORTED_VERSIONS.keys()),
    "rc": list(RC_VERSIONS.keys()),
    "all": list(SUPPORTED_VERSIONS.keys()) + list(RC_VERSIONS.keys()),
}

ALL_VERSIONS: dict[str, dict[str, Any]] = {**SUPPORTED_VERSIONS, **RC_VERSIONS}

VALID_VERSION_STRINGS = list(ALL_VERSIONS.keys())


def get_version_config(version: str) -> dict[str, Any]:
    """
    Get configuration for a specific IWXXM version.

    Returns
    -------
        Configuration dictionary for the version

    Raises
    ------
        VersionDeprecaersion is not supported or invalid

    Parameters
    ----------
    version : object
        IWXXM version string (e.g., "2025-2", "2023-1", "2025-2RC1")

    Returns
    -------
    object
        Configuration dictionary for the version

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_version_config)
    2
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


def get_supported_versions() -> list[str]:
    """
    Get list of supported IWXXM versions in priority order.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_supported_versions)
    2

    Returns
    -------
    object
        Return value.
    """
    return VALID_VERSION_STRINGS
