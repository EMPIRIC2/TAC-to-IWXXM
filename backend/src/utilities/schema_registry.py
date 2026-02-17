"""
Schema Registry

Provides centralized schema resolution and caching for IWXXM validation,
including XSD, Schematron, and codelist file locations across versions.
"""

import logging
from typing import Dict, Optional, List
from pathlib import Path
from functools import lru_cache

from ..config.iwxxm_versions import (
    get_version_config,
    normalize_version,
    resolve_schema_file,
    get_breaking_changes,
    get_namespace_uri,
    get_schema_url,
    get_version_channel,
    get_versions_by_channel,
    get_version_discovery_date,
    is_rc_version,
    get_all_versions_with_metadata,
    SUPPORTED_VERSIONS,
    ALL_VERSIONS
)

logger = logging.getLogger(__name__)


class SchemaRegistry:
    """
    Centralized registry for IWXXM schema files across versions.
    Handles file resolution, caching, and validation.
    """
    
    def __init__(self):
        self._version_cache: Dict[str, Dict] = {}
        self._file_cache: Dict[str, Path] = {}
        
    @lru_cache(maxsize=32)
    def get_xsd_path(self, version: str) -> Path:
        """
        Get path to XSD schema file for a version.
        
        Args:
            version: IWXXM version string
            
        Returns:
            Path to the XSD file
            
        Raises:
            FileNotFoundError: If schema not found
            ValueError: If version invalid
        """
        cache_key = f"xsd_{version}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]
        
        normalized = normalize_version(version)
        path = resolve_schema_file(normalized, "xsd")
        self._file_cache[cache_key] = path
        logger.debug(f"Resolved XSD for {version}: {path}")
        return path
    
    @lru_cache(maxsize=32)
    def get_schematron_path(self, version: str) -> Path:
        """
        Get path to Schematron (.sch) file for a version.
        
        Args:
            version: IWXXM version string
            
        Returns:
            Path to the Schematron file
            
        Raises:
            FileNotFoundError: If Schematron not found
            ValueError: If version invalid
        """
        cache_key = f"schematron_{version}"
        if cache_key in self._file_cache:
            return self._file_cache[cache_key]
        
        normalized = normalize_version(version)
        path = resolve_schema_file(normalized, "schematron")
        self._file_cache[cache_key] = path
        logger.debug(f"Resolved Schematron for {version}: {path}")
        return path
    
    @lru_cache(maxsize=32)
    def get_codelists_dir(self, version: str) -> Path:
        """
        Get path to codelists directory for a version.
        
        Args:
            version: IWXXM version string
            
        Returns:
            Path to the codelists directory
            
        Raises:
            FileNotFoundError: If directory not found
            ValueError: If version invalid
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
        """Get XML namespace URI for a version."""
        normalized = normalize_version(version)
        return get_namespace_uri(normalized)
    
    def get_schema_url(self, version: str) -> str:
        """Get remote schema URL for a version."""
        normalized = normalize_version(version)
        return get_schema_url(normalized)
    
    def get_version_info(self, version: str) -> Dict:
        """Get complete version configuration."""
        normalized = normalize_version(version)
        return get_version_config(normalized)
    
    def get_supported_versions(self) -> List[str]:
        """Get list of supported IWXXM versions."""
        return list(SUPPORTED_VERSIONS.keys())
    
    def list_codelists(self, version: str) -> List[str]:
        """
        List all codelist files for a version.
        
        Args:
            version: IWXXM version string
            
        Returns:
            List of codelist filenames (RDF files)
        """
        codelists_dir = self.get_codelists_dir(version)
        rdf_files = list(codelists_dir.glob("*.rdf"))
        return sorted([f.name for f in rdf_files])
    
    def get_breaking_changes(self, from_version: str, to_version: str) -> List[Dict]:
        """
        Get breaking changes for migration between versions.
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            List of breaking change definitions
        """
        return get_breaking_changes(from_version, to_version)
    
    def get_all_versions(self, channel: str = "all") -> List[str]:
        """
        Get list of versions filtered by channel.
        
        Args:
            channel: Channel filter ("stable", "rc", "all")
            
        Returns:
            List of version strings for the channel
        """
        return get_versions_by_channel(channel)
    
    def is_rc_version(self, version: str) -> bool:
        """
        Check if a version is a Release Candidate.
        
        Args:
            version: Version string
            
        Returns:
            True if version is an RC, False otherwise
        """
        return is_rc_version(version)
    
    def get_version_channel(self, version: str) -> str:
        """
        Get the channel for a specific version.
        
        Args:
            version: Version string
            
        Returns:
            Channel name ("stable", "rc", "unknown")
        """
        return get_version_channel(version)
    
    def get_version_discovery_date(self, version: str) -> str:
        """
        Get the discovery/release date for a version.
        
        Args:
            version: Version string
            
        Returns:
            ISO 8601 timestamp or empty string
        """
        return get_version_discovery_date(version)
    
    def get_catalog_path(self, version: str) -> Path:
        """
        Get path to OASIS XML Catalog for a version.
        
        Args:
            version: IWXXM version string
            
        Returns:
            Path to catalog.xml file
            
        Raises:
            FileNotFoundError: If catalog not found
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
        
        Args:
            version: IWXXM version string
            
        Returns:
            True if integrity check passes, False otherwise
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
    
    def get_all_versions_with_metadata(self) -> Dict:
        """
        Get all versions with full configuration and discovery metadata.
        
        Returns:
            Dictionary mapping versions to combined config + metadata
        """
        return get_all_versions_with_metadata()


# Global registry instance
_registry_instance: Optional[SchemaRegistry] = None


def get_schema_registry() -> SchemaRegistry:
    """
    Get singleton instance of SchemaRegistry.
    
    Returns:
        Global SchemaRegistry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SchemaRegistry()
    return _registry_instance


def clear_registry_cache():
    """Clear all cached schema paths (useful for testing)."""
    global _registry_instance
    if _registry_instance:
        _registry_instance._file_cache.clear()
        _registry_instance.get_xsd_path.cache_clear()
        _registry_instance.get_schematron_path.cache_clear()
        _registry_instance.get_codelists_dir.cache_clear()
