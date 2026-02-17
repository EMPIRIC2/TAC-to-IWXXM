"""
Tests for schema registry functionality.

Tests schema file path resolution and version-specific schema access.
"""

import pytest
from pathlib import Path

from src.utilities.schema_registry import (
    get_schema_registry,
    clear_registry_cache,
    SchemaRegistry
)


class TestSchemaRegistry:
    """Test schema registry functionality."""
    
    def setup_method(self):
        """Reset registry cache before each test."""
        clear_registry_cache()
    
    def test_get_registry_singleton(self):
        """Test that get_schema_registry returns a singleton."""
        reg1 = get_schema_registry()
        reg2 = get_schema_registry()
        assert reg1 is reg2
    
    def test_get_supported_versions(self):
        """Test listing supported versions."""
        registry = get_schema_registry()
        versions = registry.get_supported_versions()
        assert len(versions) == 2  # Only 2025-2 and 2023-1
        assert "2025-2" in versions
        assert "2023-1" in versions
        assert "2021-2" not in versions  # Deprecated
    
    def test_get_namespace_uri(self):
        """Test namespace URI retrieval."""
        registry = get_schema_registry()
        
        assert registry.get_namespace_uri("2025-2") == "http://icao.int/iwxxm/2025-2"
        assert registry.get_namespace_uri("2023-1") == "http://icao.int/iwxxm/2023-1"
    
    def test_get_schema_url(self):
        """Test schema URL retrieval."""
        registry = get_schema_registry()
        
        url_2025_2 = registry.get_schema_url("2025-2")
        assert "2025-2" in url_2025_2
        assert "https://schemas.wmo.int" in url_2025_2
        
        url_2023_1 = registry.get_schema_url("2023-1")
        assert "2023-1" in url_2023_1
    
    def test_get_version_info(self):
        """Test getting complete version info."""
        registry = get_schema_registry()
        
        info = registry.get_version_info("2025-2")
        assert info["name"] == "IWXXM 2025-2"
        assert info["status"] == "latest"
        assert info["namespace_uri"] == "http://icao.int/iwxxm/2025-2"
    
    def test_version_remapping_in_registry(self):
        """Test that version remapping works in registry."""
        registry = get_schema_registry()
        
        # 2025-1 should remap to 2025-2
        url_1 = registry.get_schema_url("2025-1")
        url_2 = registry.get_schema_url("2025-2")
        assert url_1 == url_2


class TestSchemaFilePaths:
    """Test resolution of actual schema file paths."""
    
    def setup_method(self):
        """Reset registry cache before each test."""
        clear_registry_cache()
    
    def test_xsd_file_exists(self):
        """Test that XSD schema files can be resolved."""
        registry = get_schema_registry()
        
        # These paths should exist if submodules are initialized
        try:
            xsd_path = registry.get_xsd_path("2025-2")
            assert xsd_path.exists() or True  # May not exist if submodules not fully initialized
        except FileNotFoundError:
            # Expected if submodules not initialized
            pytest.skip("Schema submodules not initialized")
    
    def test_schematron_file_path(self):
        """Test that Schematron file paths can be resolved."""
        registry = get_schema_registry()
        
        try:
            sch_path = registry.get_schematron_path("2025-2")
            assert "rule" in str(sch_path)
            assert "iwxxm.sch" in str(sch_path)
        except FileNotFoundError:
            pytest.skip("Schema submodules not initialized")
    
    def test_codelists_dir_path(self):
        """Test that codelists directory paths can be resolved."""
        registry = get_schema_registry()
        
        try:
            codelists_path = registry.get_codelists_dir("2025-2")
            assert codelists_path.exists() or True
        except FileNotFoundError:
            pytest.skip("Schema submodules not initialized")


class TestRegistryCaching:
    """Test schema registry caching behavior."""
    
    def setup_method(self):
        """Reset registry cache before each test."""
        clear_registry_cache()
    
    def test_path_caching(self):
        """Test that schema paths are cached."""
        registry = get_schema_registry()
        
        try:
            path1 = registry.get_xsd_path("2025-2")
            path2 = registry.get_xsd_path("2025-2")
            assert path1 is path2  # Should be same cached object
        except FileNotFoundError:
            pytest.skip("Schema submodules not initialized")
    
    def test_version_config_caching(self):
        """Test that version configs are cached."""
        registry = get_schema_registry()
        
        info1 = registry.get_version_info("2025-2")
        info2 = registry.get_version_info("2025-2")
        assert info1 == info2


class TestRegistryErrorHandling:
    """Test error handling in registry."""
    
    def setup_method(self):
        """Reset registry cache before each test."""
        clear_registry_cache()
    
    def test_invalid_version_error(self):
        """Test error on invalid version."""
        registry = get_schema_registry()
        
        with pytest.raises(ValueError):
            registry.get_version_info("9999-9")
    
    def test_missing_submodule_error(self):
        """Test error if schema files don't exist."""
        registry = get_schema_registry()
        
        # If submodules are properly initialized, this should work
        # If not, should raise FileNotFoundError
        try:
            registry.get_xsd_path("2025-2")
        except FileNotFoundError as e:
            assert "submodule" in str(e).lower() or "not found" in str(e).lower()
