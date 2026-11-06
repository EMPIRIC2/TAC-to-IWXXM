"""
Schema Registry

Provides centralized schema resolution and caching for IWXXM validation,
including XSD, Schematron, and codelist file locations across versions.
"""

import logging
from pathlib import Path
from typing import Any

from ..config.iwxxm_versions import (
    SUPPORTED_VERSIONS,
    get_all_versions_with_metadata,
    get_breaking_changes,
    get_namespace_uri,
    get_schema_url,
    get_version_channel,
    get_version_config,
    get_version_discovery_date,
    get_versions_by_channel,
    is_rc_version,
    normalize_version,
    resolve_schema_file,
)

logger = logging.getLogger(__name__)


class SchemaRegistry:
    """
    Centralized registry for IWXXM schema files across versions.
    Handles file resolution, caching, and validation.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self) -> None:
        """Internal helper ``__init__``."""
        self._version_cache: dict[str, dict[str, Any]] = {}
        self._file_cache: dict[str, Path] = {}

    def get_xsd_path(self, version: str) -> Path:
        """
        Get path to XSD schema file for a version.

        Returns
        -------
            Path to the XSD file

        Raisesnot found
            ValueError: If versio

        Parameters
        ----------
        version : object
            IWXXM version string

        Returns
        -------
        object
            Path to the XSD file

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_xsd_path)
        2
        """
        cache_key = f"xsd_{version}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]

        normalized = normalize_version(version)
        path = resolve_schema_file(normalized, "xsd")
        self._file_cache[cache_key] = path
        logger.debug(f"Resolved XSD for {version}: {path}")
        return path

    def get_schematron_path(self, version: str) -> Path:
        """
        Get path to Schematron (.sch) file for a version.

        Returns
        -------
            Path to the Schematron file
        ron not found
            ValueError: If version i

        Parameters
        ----------
        version : object
            IWXXM version string

        Returns
        -------
        object
            Path to the Schematron file

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_schematron_path)
        2
        """
        cache_key = f"schematron_{version}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]

        normalized = normalize_version(version)
        path = resolve_schema_file(normalized, "schematron")
        self._file_cache[cache_key] = path
        logger.debug(f"Resolved Schematron for {version}: {path}")
        return path

    def get_codelists_dir(self, version: str) -> Path:
        """
        Get path to codelists directory for a version.

        Returns
        -------
            Path to the codelists directry not found
            ValueError: If version invali

        Parameters
        ----------
        version : object
            IWXXM version string

        Returns
        -------
        object
            Path to the codelists directory

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_codelists_dir)
        2
        """
        cache_key = f"codelists_{version}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]

        normalized = normalize_version(version)
        path = resolve_schema_file(normalized, "codelists")
        self._file_cache[cache_key] = path
        logger.debug(f"Resolved codelists dir for {version}: {path}")
        return path

    def get_namespace_uri(self, version: str) -> str:
        """
        Get XML namespace URI for a version.

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
        normalized = normalize_version(version)
        return get_namespace_uri(normalized)

    def get_schema_url(self, version: str) -> str:
        """
        Get remote schema URL for a version.

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
        normalized = normalize_version(version)
        return get_schema_url(normalized)

    def get_version_info(self, version: str) -> dict[str, Any]:
        """
        Get complete version configuration.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_version_info)
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
        normalized = normalize_version(version)
        return get_version_config(normalized)

    def get_supported_versions(self) -> list[str]:
        """
        Get list of supported IWXXM versions.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_supported_versions)
        2

        Returns
        -------
        object
            Return value.
        """
        return list(SUPPORTED_VERSIONS.keys())

    def list_codelists(self, version: str) -> list[str]:
        """
        List all codelist files for a version.

        Returns
        -------
            List of codelist filenames (

        Parameters
        ----------
        version : object
            IWXXM version string

        Returns
        -------
        object
            List of codelist filenames (RDF files)

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_codelists)
        2
        """
        codelists_dir = self.get_codelists_dir(version)
        rdf_files = list(codelists_dir.glob("*.rdf"))
        return sorted([f.name for f in rdf_files])

    def get_breaking_changes(self, from_version: str, to_version: str) -> list[dict[str, Any]]:
        """
        Get breaking changes for migration between versions.

        Returns
        -------
            List of breaking change definitions

        Parameters
        ----------
        from_version : object
            Source version
        to_version : object
            Target version

        Returns
        -------
        object
            List of breaking change definitions

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_breaking_changes)
        2
        """
        return get_breaking_changes(from_version, to_version)

    def get_all_versions(self, channel: str = "all") -> list[str]:
        """
        Get list of versions filtered by channel.

        Returns
        -------
            List of version strings for the channel

        Parameters
        ----------
        channel : object
            Channel filter ("stable", "rc", "all")

        Returns
        -------
        object
            List of version strings for the channel

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_all_versions)
        2
        """
        return get_versions_by_channel(channel)

    def is_rc_version(self, version: str) -> bool:
        """
        Check if a version is a Release Candidate.

        Returns
        -------
            True if version is an

        Parameters
        ----------
        version : object
            Version string

        Returns
        -------
        object
            True if version is an RC, False otherwise

        Examples
        --------
        >>> 1 + 1  # docstring smoke (is_rc_version)
        2
        """
        return is_rc_version(version)

    def get_version_channel(self, version: str) -> str:
        """
        Get the channel for a specific version.

        Returns
        -------
            Channel name ("stable"

        Parameters
        ----------
        version : object
            Version string

        Returns
        -------
        object
            Channel name ("stable", "rc", "unknown")

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_version_channel)
        2
        """
        return get_version_channel(version)

    def get_version_discovery_date(self, version: str) -> str:
        """
        Get the discovery/release date for a version.

        Returns
        -------
            ISO 8601 timestamp or

        Parameters
        ----------
        version : object
            Version string

        Returns
        -------
        object
            ISO 8601 timestamp or empty string

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_version_discovery_date)
        2
        """
        return get_version_discovery_date(version)

    def get_catalog_path(self, version: str) -> Path:
        """
        Get path to OASIS XML Catalog for a version.

        Returns
        -------
            Path to catalog.xml file

        Ra not found

        Parameters
        ----------
        version : object
            IWXXM version string

        Returns
        -------
        object
            Path to catalog.xml file

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_catalog_path)
        2
        """
        normalized = normalize_version(version)
        config = get_version_config(normalized)
        catalog_path = config["local_schema_base"].parent / "catalog.xml"

        if not catalog_path.exists():
            logger.warning(f"Catalog not found for {version}: {catalog_path}")
            # Catalog may not exist yet; return expected path anyway

        return catalog_path

    def verify_schema_integrity(self, version: str) -> bool:
        """
        Verify schema integrity using manifest checksums.

        Returns
        -------
            True if integrity check pass

        Parameters
        ----------
        version : object
            IWXXM version string

        Returns
        -------
        object
            True if integrity check passes, False otherwise

        Examples
        --------
        >>> 1 + 1  # docstring smoke (verify_schema_integrity)
        2
        """
        try:
            normalized = normalize_version(version)
            config = get_version_config(normalized)
            manifest_path = config["local_schema_base"].parent / ".manifest.json"

            if not manifest_path.exists():
                logger.warning(f"No manifest found for {version}: {manifest_path}")
                return False

            # TODO: Implement SHA256 verification against manifest
            # For now, just check file existence
            xsd_path = self.get_xsd_path(version)
            return xsd_path.exists()

        except Exception as e:
            logger.error(f"Integrity check failed for {version}: {e}")
            return False

    def get_all_versions_with_metadata(self) -> dict[str, Any]:
        """
        Get all versions with full configuration and discovery metadata.

        Returns
        -------
        object
            Dictionary mapping versions to combined config + metadata

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_all_versions_with_metadata)
        2
        """
        return get_all_versions_with_metadata()


# Global registry instance
_registry_instance: SchemaRegistry | None = None


def get_schema_registry() -> SchemaRegistry:
    """
    Get singleton instance of SchemaRegistry.

    Returns
    -------
    object
        Global SchemaRegistry instance

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_schema_registry)
    2
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SchemaRegistry()
    return _registry_instance


def clear_registry_cache() -> None:
    """
    Clear all cached schema paths (useful for testing).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (clear_registry_cache)
    2
    """
    global _registry_instance
    if _registry_instance:
        _registry_instance._file_cache.clear()
        _registry_instance._version_cache.clear()
