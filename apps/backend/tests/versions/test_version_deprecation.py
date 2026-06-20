"""
Test Version Deprecation

Validates that deprecated IWXXM versions are properly rejected
and only 2025-2 and 2023-1 are supported.
"""

import pytest

from src.config.iwxxm_versions import (
    DEPRECATED_VERSIONS,
    SUPPORTED_VERSIONS,
    VersionDeprecatedError,
    get_supported_versions,
    get_version_config,
    normalize_version,
)


class TestVersionDeprecation:
    """Test suite for version deprecation enforcement"""

    def test_core_stable_versions_supported(self):
        """Verify core stable versions 2023-1 and 2025-2 are supported"""
        versions = get_supported_versions()
        # We now support 2+ stable versions plus RC versions
        assert len(versions) >= 2, f"Expected at least 2 versions, got {len(versions)}"
        assert "2023-1" in versions, "2023-1 should be supported"
        assert "2025-2" in versions, "2025-2 should be supported"

    def test_2025_2_is_in_supported_versions(self):
        """Verify 2025-2 exists in SUPPORTED_VERSIONS"""
        assert "2025-2" in SUPPORTED_VERSIONS

    def test_2023_1_is_in_supported_versions(self):
        """Verify 2023-1 exists in SUPPORTED_VERSIONS"""
        assert "2023-1" in SUPPORTED_VERSIONS

    def test_2021_2_not_in_supported_versions(self):
        """Verify 2021-2 removed from SUPPORTED_VERSIONS"""
        assert "2021-2" not in SUPPORTED_VERSIONS

    def test_2021_2_is_deprecated(self):
        """Verify 2021-2 is in DEPRECATED_VERSIONS"""
        assert "2021-2" in DEPRECATED_VERSIONS

    def test_deprecated_versions_have_dates(self):
        """All deprecated versions must have deprecation_date"""
        for version, info in DEPRECATED_VERSIONS.items():
            assert "deprecated_date" in info
            assert "reason" in info
            assert info["deprecated_date"] == "2026-02-13"

    @pytest.mark.parametrize("old_version", ["2021-2", "2018", "2018-2", "2016", "2016-1", "3.0.0", "3.0-dev"])
    def test_old_versions_rejected_with_deprecation_error(self, old_version):
        """Verify deprecated versions raise VersionDeprecatedError"""
        with pytest.raises(VersionDeprecatedError) as exc_info:
            get_version_config(old_version)

        # Check error message contains version and date
        error_msg = str(exc_info.value)
        assert old_version in error_msg
        assert "2026-02-13" in error_msg
        assert "no longer supported" in error_msg.lower()

    def test_deprecated_error_lists_supported_versions(self):
        """Error message should list currently supported versions"""
        with pytest.raises(VersionDeprecatedError) as exc_info:
            get_version_config("2021-2")

        error_msg = str(exc_info.value)
        assert "2025-2" in error_msg
        assert "2023-1" in error_msg

    def test_supported_versions_config_loads(self):
        """Verify supported versions return valid config"""
        config_2025 = get_version_config("2025-2")
        assert config_2025["name"] == "IWXXM 2025-2"
        assert config_2025["wmo_amendment"] == 82

        config_2023 = get_version_config("2023-1")
        assert config_2023["name"] == "IWXXM 2023-1"
        assert config_2023["wmo_amendment"] == 78

    def test_schema_files_exist_for_supported_versions(self):
        """Verify schema infrastructure complete for supported versions"""
        from src.config.iwxxm_versions import resolve_schema_file

        for version in ["2023-1", "2025-2"]:
            # XSD should exist
            xsd_path = resolve_schema_file(version, "xsd")
            assert xsd_path.exists(), f"XSD not found for {version}"

            # Schematron should exist
            sch_path = resolve_schema_file(version, "schematron")
            assert sch_path.exists(), f"Schematron not found for {version}"

            # Codelists dir should exist
            codelists_dir = resolve_schema_file(version, "codelists")
            assert codelists_dir.exists(), f"Codelists dir not found for {version}"

    def test_normalize_version_doesnt_map_deprecated(self):
        """Normalization should not remap deprecated versions to supported ones"""
        # 2021-2 should not be remapped to 2023-1
        normalized = normalize_version("2021-2")
        assert normalized == "2021-2"  # Returns as-is

        # But get_version_config should still reject it
        with pytest.raises(VersionDeprecatedError):
            get_version_config("2021-2")

    def test_unknown_version_raises_value_error_not_deprecation(self):
        """Unknown versions should raise ValueError, not VersionDeprecatedError"""
        with pytest.raises(ValueError) as exc_info:
            get_version_config("2024-1")  # Non-existent version

        # Should NOT be a VersionDeprecatedError
        assert not isinstance(exc_info.value, VersionDeprecatedError)

    def test_empty_version_uses_default(self):
        """Empty version string should default to 2025-2"""
        normalized = normalize_version("")
        assert normalized == "2025-2"

        config = get_version_config("")
        assert config["name"] == "IWXXM 2025-2"

    def test_whitespace_version_uses_default(self):
        """Whitespace-only version should default to 2025-2"""
        normalized = normalize_version("   ")
        assert normalized == "2025-2"

    def test_deprecated_versions_dict_complete(self):
        """DEPRECATED_VERSIONS should include all pre-2023 versions"""
        expected_deprecated = {"2021-2", "2018", "2018-2", "2016", "2016-1", "3.0.0", "3.0-dev"}
        actual_deprecated = set(DEPRECATED_VERSIONS.keys())

        assert expected_deprecated.issubset(actual_deprecated), (
            f"Missing deprecated versions: {expected_deprecated - actual_deprecated}"
        )


class TestVersionDeprecationErrorHandling:
    """Test error handling and messaging for deprecated versions"""

    def test_deprecation_error_is_value_error_subclass(self):
        """VersionDeprecatedError should be a ValueError subclass"""
        assert issubclass(VersionDeprecatedError, ValueError)

    def test_deprecation_error_can_be_caught_as_value_error(self):
        """VersionDeprecatedError should be catchable as ValueError"""
        try:
            get_version_config("2021-2")
        except ValueError as e:
            # Should catch both ValueError and VersionDeprecatedError
            assert isinstance(e, VersionDeprecatedError)
        else:
            pytest.fail("Should have raised VersionDeprecatedError")

    def test_error_message_format_consistent(self):
        """All deprecation errors should have consistent message format"""
        for version in ["2021-2", "2018", "2016"]:
            with pytest.raises(VersionDeprecatedError) as exc_info:
                get_version_config(version)

            msg = str(exc_info.value)
            # Check required components
            assert version in msg
            assert "no longer supported" in msg.lower()
            assert "2026-02-13" in msg
            assert "Supported versions" in msg


class TestBreakingChanges:
    """Test breaking changes tracking between versions"""

    def test_2025_2_breaking_changes_from_2023_1_documented(self):
        """2025-2 should document breaking changes from 2023-1"""
        config = get_version_config("2025-2")
        changes = config["breaking_changes_from_prior"]["2023-1"]

        assert len(changes) > 0
        # Should include runway state removal
        runway_changes = [c for c in changes if "runwayState" in c["element"]]
        assert len(runway_changes) > 0

    def test_2023_1_has_no_breaking_changes(self):
        """2023-1 should have empty breaking_changes_from_prior"""
        config = get_version_config("2023-1")
        assert config["breaking_changes_from_prior"] == {}

    def test_breaking_changes_include_runway_state(self):
        """Breaking changes should document runway state removal"""
        from src.config.iwxxm_versions import get_breaking_changes

        changes = get_breaking_changes("2023-1", "2025-2")
        runway_changes = [c for c in changes if "runway" in c["element"].lower()]

        assert len(runway_changes) >= 2  # runwayState + AerodromeRunwayState

        for change in runway_changes:
            assert change["action"] == "remove"
            assert "reason" in change


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
