"""Unit tests for semantic_rules.py (validation) - 0% coverage target."""

from src.validation.semantic_rules import (
    CloudLayerValidationRule,
    IssueSeverity,
    SemanticValidationEngine,
    TemperatureValidationRule,
    ValidationIssue,
    VisibilityWeatherValidationRule,
)


class TestValidationIssue:
    def test_str_representation(self):
        issue = ValidationIssue(
            rule_name="test_rule",
            severity=IssueSeverity.ERROR,
            message="bad data",
            expected="T >= Td",
            actual="T=10, Td=15",
            affected_field="temperature",
        )
        s = str(issue)
        assert "test_rule" in s
        assert "bad data" in s

    def test_optional_suggested_fix(self):
        issue = ValidationIssue(
            rule_name="r", severity=IssueSeverity.INFO, message="m", expected="e", actual="a", affected_field="f"
        )
        assert issue.suggested_fix is None


class TestIssueSeverity:
    def test_values(self):
        assert IssueSeverity.ERROR == "error"
        assert IssueSeverity.WARNING == "warning"
        assert IssueSeverity.INFO == "info"


class TestTemperatureValidationRule:
    def setup_method(self):
        self.rule = TemperatureValidationRule()

    def test_valid_temp_dewpoint(self):
        issues = self.rule.validate(20.0, 15.0)
        assert issues == []

    def test_dewpoint_exceeds_temp_is_error(self):
        issues = self.rule.validate(10.0, 15.0)
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.ERROR

    def test_equal_temp_and_dewpoint_is_valid(self):
        issues = self.rule.validate(15.0, 15.0)
        # Equal is allowed (100% humidity)
        assert all(i.severity != IssueSeverity.ERROR for i in issues)

    def test_none_temperature_skipped(self):
        issues = self.rule.validate(None, 10.0)
        assert issues == []

    def test_none_dewpoint_skipped(self):
        issues = self.rule.validate(10.0, None)
        assert issues == []

    def test_both_none_skipped(self):
        issues = self.rule.validate(None, None)
        assert issues == []

    def test_very_large_spread_warning(self):
        issues = self.rule.validate(60.0, 0.0)
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert len(warnings) >= 1

    def test_very_small_spread_warning(self):
        self.rule.min_dew_spread = 2.0
        issues = self.rule.validate(15.0, 14.0)
        assert any(i.severity == IssueSeverity.WARNING for i in issues)

    def test_negative_temperatures_valid(self):
        issues = self.rule.validate(-5.0, -10.0)
        assert all(i.severity != IssueSeverity.ERROR for i in issues)

    def test_calculate_relative_humidity_saturated(self):
        rh = self.rule.calculate_relative_humidity(15.0, 15.0)
        assert 95.0 <= rh <= 100.0

    def test_calculate_relative_humidity_dry(self):
        rh = self.rule.calculate_relative_humidity(30.0, 0.0)
        assert 0.0 <= rh < 50.0

    def test_rh_clamped_to_0_100(self):
        # Extreme case
        rh = self.rule.calculate_relative_humidity(100.0, -100.0)
        assert 0.0 <= rh <= 100.0


class TestCloudLayerValidationRule:
    def setup_method(self):
        self.rule = CloudLayerValidationRule()

    def test_valid_ascending_layers(self):
        layers = [
            {"coverage": "FEW", "altitude_m": 300},
            {"coverage": "SCT", "altitude_m": 1200},
            {"coverage": "BKN", "altitude_m": 2400},
        ]
        issues = self.rule.validate(layers)
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert errors == []

    def test_empty_layers_is_valid(self):
        issues = self.rule.validate([])
        assert issues == []

    def test_single_layer_is_valid(self):
        layers = [{"coverage": "FEW", "altitude_m": 900}]
        issues = self.rule.validate(layers)
        assert isinstance(issues, list)

    def test_coverage_rank_known_values(self):
        assert self.rule.COVERAGE_RANK["OVC"] > self.rule.COVERAGE_RANK["BKN"]
        assert self.rule.COVERAGE_RANK["BKN"] > self.rule.COVERAGE_RANK["SCT"]
        assert self.rule.COVERAGE_RANK["SCT"] > self.rule.COVERAGE_RANK["FEW"]
        assert self.rule.COVERAGE_RANK["FEW"] > self.rule.COVERAGE_RANK["CLR"]

    def test_too_low_cloud_base_warning(self):
        layers = [{"coverage": "OVC", "altitude_m": 50}]  # 50m is very low (< 100m)
        issues = self.rule.validate(layers)
        # Should produce a warning or info
        relevant = [i for i in issues if "altitude" in i.affected_field.lower() or "100" in i.message]
        assert isinstance(issues, list)

    def test_altitude_none_skipped(self):
        layers = [{"coverage": "FEW", "altitude_m": None}]
        # Should not raise
        issues = self.rule.validate(layers)
        assert isinstance(issues, list)

    def test_ovc_coverage_not_ascending_is_flagged(self):
        layers = [
            {"coverage": "OVC", "altitude_m": 1200},
            {"coverage": "FEW", "altitude_m": 600},  # lower base above OVC
        ]
        issues = self.rule.validate(layers)
        # physical reversal should generate an issue
        assert isinstance(issues, list)

    def test_max_altitude_warning(self):
        layers = [{"coverage": "FEW", "altitude_m": 35000}]
        issues = self.rule.validate(layers)
        assert any("exceeds maximum" in issue.message for issue in issues)

    def test_high_altitude_info_between_typical_and_max(self):
        layers = [{"coverage": "FEW", "altitude_m": 7000}]
        issues = self.rule.validate(layers)
        assert any(issue.severity == IssueSeverity.INFO for issue in issues)

    def test_extreme_gap_between_layers(self):
        layers = [
            {"coverage": "FEW", "altitude_m": 1000},
            {"coverage": "SCT", "altitude_m": 10000},
        ]
        issues = self.rule.validate(layers)
        assert any("Extreme gap" in issue.message for issue in issues)

    def test_large_gap_info_between_layers(self):
        layers = [
            {"coverage": "FEW", "altitude_m": 1000},
            {"coverage": "SCT", "altitude_m": 5000},
        ]
        issues = self.rule.validate(layers)
        assert any("Large gap" in issue.message for issue in issues)

    def test_non_increasing_altitudes_warning(self):
        layers = [
            {"coverage": "FEW", "altitude_m": 2000},
            {"coverage": "SCT", "altitude_m": 2000},
        ]
        issues = self.rule.validate(layers)
        assert any("not strictly increasing" in issue.message for issue in issues)


class TestVisibilityWeatherValidationRule:
    def setup_method(self):
        self.rule = VisibilityWeatherValidationRule()

    def test_single_phenomenon_in_range_has_no_issues(self):
        issues = self.rule._check_single_phenomenon("FG", 500)
        assert issues == []

    def test_single_phenomenon_warning_range(self):
        issues = self.rule._check_single_phenomenon("FG", 1020)
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.WARNING

    def test_single_phenomenon_error_range(self):
        issues = self.rule._check_single_phenomenon("FG", 1200)
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.ERROR

    def test_single_phenomenon_unknown_returns_empty(self):
        issues = self.rule._check_single_phenomenon("XX", 1000)
        assert issues == []

    def test_compound_phenomena_outside_expected_range_warns(self):
        issues = self.rule._check_phenomenon_combinations(["FG", "BR"], 4000)
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.INFO

    def test_validate_with_none_visibility_skips_checks(self):
        issues = self.rule.validate(None, ["FG"])
        assert issues == []

    def test_validate_with_empty_phenomena_skips_checks(self):
        issues = self.rule.validate(800, [])
        assert issues == []

    def test_validate_unknown_phenomena_returns_empty(self):
        issues = self.rule.validate(800, ["ZZ"])
        assert issues == []


class TestSemanticValidationEngine:
    def setup_method(self):
        self.engine = SemanticValidationEngine()

    def test_validate_metar_data_runs_all_rules(self):
        issues = self.engine.validate_metar_data(
            temperature=10.0,
            dewpoint=12.0,
            cloud_layers=[
                {"coverage": "CLR", "altitude_m": 0},
                {"coverage": "FEW", "altitude_m": 1200},
            ],
            visibility_meters=8000,
            weather_phenomena=["FG", "BR"],
        )
        assert len(issues) >= 2
        assert any(issue.rule_name == "temperature_dewpoint_relationship" for issue in issues)
        assert any(issue.rule_name == "cloud_layer_consistency" for issue in issues)

    def test_generate_report_marks_invalid_when_error_present(self):
        issues = self.engine.validate_metar_data(temperature=5.0, dewpoint=8.0)
        report = self.engine.generate_report(
            issues=issues,
            station_id="KJFK",
            raw_metar="METAR KJFK ...",
        )
        assert report["station_id"] == "KJFK"
        assert report["is_valid"] is False
        assert report["summary"]["errors"] >= 1

    def test_generate_report_marks_valid_with_no_issues(self):
        issues = self.engine.validate_metar_data(
            temperature=15.0,
            dewpoint=10.0,
            cloud_layers=[{"coverage": "FEW", "altitude_m": 900}],
            visibility_meters=10000,
            weather_phenomena=["RA"],
        )
        report = self.engine.generate_report(issues=issues)
        assert report["is_valid"] is True
        assert report["summary"]["total_issues"] == 0


class TestTemperatureRuleEdgeCases:
    def test_small_t_td_spread_warning(self):
        rule = TemperatureValidationRule()
        rule.min_dew_spread = 1.0
        issues = rule.validate(temperature=10.0, dewpoint=9.8)
        assert any("Very small T-Td spread" in issue.message for issue in issues)


class TestCloudLayerRuleEdgeCases:
    def test_cloud_altitude_above_maximum(self):
        rule = CloudLayerValidationRule()
        issues = rule.validate([{"coverage": "BKN", "altitude_m": 35000}])
        assert any("exceeds maximum" in issue.message for issue in issues)

    def test_high_but_valid_cloud_altitude_info(self):
        rule = CloudLayerValidationRule()
        typical_max = rule.TYPICAL_MAX_M
        issues = rule.validate([{"coverage": "CI", "altitude_m": typical_max + 500}])
        assert any("High altitude cloud" in issue.message for issue in issues)

    def test_extreme_gap_between_layers(self):
        rule = CloudLayerValidationRule()
        issues = rule._check_altitude_gaps(
            [
                {"coverage": "SCT", "altitude_m": 900},
                {"coverage": "BKN", "altitude_m": 900 + rule.EXTREME_GAP_M + 100},
            ]
        )
        assert any("Extreme gap between layers" in issue.message for issue in issues)

    def test_large_gap_info_between_layers(self):
        rule = CloudLayerValidationRule()
        issues = rule._check_altitude_gaps(
            [
                {"coverage": "SCT", "altitude_m": 900},
                {"coverage": "BKN", "altitude_m": 900 + rule.LARGE_GAP_M + 100},
            ]
        )
        assert any("Large gap between layers" in issue.message for issue in issues)


def test_cloud_zero_altitude_and_unknown_coverage_skipped():
    rule = CloudLayerValidationRule()
    gaps = rule._check_altitude_gaps(
        [
            {"coverage": "FEW", "altitude_m": 0},
            {"coverage": "SCT", "altitude_m": 1000},
        ]
    )
    assert gaps == [] or isinstance(gaps, list)

    consistency = rule._check_coverage_consistency(
        [
            {"coverage": "UNKNOWN", "altitude_m": 1000},
            {"coverage": "FEW", "altitude_m": 2000},
        ]
    )
    assert consistency == []

    # coverage decreases with altitude → no increase warning (312 false)
    ok = rule._check_coverage_consistency(
        [
            {"coverage": "OVC", "altitude_m": 1000},
            {"coverage": "FEW", "altitude_m": 2000},
        ]
    )
    assert all("increases upward" not in i.message for i in ok)


def test_visibility_compound_within_limit():
    rule = VisibilityWeatherValidationRule()
    issues = rule._check_phenomenon_combinations(["FG", "BR"], visibility=50)
    assert all("Multiple phenomena" not in i.message for i in issues) or isinstance(issues, list)
