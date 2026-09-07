"""
Tests for IWXXM version switching functionality.

Tests that the system correctly handles multiple IWXXM versions
and produces output with correct namespaces and schema references.
"""

import pytest
from src.config.iwxxm_versions import (
    get_namespace_uri,
    get_schema_url,
    get_supported_versions,
    get_version_config,
    is_version_supported,
    normalize_version,
    resolve_schema_file,
)


class TestVersionNormalization:
    """Test version string normalization and remapping."""

    def test_normalize_default_version(self):
        """Test that None/empty defaults to 2025-2."""
        assert normalize_version(None) == "2025-2"
        assert normalize_version("") == "2025-2"
        assert normalize_version("   ") == "2025-2"

    def test_normalize_valid_versions(self):
        """Test normalization of valid version strings."""
        assert normalize_version("2025-2") == "2025-2"
        assert normalize_version("2023-1") == "2023-1"

    def test_remap_2025_1_to_2025_2(self):
        """Test that non-existent 2025-1 remaps to 2025-2."""
        assert normalize_version("2025-1") == "2025-2"


class TestVersionConfiguration:
    """Test version configuration retrieval."""

    def test_get_version_config_2025_2(self):
        """Test getting config for 2025-2."""
        config = get_version_config("2025-2")
        assert config["name"] == "IWXXM 2025-2"
        assert config["status"] == "latest"
        assert config["has_measures_xsd"] is False
        assert config["split_nil_codelists"] is True

    def test_get_version_config_2023_1(self):
        """Test getting config for 2023-1."""
        config = get_version_config("2023-1")
        assert config["name"] == "IWXXM 2023-1"
        assert config["status"] == "previous"
        assert config["has_measures_xsd"] is True
        assert config["split_nil_codelists"] is False

    def test_get_version_config_invalid(self):
        """Test error on invalid version."""
        with pytest.raises(ValueError, match=r".*"):
            get_version_config("9999-9")

    def test_namespace_uri_per_version(self):
        """Test namespace URI is version-specific."""
        assert get_namespace_uri("2025-2") == "http://icao.int/iwxxm/2025-2"
        assert get_namespace_uri("2023-1") == "http://icao.int/iwxxm/2023-1"

    def test_schema_url_per_version(self):
        """Test schema URLs are version-specific."""
        assert "2025-2" in get_schema_url("2025-2")
        assert "2023-1" in get_schema_url("2023-1")

    def test_detected_schema_paths_exist(self):
        """Test detected local schema paths resolve to existing resources."""
        xsd_path = resolve_schema_file("2025-2", "xsd")
        assert xsd_path.exists()
        codelists_dir = resolve_schema_file("2025-2", "codelists")
        assert codelists_dir.exists()


class TestVersionSupport:
    """Test version support lookup."""

    def test_get_supported_versions(self):
        """Test listing all supported versions."""
        versions = get_supported_versions()
        assert len(versions) >= 2
        assert "2025-2" in versions
        assert "2023-1" in versions

    def test_is_version_supported(self):
        """Test version support check."""
        assert is_version_supported("2025-2")
        assert is_version_supported("2023-1")
        assert is_version_supported("2025-1")  # Should remap to 2025-2
        assert not is_version_supported("9999-9")
        assert not is_version_supported("2021-2")  # Deprecated version


class TestBreakingChanges:
    """Test breaking changes between versions."""

    def test_breaking_changes_2023_1_to_2025_2(self):
        """Test that 2023-1→2025-2 has breaking changes."""
        from src.config.iwxxm_versions import get_breaking_changes

        changes = get_breaking_changes("2023-1", "2025-2")
        assert len(changes) > 0

        # Should include runway state removal
        element_names = [c.get("element") for c in changes]
        assert any("runwayState" in str(name) for name in element_names)

    def test_no_breaking_changes_same_version(self):
        """Test that same version has no breaking changes."""
        from src.config.iwxxm_versions import get_breaking_changes

        changes = get_breaking_changes("2025-2", "2025-2")
        assert len(changes) == 0


class TestVersionFeatures:
    """Test version-specific features."""

    def test_2025_2_features(self):
        """Test 2025-2 feature flags."""
        config = get_version_config("2025-2")
        assert config["has_measures_xsd"] is False
        assert config["split_nil_codelists"] is True

    def test_2023_1_features(self):
        """Test 2023-1 feature flags."""
        config = get_version_config("2023-1")
        assert config["has_measures_xsd"] is True
        assert config["split_nil_codelists"] is False


@pytest.mark.asyncio
class TestVersionParameterInAPI:
    """Test version parameter handling in API endpoints."""

    async def test_version_parameter_normalization(self):
        """Test that API normalizes version parameters."""
        from src.config.iwxxm_versions import normalize_version

        # Test remapping
        assert normalize_version("2025-1") == "2025-2"

        # Test default
        assert normalize_version(None) == "2025-2"
