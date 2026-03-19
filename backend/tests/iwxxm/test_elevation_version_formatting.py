"""
Tests for elevation service version-aware formatting.

Verifies that elevation values are formatted according to IWXXM version rules.
"""

import pytest

from src.config.version_formatting import ELEVATION_FORMAT, format_elevation, get_elevation_rounding
from src.utilities.elevation_service import ElevationService


class TestElevationVersionFormatting:
    """Test elevation formatting with version awareness."""

    @pytest.fixture
    def elevation_service(self):
        """Provide an elevation service instance."""
        return ElevationService()

    def test_elevation_service_accepts_version_parameter(self, elevation_service):
        """Verify that get_elevation_data accepts version parameter."""
        # This should not raise an exception
        elevation_m, datum = elevation_service.get_elevation_data(
            icao="BGBW",
            default_elevation_ft=124,
            version="2025-2"
        )
        assert datum == "EGM_96"

    def test_format_elevation_2025_2(self):
        """Test elevation formatting for version 2025-2 (no rounding)."""
        value = 124 * 0.3048  # 37.79 meters
        result = format_elevation(value, version="2025-2")
        # 2025-2 should have no rounding (round_to=0)
        assert isinstance(result, (int, float))
        assert result == round(value, 0)

    def test_format_elevation_2023_1(self):
        """Test elevation formatting for version 2023-1 (no rounding)."""
        value = 1000.4567
        result = format_elevation(value, version="2023-1")
        # 2023-1 should have no rounding (round_to=0)
        assert result == round(value, 0)

    def test_elevation_rounding_rules_consistency(self):
        """Verify all versions have defined rounding rules."""
        for version in ELEVATION_FORMAT.keys():
            rounding = get_elevation_rounding(version)
            assert isinstance(rounding, int)
            assert 0 <= rounding <= 10

    def test_elevation_service_with_different_versions(self, elevation_service):
        """Test that elevation service can handle multiple versions."""
        versions = ["2023-1", "2025-2"]

        for version in versions:
            elev_m, datum = elevation_service.get_elevation_data(
                icao="BGBW",
                default_elevation_ft=124,
                version=version
            )
            # Should return consistent datum regardless of version
            assert datum == "EGM_96"
            # Elevation should be approximately the same (conversion accuracy)
            # 124 ft * 0.3048 = 37.79 m, rounded to int = 38 m
            if elev_m is not None:
                assert 30 < elev_m < 45  # Allow reasonable range for rounding

    def test_elevation_formatting_precision_consistent(self):
        """Verify that supported versions use consistent precision."""
        test_value = 12345.6789

        # Both 2023-1 and 2025-2 use no rounding (round to integer)
        result_2023_1 = format_elevation(test_value, "2023-1")
        result_2025_2 = format_elevation(test_value, "2025-2")

        # Both should maintain same precision
        assert result_2023_1 == round(test_value, 0)
        assert result_2025_2 == round(test_value, 0)
        assert result_2023_1 == result_2025_2

    def test_get_elevation_rounding_defaults(self):
        """Verify rounding defaults for unknown versions."""
        # Unknown versions should default to 0 (no rounding)
        rounding = get_elevation_rounding("2099-9")
        assert rounding == 0


class TestElevationIntegration:
    """Integration tests for elevation service with versions."""

    def test_elevation_data_with_version_override(self):
        """Test that version parameter doesn't break existing functionality."""
        service = ElevationService()

        # Add an override
        service.add_airport_override(
            icao="TTEST",
            elevation_m=2500,
            vertical_datum="NAVD88",
            source="test_override"
        )

        # Get with version parameter
        elev_m, datum = service.get_elevation_data(
            icao="TTEST",
            version="2025-2"
        )

        assert elev_m == 2500
        assert datum == "NAVD88"

    def test_elevation_version_parameter_backward_compat(self):
        """Verify backward compatibility - version param should be optional."""
        service = ElevationService()

        # Should work without version parameter (uses default)
        elev_m, datum = service.get_elevation_data(
            icao="BGBW",
            default_elevation_ft=124
        )

        assert isinstance(datum, str)
        assert len(datum) > 0
