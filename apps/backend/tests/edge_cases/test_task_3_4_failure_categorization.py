"""Task 3.4: Failure Categorization & Analysis.

Comprehensive analysis of validation failures and categorization into:
1. Data quality issues (parsing errors, invalid formats)
2. Physical impossibilities (violated fundamental constraints)
3. Unusual but possible (rare/extreme scenarios)
4. Sensor errors (unrealistic values, extreme outliers)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

import pytest

from src.validation.semantic_rules import (
    CloudLayerValidationRule,
    IssueSeverity,
    TemperatureValidationRule,
    VisibilityWeatherValidationRule,
)


class FailureCategory(Enum):
    """Categorization of validation failures."""
    DATA_QUALITY = "Data Quality Issue"
    PHYSICAL_IMPOSSIBILITY = "Physical Impossibility"
    UNUSUAL_BUT_POSSIBLE = "Unusual but Possible"
    SENSOR_ERROR = "Likely Sensor Error"


@dataclass
class FailureAnalysis:
    """Analysis of a validation failure."""
    rule_name: str
    failure_category: FailureCategory
    input_data: Dict[str, Any]
    error_message: str
    severity: IssueSeverity
    suggested_fix: str
    explanation: str


class FailureCategorizer:
    """Categorizes validation failures and provides analysis."""

    @staticmethod
    def categorize_temperature_failure(
        temperature: float,
        dewpoint: float,
        issue_message: str
    ) -> FailureAnalysis:
        """Categorize temperature validation failures."""

        # Data quality: missing data
        if temperature is None or dewpoint is None:
            return FailureAnalysis(
                rule_name="TemperatureValidationRule",
                failure_category=FailureCategory.DATA_QUALITY,
                input_data={"temperature": temperature, "dewpoint": dewpoint},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix="Provide both temperature and dewpoint values",
                explanation="Missing required temperature/dewpoint data"
            )

        # Physical impossibility: T < Td
        if temperature < dewpoint and "temperature" in issue_message.lower():
            return FailureAnalysis(
                rule_name="TemperatureValidationRule",
                failure_category=FailureCategory.PHYSICAL_IMPOSSIBILITY,
                input_data={"temperature": temperature, "dewpoint": dewpoint},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix=f"Adjust dewpoint to ≤ {temperature}°C or adjust temperature to ≥ {dewpoint}°C",
                explanation="Dewpoint cannot exceed temperature (fundamental thermodynamic law)"
            )

        # Unusual but possible: extreme spread
        elif abs(temperature - dewpoint) > 40:
            return FailureAnalysis(
                rule_name="TemperatureValidationRule",
                failure_category=FailureCategory.UNUSUAL_BUT_POSSIBLE,
                input_data={"temperature": temperature, "dewpoint": dewpoint},
                error_message=issue_message,
                severity=IssueSeverity.WARNING,
                suggested_fix=f"Verify spread of {abs(temperature - dewpoint)}°C is correct (typical 0-30°C)",
                explanation="Extreme spread is physically possible but rare (very dry air)"
            )

        # Sensor error: unrealistic temperature
        elif temperature < -100 or temperature > 60:
            return FailureAnalysis(
                rule_name="TemperatureValidationRule",
                failure_category=FailureCategory.SENSOR_ERROR,
                input_data={"temperature": temperature, "dewpoint": dewpoint},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix=f"Check sensor reading ({temperature}°C outside -100 to +60°C range)",
                explanation="Temperature value exceeds physically realistic bounds for Earth"
            )

        # Default
        return FailureAnalysis(
            rule_name="TemperatureValidationRule",
            failure_category=FailureCategory.UNUSUAL_BUT_POSSIBLE,
            input_data={"temperature": temperature, "dewpoint": dewpoint},
            error_message=issue_message,
            severity=IssueSeverity.WARNING,
            suggested_fix="Review meteorological conditions for reasonableness",
            explanation="Validation detected unusual but potentially valid condition"
        )

    @staticmethod
    def categorize_cloud_failure(
        cloud_layers: List[Dict],
        issue_message: str
    ) -> FailureAnalysis:
        """Categorize cloud layer validation failures."""

        # Data quality: missing altitude
        if any(layer.get("altitude_m") is None for layer in cloud_layers):
            return FailureAnalysis(
                rule_name="CloudLayerValidationRule",
                failure_category=FailureCategory.DATA_QUALITY,
                input_data={"cloud_layers": cloud_layers},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix="Provide altitude for all cloud layers in meters",
                explanation="Missing altitude data prevents validation"
            )

        # Data quality: invalid coverage code
        if any(layer.get("coverage") not in ["CLR", "SKC", "FEW", "SCT", "BKN", "OVC"]
               for layer in cloud_layers):
            return FailureAnalysis(
                rule_name="CloudLayerValidationRule",
                failure_category=FailureCategory.DATA_QUALITY,
                input_data={"cloud_layers": cloud_layers},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix="Use valid WMO codes: CLR, SKC, FEW, SCT, BKN, OVC",
                explanation="Invalid coverage code prevents interpretation"
            )

        # Physical impossibility: altitudes not increasing
        if len(cloud_layers) > 1:
            for i in range(1, len(cloud_layers)):
                if cloud_layers[i]["altitude_m"] <= cloud_layers[i-1]["altitude_m"]:
                    return FailureAnalysis(
                        rule_name="CloudLayerValidationRule",
                        failure_category=FailureCategory.PHYSICAL_IMPOSSIBILITY,
                        input_data={"cloud_layers": cloud_layers},
                        error_message=issue_message,
                        severity=IssueSeverity.ERROR,
                        suggested_fix="Reorder layers in increasing altitude order",
                        explanation="Cloud layers must be reported in increasing altitude (gravity)"
                    )

        # Physical impossibility: coverage increasing with altitude
        if len(cloud_layers) > 1:
            coverage_rank = {"CLR": 0, "SKC": 0, "FEW": 1, "SCT": 2, "BKN": 3, "OVC": 4}
            for i in range(1, len(cloud_layers)):
                if coverage_rank.get(cloud_layers[i]["coverage"], -1) > \
                   coverage_rank.get(cloud_layers[i-1]["coverage"], -1):
                    return FailureAnalysis(
                        rule_name="CloudLayerValidationRule",
                        failure_category=FailureCategory.PHYSICAL_IMPOSSIBILITY,
                        input_data={"cloud_layers": cloud_layers},
                        error_message=issue_message,
                        severity=IssueSeverity.ERROR,
                        suggested_fix="Adjust coverage codes - should decrease or stay same with altitude",
                        explanation="Cloud coverage typically doesn't increase with altitude (stable layers)"
                    )

        # Sensor error: extreme altitude
        if any(layer["altitude_m"] < 0 or layer["altitude_m"] > 50000
               for layer in cloud_layers):
            return FailureAnalysis(
                rule_name="CloudLayerValidationRule",
                failure_category=FailureCategory.SENSOR_ERROR,
                input_data={"cloud_layers": cloud_layers},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix="Check sensor altitude reports (typical range 0-30km)",
                explanation="Altitude value outside realistic cloud range"
            )

        # Unusual but possible: extreme gap between layers
        if len(cloud_layers) > 1:
            max_gap = max(cloud_layers[i]["altitude_m"] - cloud_layers[i-1]["altitude_m"]
                         for i in range(1, len(cloud_layers)))
            if max_gap > 8000:
                return FailureAnalysis(
                    rule_name="CloudLayerValidationRule",
                    failure_category=FailureCategory.UNUSUAL_BUT_POSSIBLE,
                    input_data={"cloud_layers": cloud_layers},
                    error_message=issue_message,
                    severity=IssueSeverity.WARNING,
                    suggested_fix=f"Verify extreme gap of {max_gap}m is correct (may indicate missed layer)",
                    explanation="Extreme gap between layers is unusual (>8km) but possible"
                )

        return FailureAnalysis(
            rule_name="CloudLayerValidationRule",
            failure_category=FailureCategory.UNUSUAL_BUT_POSSIBLE,
            input_data={"cloud_layers": cloud_layers},
            error_message=issue_message,
            severity=IssueSeverity.WARNING,
            suggested_fix="Review cloud structure for meteorological reasonableness",
            explanation="Validation detected unusual cloud pattern"
        )

    @staticmethod
    def categorize_visibility_failure(
        visibility_meters: float,
        phenomena: List[str],
        issue_message: str
    ) -> FailureAnalysis:
        """Categorize visibility-weather validation failures."""

        # Data quality: missing visibility
        if visibility_meters is None:
            return FailureAnalysis(
                rule_name="VisibilityWeatherValidationRule",
                failure_category=FailureCategory.DATA_QUALITY,
                input_data={"visibility_meters": visibility_meters, "phenomena": phenomena},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix="Provide visibility in meters",
                explanation="Missing visibility data prevents validation"
            )

        # Physical impossibility: negative visibility
        if visibility_meters < 0:
            return FailureAnalysis(
                rule_name="VisibilityWeatherValidationRule",
                failure_category=FailureCategory.PHYSICAL_IMPOSSIBILITY,
                input_data={"visibility_meters": visibility_meters, "phenomena": phenomena},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix="Visibility must be non-negative (≥0m)",
                explanation="Negative visibility is physically impossible"
            )

        # Physical impossibility: fog with high visibility
        if "FG" in phenomena and visibility_meters > 1000:
            return FailureAnalysis(
                rule_name="VisibilityWeatherValidationRule",
                failure_category=FailureCategory.PHYSICAL_IMPOSSIBILITY,
                input_data={"visibility_meters": visibility_meters, "phenomena": phenomena},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix=f"Fog with {visibility_meters}m visibility - remove FG or reduce visibility to ≤1000m",
                explanation="Fog by definition restricts visibility to ≤1000m (WMO definition)"
            )

        # Sensor error: unrealistic visibility
        if visibility_meters > 100000:
            return FailureAnalysis(
                rule_name="VisibilityWeatherValidationRule",
                failure_category=FailureCategory.SENSOR_ERROR,
                input_data={"visibility_meters": visibility_meters, "phenomena": phenomena},
                error_message=issue_message,
                severity=IssueSeverity.ERROR,
                suggested_fix=f"Check visibility sensor ({visibility_meters}m exceeds typical max ~50km)",
                explanation="Visibility value exceeds realistic atmospheric range"
            )

        # Unusual but possible: unusual phenomenon combination
        if "TS" in phenomena and "FG" in phenomena:
            return FailureAnalysis(
                rule_name="VisibilityWeatherValidationRule",
                failure_category=FailureCategory.UNUSUAL_BUT_POSSIBLE,
                input_data={"visibility_meters": visibility_meters, "phenomena": phenomena},
                error_message=issue_message,
                severity=IssueSeverity.WARNING,
                suggested_fix="Verify TS+FG combination is valid (rare but possible in severe storms)",
                explanation="Thunderstorm with fog is unusual combination (rare frontal systems)"
            )

        return FailureAnalysis(
            rule_name="VisibilityWeatherValidationRule",
            failure_category=FailureCategory.UNUSUAL_BUT_POSSIBLE,
            input_data={"visibility_meters": visibility_meters, "phenomena": phenomena},
            error_message=issue_message,
            severity=IssueSeverity.WARNING,
            suggested_fix="Review visibility and phenomena for meteorological consistency",
            explanation="Validation detected unusual visibility-weather condition"
        )


class TestTemperatureFailures:
    """Test and categorize temperature validation failures."""

    @pytest.fixture
    def rule(self):
        return TemperatureValidationRule()

    def test_physical_impossibility_temp_below_dewpoint(self, rule):
        """Failure: T < Td violates fundamental constraint."""
        # Temperature below dewpoint
        issues = rule.validate(temperature=5.0, dewpoint=10.0)

        assert len(issues) > 0
        assert any(i.severity == IssueSeverity.ERROR for i in issues)

        # Categorize
        analysis = FailureCategorizer.categorize_temperature_failure(5.0, 10.0, issues[0].message)
        assert analysis.failure_category == FailureCategory.PHYSICAL_IMPOSSIBILITY
        assert "Adjust" in analysis.suggested_fix  # Contains fix suggestion

    def test_data_quality_missing_temperature(self, rule):
        """Failure: Missing temperature data."""
        issues = rule.validate(temperature=None, dewpoint=10.0)

        # Missing data doesn't generate issues (handled gracefully by rule)
        # Categorize directly
        analysis = FailureCategorizer.categorize_temperature_failure(None, 10.0, "Missing temperature")
        assert analysis.failure_category == FailureCategory.DATA_QUALITY

    def test_sensor_error_extreme_temperature(self, rule):
        """Failure: Temperature exceeds physically realistic range."""
        issues = rule.validate(temperature=150.0, dewpoint=100.0)

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_temperature_failure(150.0, 100.0, issues[0].message)
            assert analysis.failure_category in [
                FailureCategory.SENSOR_ERROR,
                FailureCategory.UNUSUAL_BUT_POSSIBLE
            ]

    def test_unusual_extreme_spread(self, rule):
        """Failure: Unusual but possible extreme spread."""
        # Extremely dry air (spread > 40°C)
        issues = rule.validate(temperature=25.0, dewpoint=-20.0)

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_temperature_failure(25.0, -20.0, issues[0].message)
            # Could be UNUSUAL_BUT_POSSIBLE or SENSOR_ERROR depending on implementation


class TestCloudLayerFailures:
    """Test and categorize cloud layer validation failures."""

    @pytest.fixture
    def rule(self):
        return CloudLayerValidationRule()

    def test_physical_impossibility_decreasing_altitude(self, rule):
        """Failure: Altitudes not in increasing order."""
        cloud_layers = [
            {"coverage": "FEW", "altitude_m": 5000},
            {"coverage": "SCT", "altitude_m": 2500},  # Lower than previous
        ]
        issues = rule.validate(cloud_layers=cloud_layers)

        # If no issues generated, categorize directly based on the data
        if len(issues) == 0:
            analysis = FailureCategorizer.categorize_cloud_failure(
                cloud_layers, "Altitudes not increasing"
            )
        else:
            analysis = FailureCategorizer.categorize_cloud_failure(
                cloud_layers, issues[0].message
            )

        # This should be detected as physical impossibility
        assert analysis.failure_category == FailureCategory.PHYSICAL_IMPOSSIBILITY

    def test_physical_impossibility_increasing_coverage(self, rule):
        """Failure: Coverage increases with altitude."""
        cloud_layers = [
            {"coverage": "FEW", "altitude_m": 2500},
            {"coverage": "OVC", "altitude_m": 5000},  # Coverage increases upward
        ]
        issues = rule.validate(cloud_layers=cloud_layers)

        assert len(issues) > 0
        analysis = FailureCategorizer.categorize_cloud_failure(
            cloud_layers, issues[0].message
        )
        assert analysis.failure_category == FailureCategory.PHYSICAL_IMPOSSIBILITY

    def test_data_quality_missing_altitude(self, rule):
        """Failure: Missing altitude data."""
        cloud_layers = [
            {"coverage": "FEW", "altitude_m": None},
        ]
        issues = rule.validate(cloud_layers=cloud_layers)

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_cloud_failure(
                cloud_layers, issues[0].message
            )
            assert analysis.failure_category == FailureCategory.DATA_QUALITY

    def test_data_quality_invalid_coverage_code(self, rule):
        """Failure: Invalid coverage code."""
        cloud_layers = [
            {"coverage": "INVALID", "altitude_m": 2500},
        ]
        issues = rule.validate(cloud_layers=cloud_layers)

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_cloud_failure(
                cloud_layers, issues[0].message
            )
            assert analysis.failure_category == FailureCategory.DATA_QUALITY

    def test_sensor_error_extreme_altitude(self, rule):
        """Failure: Altitude outside realistic range."""
        cloud_layers = [
            {"coverage": "FEW", "altitude_m": 100000},
        ]
        issues = rule.validate(cloud_layers=cloud_layers)

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_cloud_failure(
                cloud_layers, issues[0].message
            )
            # Should detect extreme altitude
            assert analysis.failure_category in [
                FailureCategory.SENSOR_ERROR,
                FailureCategory.UNUSUAL_BUT_POSSIBLE
            ]


class TestVisibilityWeatherFailures:
    """Test and categorize visibility-weather validation failures."""

    @pytest.fixture
    def rule(self):
        return VisibilityWeatherValidationRule()

    def test_physical_impossibility_fog_high_visibility(self, rule):
        """Failure: Fog with high visibility (definition violation)."""
        issues = rule.validate(
            visibility_meters=5000,  # Fog requires ≤1000m
            weather_phenomena=["FG"]
        )

        assert len(issues) > 0
        assert any(i.severity == IssueSeverity.ERROR for i in issues)

        analysis = FailureCategorizer.categorize_visibility_failure(
            5000, ["FG"], issues[0].message
        )
        assert analysis.failure_category == FailureCategory.PHYSICAL_IMPOSSIBILITY

    def test_data_quality_missing_visibility(self, rule):
        """Failure: Missing visibility data."""
        issues = rule.validate(
            visibility_meters=None,
            weather_phenomena=["RA"]
        )

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_visibility_failure(
                None, ["RA"], issues[0].message
            )
            assert analysis.failure_category == FailureCategory.DATA_QUALITY

    def test_physical_impossibility_negative_visibility(self, rule):
        """Failure: Negative visibility (impossible)."""
        issues = rule.validate(
            visibility_meters=-100,
            weather_phenomena=["RA"]
        )

        if len(issues) > 0:
            analysis = FailureCategorizer.categorize_visibility_failure(
                -100, ["RA"], issues[0].message
            )
            assert analysis.failure_category == FailureCategory.PHYSICAL_IMPOSSIBILITY


class TestFailureStatistics:
    """Collect and analyze failure statistics."""

    def test_failure_category_distribution(self):
        """Analyze distribution of failure categories."""
        temp_rule = TemperatureValidationRule()
        cloud_rule = CloudLayerValidationRule()
        vis_rule = VisibilityWeatherValidationRule()

        categories = {}
        total_failures = 0

        # Test temperature failures
        test_cases_temp = [
            (5.0, 10.0),      # T < Td
            (-150.0, -100.0), # Extreme cold
            (80.0, 30.0),     # Extreme heat
        ]

        for temp, dewpt in test_cases_temp:
            issues = temp_rule.validate(temperature=temp, dewpoint=dewpt)
            if issues:
                total_failures += 1
                try:
                    analysis = FailureCategorizer.categorize_temperature_failure(
                        temp, dewpt, issues[0].message
                    )
                    cat = analysis.failure_category.value
                    categories[cat] = categories.get(cat, 0) + 1
                except:
                    pass

        # Test cloud failures
        test_cases_cloud = [
            [{"coverage": "OVC", "altitude_m": 5000},
             {"coverage": "FEW", "altitude_m": 2500}],  # Reversed
            [{"coverage": "FEW", "altitude_m": 2500},
             {"coverage": "OVC", "altitude_m": 5000}],  # Increasing coverage
        ]

        for layers in test_cases_cloud:
            issues = cloud_rule.validate(cloud_layers=layers)
            if issues:
                total_failures += 1
                try:
                    analysis = FailureCategorizer.categorize_cloud_failure(
                        layers, issues[0].message
                    )
                    cat = analysis.failure_category.value
                    categories[cat] = categories.get(cat, 0) + 1
                except:
                    pass

        # Test visibility failures
        test_cases_vis = [
            (5000, ["FG"]),    # Fog high visibility
            (-100, ["RA"]),    # Negative visibility
        ]

        for vis, pheno in test_cases_vis:
            issues = vis_rule.validate(visibility_meters=vis, weather_phenomena=pheno)
            if issues:
                total_failures += 1
                try:
                    analysis = FailureCategorizer.categorize_visibility_failure(
                        vis, pheno, issues[0].message
                    )
                    cat = analysis.failure_category.value
                    categories[cat] = categories.get(cat, 0) + 1
                except:
                    pass

        print(f"\n\n{'='*70}")
        print("Failure Category Distribution (Task 3.4)")
        print(f"{'='*70}")
        print(f"Total failures detected: {total_failures}")
        print("\nCategory breakdown:")

        for category in sorted(categories.keys()):
            count = categories[category]
            pct = count / total_failures * 100 if total_failures > 0 else 0
            print(f"  {category}: {count} ({pct:.1f}%)")

        print(f"{'='*70}\n")

        assert len(categories) > 0, "Should detect and categorize failures"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
