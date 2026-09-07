"""
Tests for IWXXM Version Detector
"""

from pathlib import Path

import pytest
from src.utilities.version_detector import VersionDetector, VersionInfo, check_for_updates, detect_available_versions


class TestVersionDetector:
    """Test version detection functionality."""

    def test_detector_initialization(self):
        """Test detector initializes with default paths."""
        detector = VersionDetector()

        assert detector.schemas_root.exists()
        assert detector.iwxxm_path.exists()

    def test_tag_to_version_conversion(self):
        """Test git tag to version string conversion."""
        detector = VersionDetector()

        assert detector.tag_to_version("v2025-2") == "2025-2"
        assert detector.tag_to_version("v2023-1") == "2023-1"
        assert detector.tag_to_version("2021-2") == "2021-2"  # Already without v

    def test_version_to_tag_conversion(self):
        """Test version string to git tag conversion."""
        detector = VersionDetector()

        assert detector.version_to_tag("2025-2") == "v2025-2"
        assert detector.version_to_tag("2023-1") == "v2023-1"
        assert detector.version_to_tag("v2021-2") == "v2021-2"  # Already has v

    def test_get_latest_version(self):
        """Test reading LATEST_VERSION file."""
        detector = VersionDetector()
        latest = detector.get_latest_version()

        if latest:
            # Should be a version string like "2025-2"
            assert isinstance(latest, str)
            assert "-" in latest
            assert len(latest.split("-")) == 2

    @pytest.mark.integration
    def test_get_available_tags(self):
        """Test getting git tags from submodule."""
        detector = VersionDetector()
        tags = detector.get_available_tags()

        # Should return list (may be empty if submodule not initialized)
        assert isinstance(tags, list)

        if tags:
            # Tags should start with 'v'
            assert all(tag.startswith("v") for tag in tags)
            # Tags should contain version pattern (YYYY-N)
            assert all("-" in tag for tag in tags)

    @pytest.mark.integration
    def test_detect_versions(self):
        """Test detecting all available versions."""
        detector = VersionDetector()
        versions = detector.detect_versions()

        assert isinstance(versions, list)

        for version_info in versions:
            assert isinstance(version_info, VersionInfo)
            assert version_info.version
            assert version_info.tag
            assert isinstance(version_info.is_configured, bool)
            assert isinstance(version_info.is_latest, bool)

    def test_get_unconfigured_versions(self):
        """Test getting unconfigured versions."""
        detector = VersionDetector()
        unconfigured = detector.get_unconfigured_versions()

        assert isinstance(unconfigured, list)

        # All should have is_configured = False
        assert all(not v.is_configured for v in unconfigured)

    def test_get_new_versions_since(self):
        """Test getting versions newer than reference."""
        detector = VersionDetector()
        newer = detector.get_new_versions_since("2021-2")

        assert isinstance(newer, list)

        # All should be > 2021-2
        assert all(v.version > "2021-2" for v in newer)

    def test_generate_version_report(self):
        """Test generating human-readable version report."""
        detector = VersionDetector()
        report = detector.generate_version_report()

        assert isinstance(report, str)
        assert "IWXXM Version Report" in report
        assert "Latest WMO Version" in report
        assert "Total Available" in report

    def test_convenience_detect_function(self):
        """Test convenience function for detecting versions."""
        versions = detect_available_versions()

        assert isinstance(versions, list)

    def test_convenience_check_updates_function(self):
        """Test convenience function for checking updates."""
        has_updates = check_for_updates()

        assert isinstance(has_updates, bool)


@pytest.mark.integration
class TestVersionDetectorIntegration:
    """Integration tests requiring git submodule."""

    def test_check_version_files_for_known_version(self):
        """Test checking file existence for known version."""
        schemas_path = Path(__file__).parent.parent.parent / "schemas" / "iwxxm"

        if not schemas_path.exists():
            pytest.skip("IWXXM schemas not available (git submodule not initialized)")

        detector = VersionDetector()

        # Check for version 2025-2 (should exist in IWXXM/)
        file_checks = detector.check_version_files("2025-2")

        assert isinstance(file_checks, dict)
        assert "xsd" in file_checks
        assert "metar_xsd" in file_checks
        assert "schematron" in file_checks
        assert "codelists" in file_checks

    def test_detect_actual_wmo_versions(self):
        """Test detecting real WMO IWXXM versions from submodule."""
        schemas_path = Path(__file__).parent.parent.parent / "schemas" / "iwxxm"

        if not schemas_path.exists():
            pytest.skip("IWXXM schemas not available")

        detector = VersionDetector()
        versions = detector.detect_versions()

        # Should detect at least 2025-2, 2023-1, 2021-2
        version_strings = [v.version for v in versions]

        # Latest should be 2025-2 or newer
        if version_strings:
            latest = detector.get_latest_version()
            assert latest in version_strings or latest is None

    def test_version_report_with_real_data(self):
        """Test version report generation with real submodule data."""
        schemas_path = Path(__file__).parent.parent.parent / "schemas" / "iwxxm"

        if not schemas_path.exists():
            pytest.skip("IWXXM schemas not available")

        detector = VersionDetector()
        report = detector.generate_version_report()

        # Report should contain version information
        assert "2025-2" in report or "2023-1" in report
        assert "Configured" in report or "Not Configured" in report
