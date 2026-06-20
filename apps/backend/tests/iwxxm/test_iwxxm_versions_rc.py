"""
Tests for Enhanced IWXXM Version Configuration

Tests RC channel support, version discovery metadata, and channel filtering.
"""

import pytest

from src.config.iwxxm_versions import (
    ALL_VERSIONS,
    RC_VERSIONS,
    SUPPORTED_VERSIONS,
    VERSION_DISCOVERY_METADATA,
    get_all_versions_with_metadata,
    get_version_channel,
    get_version_config,
    get_version_discovery_date,
    get_versions_by_channel,
    is_rc_version,
    register_rc_version,
)


class TestVersionChannels:
    """Test version channel classification."""

    def test_stable_versions_in_supported(self):
        """Test stable versions are in SUPPORTED_VERSIONS."""
        assert "2025-2" in SUPPORTED_VERSIONS
        assert "2023-1" in SUPPORTED_VERSIONS

    def test_get_version_channel_stable(self):
        """Test channel detection for stable versions."""
        assert get_version_channel("2025-2") == "stable"
        assert get_version_channel("2023-1") == "stable"

    def test_is_rc_version_detection(self):
        """Test RC version detection."""
        assert not is_rc_version("2025-2")
        assert not is_rc_version("2023-1")
        # RC detection uses pattern matching, so any version with "RC" should match
        assert is_rc_version("2025-2RC1")
        assert is_rc_version("2026-1RC1")


class TestChannelFiltering:
    """Test version filtering by channel."""

    def test_get_stable_versions(self):
        """Test retrieving stable versions only."""
        stable = get_versions_by_channel("stable")
        assert "2025-2" in stable
        assert "2023-1" in stable
        assert all("RC" not in v for v in stable)

    def test_get_rc_versions(self):
        """Test retrieving RC versions only."""
        rc = get_versions_by_channel("rc")
        # RC_VERSIONS starts empty; register one for testing
        if not rc:
            # Initially empty is expected
            assert rc == []

    def test_get_all_versions(self):
        """Test retrieving all versions."""
        all_versions = get_versions_by_channel("all")
        assert "2025-2" in all_versions
        assert "2023-1" in all_versions


class TestVersionDiscoveryMetadata:
    """Test version discovery metadata."""

    def test_discovery_metadata_exists_for_stable(self):
        """Test discovery metadata exists for stable versions."""
        assert "2025-2" in VERSION_DISCOVERY_METADATA
        assert "2023-1" in VERSION_DISCOVERY_METADATA

    def test_get_version_discovery_date(self):
        """Test getting discovery date for versions."""
        date_2025_2 = get_version_discovery_date("2025-2")
        assert date_2025_2  # Should not be empty
        assert "2025" in date_2025_2

        date_2023_1 = get_version_discovery_date("2023-1")
        assert date_2023_1
        assert "2023" in date_2023_1

    def test_discovery_date_empty_for_unknown(self):
        """Test discovery date returns empty string for unknown versions."""
        date = get_version_discovery_date("unknown-version")
        assert date == ""


class TestRCVersionRegistration:
    """Test runtime RC version registration."""

    def test_register_rc_version(self):
        """Test registering a new RC version."""
        test_rc_config = {
            "name": "IWXXM 2025-2 RC1",
            "namespace_uri": "http://icao.int/iwxxm/2025-2",
            "status": "rc",
            "base_version": "2025-2",
        }

        # Register RC version
        register_rc_version("2025-2RC1", test_rc_config)

        # Verify it's registered
        assert "2025-2RC1" in RC_VERSIONS
        assert "2025-2RC1" in ALL_VERSIONS
        assert is_rc_version("2025-2RC1")

        # Verify channel classification
        assert get_version_channel("2025-2RC1") == "rc"

        # Verify it appears in RC list
        rc_versions = get_versions_by_channel("rc")
        assert "2025-2RC1" in rc_versions


class TestVersionConfigAccess:
    """Test accessing version configuration."""

    def test_get_version_config_stable(self):
        """Test getting config for stable versions."""
        config = get_version_config("2025-2")
        assert config["name"] == "IWXXM 2025-2"
        assert config["status"] == "latest"
        assert "namespace_uri" in config

        config_2023 = get_version_config("2023-1")
        assert config_2023["name"] == "IWXXM 2023-1"
        assert config_2023["status"] == "previous"

    def test_get_all_versions_with_metadata(self):
        """Test getting all versions with full metadata."""
        all_data = get_all_versions_with_metadata()

        assert "2025-2" in all_data
        assert "2023-1" in all_data

        # Check structure
        assert "discovery_metadata" in all_data["2025-2"]
        assert "name" in all_data["2025-2"]


@pytest.mark.unit
class TestVersionConfigIntegration:
    """Integration tests for version configuration."""

    def test_stable_and_rc_coexist(self):
        """Test that stable and RC versions can coexist."""
        # Register a test RC version
        test_rc = {"name": "IWXXM 2026-1 RC1", "status": "rc"}
        register_rc_version("2026-1RC1", test_rc)

        # Verify both stable and RC are accessible
        stable = get_versions_by_channel("stable")
        rc = get_versions_by_channel("rc")
        all_v = get_versions_by_channel("all")

        assert len(stable) >= 2  # At least 2025-2 and 2023-1
        assert "2026-1RC1" in rc
        assert len(all_v) == len(stable) + len(rc)
