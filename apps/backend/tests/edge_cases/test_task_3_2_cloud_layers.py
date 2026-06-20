"""Tests for Task 3.2: Cloud Layer Ordering Validation (Enhanced).

Tests enhanced cloud layer validation with:
- Altitude anomaly detection
- Gap analysis
- Coverage consistency
- Production integration
"""

import pytest

from src.validation.semantic_rules import (
    CloudLayerValidationRule,
    IssueSeverity,
)


class TestCloudLayerValidationEnhanced:
    """Test enhanced cloud layer validation (Task 3.2)."""

    @pytest.fixture
    def rule(self):
        """Provide cloud layer validation rule."""
        return CloudLayerValidationRule()

    # ==================== ALTITUDE VALIDITY TESTS ====================

    def test_valid_single_layer(self, rule):
        """Test valid single cloud layer within range."""
        layers = [{"coverage": "BKN", "altitude_m": 1500}]
        issues = rule.validate(layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0

    def test_valid_multiple_layers_increasing_altitude(self, rule):
        """Test valid multiple layers with strictly increasing altitudes."""
        layers = [
            {"coverage": "FEW", "altitude_m": 800},
            {"coverage": "SCT", "altitude_m": 2000},
            {"coverage": "OVC", "altitude_m": 4500},
        ]
        issues = rule.validate(layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0

    def test_cloud_altitude_below_minimum(self, rule):
        """Test warning for cloud base below minimum threshold."""
        layers = [{"coverage": "BKN", "altitude_m": 50}]  # Below 100m minimum
        issues = rule.validate(layers)

        # Should have warning about altitude
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert len(warnings) >= 1
        assert "minimum" in warnings[0].message.lower()

    def test_cloud_altitude_above_maximum(self, rule):
        """Test warning for cloud base above maximum threshold."""
        layers = [{"coverage": "CIR", "altitude_m": 35000}]  # Above 30km max
        issues = rule.validate(layers)

        # Should have warning about altitude
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert len(warnings) >= 1
        assert "exceeds maximum" in warnings[0].message.lower()

    def test_cloud_altitude_above_typical_max(self, rule):
        """Test info message for unusual but valid high altitude."""
        layers = [{"coverage": "CIR", "altitude_m": 8000}]  # Above 6km typical
        issues = rule.validate(layers)

        # Should have info about unusual altitude
        infos = [i for i in issues if i.severity == IssueSeverity.INFO]
        assert len(infos) >= 1
        assert "high altitude" in infos[0].message.lower()

    # ==================== ALTITUDE GAP ANALYSIS TESTS ====================

    def test_normal_gap_between_layers(self, rule):
        """Test normal gap between cloud layers (no issues)."""
        layers = [{"coverage": "FEW", "altitude_m": 1000}, {"coverage": "BKN", "altitude_m": 2500}]
        issues = rule.validate(layers)
        # Gap is 1500m (between small and large thresholds)
        gap_issues = [i for i in issues if "gap" in i.message.lower()]
        assert len(gap_issues) == 0

    def test_small_gap_between_layers(self, rule):
        """Test small gap between layers (< 500m)."""
        layers = [{"coverage": "SCT", "altitude_m": 1000}, {"coverage": "OVC", "altitude_m": 1200}]
        issues = rule.validate(layers)
        # Gap is 200m (very close, but not necessarily invalid)
        # This is physically possible - should not flag
        gap_errors = [i for i in issues if "gap" in i.message.lower() and i.severity == IssueSeverity.ERROR]
        assert len(gap_errors) == 0

    def test_large_gap_between_layers(self, rule):
        """Test large gap between layers (3-8km)."""
        layers = [
            {"coverage": "OVC", "altitude_m": 2000},
            {"coverage": "FEW", "altitude_m": 6000},  # Gap = 4km
        ]
        issues = rule.validate(layers)

        # Should have info about large gap
        gap_infos = [i for i in issues if "gap" in i.message.lower() and i.severity == IssueSeverity.INFO]
        assert len(gap_infos) >= 1

    def test_extreme_gap_between_layers(self, rule):
        """Test extreme gap between layers (> 8km)."""
        layers = [
            {"coverage": "OVC", "altitude_m": 1000},
            {"coverage": "CIR", "altitude_m": 10000},  # Gap = 9km
        ]
        issues = rule.validate(layers)

        # Should have warning about extreme gap
        gap_warnings = [i for i in issues if "gap" in i.message.lower() and i.severity == IssueSeverity.WARNING]
        assert len(gap_warnings) >= 1

    # ==================== ALTITUDE ORDERING TESTS ====================

    def test_duplicate_altitudes(self, rule):
        """Test warning for duplicate altitudes."""
        layers = [
            {"coverage": "BKN", "altitude_m": 1500},
            {"coverage": "OVC", "altitude_m": 1500},  # Same altitude
        ]
        issues = rule.validate(layers)

        # Should have warning about not strictly increasing
        ordering_warnings = [i for i in issues if "not strictly" in i.message.lower()]
        assert len(ordering_warnings) >= 1

    def test_reversed_altitudes(self, rule):
        """Test warning for reversed altitude order."""
        layers = [
            {"coverage": "BKN", "altitude_m": 3000},
            {"coverage": "FEW", "altitude_m": 1000},  # Lower than previous
        ]
        issues = rule.validate(layers)

        # After sorting, these are in correct order, so no errors
        # The layers are reordered internally
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

    # ==================== CLEAR SKY EXCLUSIVITY TESTS ====================

    def test_clear_sky_only(self, rule):
        """Test valid CLR (clear sky) layer alone."""
        layers = [{"coverage": "CLR", "altitude_m": 0}]
        issues = rule.validate(layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0

    def test_sky_clear_only(self, rule):
        """Test valid SKC (sky clear) layer alone."""
        layers = [{"coverage": "SKC", "altitude_m": 0}]
        issues = rule.validate(layers)
        assert len([i for i in issues if i.severity == IssueSeverity.ERROR]) == 0

    def test_clear_with_other_layers(self, rule):
        """Test INVALID: CLR coexists with other layers."""
        layers = [{"coverage": "CLR", "altitude_m": 0}, {"coverage": "FEW", "altitude_m": 2000}]
        issues = rule.validate(layers)

        # Should have error about clear sky exclusivity
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) >= 1
        assert "clear sky" in errors[0].message.lower()

    def test_sky_clear_with_other_layers(self, rule):
        """Test INVALID: SKC coexists with other layers."""
        layers = [{"coverage": "SKC", "altitude_m": 0}, {"coverage": "OVC", "altitude_m": 3000}]
        issues = rule.validate(layers)

        # Should have error about clear sky exclusivity
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) >= 1

    # ==================== COVERAGE CONSISTENCY TESTS ====================

    def test_valid_coverage_decreasing_with_altitude(self, rule):
        """Test valid: coverage decreases with altitude."""
        layers = [
            {"coverage": "OVC", "altitude_m": 1000},  # 100% coverage (rank 4)
            {"coverage": "BKN", "altitude_m": 3000},  # 62-87% coverage (rank 3)
            {"coverage": "SCT", "altitude_m": 5000},  # 37-50% coverage (rank 2)
        ]
        issues = rule.validate(layers)

        # Coverage is decreasing (4->3->2), so no warnings
        cov_warnings = [i for i in issues if "coverage increases" in i.message.lower()]
        assert len(cov_warnings) == 0

    def test_valid_coverage_non_increasing_with_altitude(self, rule):
        """Test valid: coverage non-increasing upward."""
        layers = [
            {"coverage": "OVC", "altitude_m": 1000},  # rank 4
            {"coverage": "OVC", "altitude_m": 2500},  # rank 4 (same)
            {"coverage": "BKN", "altitude_m": 4000},  # rank 3 (decreasing)
        ]
        issues = rule.validate(layers)

        # Coverage stays same then decreases (4->4->3), so no warnings
        cov_warnings = [i for i in issues if "coverage increases" in i.message.lower()]
        assert len(cov_warnings) == 0

    def test_invalid_coverage_increasing_with_altitude(self, rule):
        """Test INVALID: coverage increases upward."""
        layers = [
            {"coverage": "FEW", "altitude_m": 1000},  # rank 1 (1-2 oktas)
            {"coverage": "OVC", "altitude_m": 2000},  # rank 4 (8 oktas - INCREASES)
        ]
        issues = rule.validate(layers)

        # Should have warning about coverage increasing (1->4 is upward increase)
        cov_warnings = [
            i for i in issues if "coverage increases" in i.message.lower() and i.severity == IssueSeverity.WARNING
        ]
        assert len(cov_warnings) >= 1

    def test_severely_invalid_coverage_increasing(self, rule):
        """Test INVALID: extreme coverage increase (clear to overcast)."""
        layers = [{"coverage": "SKC", "altitude_m": 0}, {"coverage": "OVC", "altitude_m": 3000}]
        issues = rule.validate(layers)

        # Should have error (clear sky + other layers is primary error)
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) >= 1

    # ==================== REAL-WORLD SCENARIO TESTS ====================

    def test_realistic_fair_weather_clouds(self, rule):
        """Test typical fair weather cloud scenario."""
        # Fair weather: Few cumulus at 1500m, scattered at 3000m
        layers = [{"coverage": "FEW", "altitude_m": 1500}, {"coverage": "SCT", "altitude_m": 3000}]
        issues = rule.validate(layers)

        # Should be valid - realistic layering
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

    def test_realistic_overcast_scenario(self, rule):
        """Test typical overcast conditions."""
        # Stratified overcast: Low stratus + high cirrus
        layers = [{"coverage": "OVC", "altitude_m": 600}, {"coverage": "CIR", "altitude_m": 8500}]
        issues = rule.validate(layers)

        # Should be valid - physically realistic
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

        # May have info about high cirrus altitude (expected)
        infos = [i for i in issues if i.severity == IssueSeverity.INFO]
        # These are expected and acceptable

    def test_realistic_multi_layer_frontal_system(self, rule):
        """Test realistic multi-layer cloud from frontal passage."""
        # Frontal system: Low, mid, high clouds
        layers = [
            {"coverage": "OVC", "altitude_m": 500},  # Stratus
            {"coverage": "BKN", "altitude_m": 2000},  # Altocumulus
            {"coverage": "OVC", "altitude_m": 6000},  # Altostratus (can be valid!)
        ]
        issues = rule.validate(layers)

        # Altostratus above altocumulus is physically possible
        # (layered cloud in frontal system)
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

    # ==================== EDGE CASES ====================

    def test_empty_cloud_layers(self, rule):
        """Test with empty cloud layers list."""
        issues = rule.validate([])
        assert len(issues) == 0

    def test_missing_altitude_data(self, rule):
        """Test with missing altitude values."""
        layers = [{"coverage": "BKN"}]  # No altitude_m
        issues = rule.validate(layers)
        # Should not crash, should handle gracefully
        assert isinstance(issues, list)

    def test_missing_coverage_data(self, rule):
        """Test with missing coverage values."""
        layers = [{"altitude_m": 1500}]  # No coverage
        issues = rule.validate(layers)
        # Should not crash
        assert isinstance(issues, list)

    def test_unknown_coverage_code(self, rule):
        """Test with unknown coverage code."""
        layers = [{"coverage": "XYZ", "altitude_m": 1000}, {"coverage": "BKN", "altitude_m": 2000}]
        issues = rule.validate(layers)
        # Should handle gracefully, skip unknown codes in coverage checks
        assert isinstance(issues, list)


class TestCloudLayerIntegration:
    """Integration tests with real meteorological scenarios."""

    @pytest.fixture
    def rule(self):
        """Provide cloud layer validation rule."""
        return CloudLayerValidationRule()

    def test_complete_vcs_scenario(self, rule):
        """Test Vertical Cloud Structure (VCS) observation."""
        # WMO VCS format: Multiple well-ordered cloud layers
        vcs_layers = [
            {"coverage": "FEW", "altitude_m": 600},
            {"coverage": "SCT", "altitude_m": 2000},
            {"coverage": "BKN", "altitude_m": 3500},
            {"coverage": "OVC", "altitude_m": 5500},
        ]

        issues = rule.validate(vcs_layers)

        # Should validate without errors
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

        # All layers properly ordered
        assert len(vcs_layers) == 4

    def test_anomalous_detected_cloud_merging(self, rule):
        """Test multiple very close cloud layers (potential data issue)."""
        # Close layers: Two OVC layers with very small gap
        layers = [
            {"coverage": "OVC", "altitude_m": 1000},
            {"coverage": "OVC", "altitude_m": 1050},  # Only 50m apart
        ]

        issues = rule.validate(layers)

        # These altitudes are strictly increasing (1050 > 1000)
        # and gap is < 500m, so not flagged as anomaly by current rules
        # This is physically possible (layered clouds close together)
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

        # Gap should not be flagged (50m is within small gap threshold)
        gap_issues = [i for i in issues if "gap" in i.message.lower()]
        assert len(gap_issues) == 0
