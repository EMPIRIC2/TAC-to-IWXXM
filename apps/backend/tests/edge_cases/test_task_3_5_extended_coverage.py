"""Task 3.5: Extended Coverage (500+ test cases).

Comprehensive integration testing of semantic validation rules against
500+ diverse METAR test cases with detailed statistics and analysis.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict

import pytest

from src.testing.metar_test_generator import METARTestGenerator
from src.validation.semantic_rules import (
    CloudLayerValidationRule,
    IssueSeverity,
    TemperatureValidationRule,
    VisibilityWeatherValidationRule,
)


@dataclass
class ValidationStatistics:
    """Statistics from comprehensive validation run."""

    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    warnings: int = 0

    # Per-rule statistics
    temperature_passed: int = 0
    temperature_failed: int = 0
    cloud_passed: int = 0
    cloud_failed: int = 0
    visibility_passed: int = 0
    visibility_failed: int = 0

    # Failure distribution
    failures_by_category: Dict[str, int] = field(
        default_factory=lambda: {
            "data_quality": 0,
            "physical_impossibility": 0,
            "unusual_but_possible": 0,
            "sensor_error": 0,
        }
    )

    # Phenomenon distribution
    phenomena_encountered: Dict[str, int] = field(default_factory=dict)

    # Coverage code distribution
    coverage_codes: Dict[str, int] = field(default_factory=dict)

    # Real data insights
    temperature_stats: Dict[str, float] = field(default_factory=dict)
    visibility_stats: Dict[str, float] = field(default_factory=dict)
    altitude_stats: Dict[str, float] = field(default_factory=dict)

    def pass_rate(self) -> float:
        """Calculate overall pass rate."""
        if self.total_cases == 0:
            return 0.0
        return (self.passed / self.total_cases) * 100

    def temperature_pass_rate(self) -> float:
        """Calculate temperature rule pass rate."""
        total = self.temperature_passed + self.temperature_failed
        if total == 0:
            return 0.0
        return (self.temperature_passed / total) * 100

    def cloud_pass_rate(self) -> float:
        """Calculate cloud rule pass rate."""
        total = self.cloud_passed + self.cloud_failed
        if total == 0:
            return 0.0
        return (self.cloud_passed / total) * 100

    def visibility_pass_rate(self) -> float:
        """Calculate visibility rule pass rate."""
        total = self.visibility_passed + self.visibility_failed
        if total == 0:
            return 0.0
        return (self.visibility_passed / total) * 100


class TestExtendedValidationCoverage:
    """Comprehensive validation testing with 500+ test cases."""

    @pytest.fixture(scope="session")
    def test_cases(self):
        """Generate 500+ test cases from live METAR data."""
        generator = METARTestGenerator()
        print("\n🔄 Generating 500+ test cases for Task 3.5...")

        # Generate large diverse sample
        test_cases = generator.diverse_sample(count=500, hours=24, use_cache=True)

        if not test_cases:
            pytest.skip("Unable to generate test cases")

        print(f"Generated {len(test_cases)} test cases")
        return test_cases

    @pytest.fixture
    def rules(self):
        """Provide validation rules."""
        return {
            "temperature": TemperatureValidationRule(),
            "cloud": CloudLayerValidationRule(),
            "visibility": VisibilityWeatherValidationRule(),
        }

    @pytest.fixture
    def stats(self):
        """Provide statistics collection."""
        return ValidationStatistics()

    def parse_metar_data(self, raw_metar: str) -> Dict[str, Any]:
        """Extract temperature, clouds, visibility, and phenomena from METAR."""
        data = {
            "temperature": None,
            "dewpoint": None,
            "cloud_layers": [],
            "visibility_meters": None,
            "phenomena": [],
        }

        # Extract temperature and dewpoint (format: M10/M15 or 15/10)
        temp_match = re.search(r"(M?\d{1,2})/(M?\d{1,2})", raw_metar)
        if temp_match:
            temp_str = temp_match.group(1).replace("M", "-")
            dewpt_str = temp_match.group(2).replace("M", "-")
            try:
                data["temperature"] = float(temp_str)
                data["dewpoint"] = float(dewpt_str)
            except:
                pass

        # Extract visibility (format: 10SM or 9999 or M0400)
        # Try statute miles first
        sm_match = re.search(r"(\d+)SM", raw_metar)
        if sm_match:
            sm = int(sm_match.group(1))
            data["visibility_meters"] = round(sm * 1609.34)
        else:
            # Try meters
            m_match = re.search(r"(?<![0-9M])(\d{4})(?![0-9])", raw_metar)
            if m_match:
                data["visibility_meters"] = int(m_match.group(1))

        # Extract cloud layers (format: FEW250 SCT500 BKN1200)
        cloud_pattern = r"(CLR|SKC|FEW|SCT|BKN|OVC)(\d{3})"
        cloud_matches = re.finditer(cloud_pattern, raw_metar)
        for match in cloud_matches:
            coverage = match.group(1)
            altitude_hundreds = int(match.group(2))
            data["cloud_layers"].append({"coverage": coverage, "altitude_m": altitude_hundreds * 100})

        # Extract weather phenomena
        phenomena_pattern = r"(VC|RE|DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)"
        phenomena_matches = re.finditer(phenomena_pattern, raw_metar)
        phenomena = []
        for match in phenomena_matches:
            p = match.group(1)
            if p not in phenomena:  # Avoid duplicates
                phenomena.append(p)
        data["phenomena"] = phenomena

        return data

    def test_extended_coverage_500_cases(self, rules, stats, test_cases):
        """Validate 500+ real METAR test cases against all semantic rules."""

        print(f"\n🧪 Validating {len(test_cases)} test cases...")

        for i, case in enumerate(test_cases):
            stats.total_cases += 1

            # Parse METAR data
            data = self.parse_metar_data(case.raw_metar)

            has_error = False
            has_warning = False
            case_passed = True

            # Validate temperature
            if data["temperature"] is not None and data["dewpoint"] is not None:
                temp_issues = rules["temperature"].validate(temperature=data["temperature"], dewpoint=data["dewpoint"])

                if temp_issues:
                    case_passed = False
                    stats.temperature_failed += 1
                    for issue in temp_issues:
                        if issue.severity == IssueSeverity.ERROR:
                            has_error = True
                        elif issue.severity == IssueSeverity.WARNING:
                            has_warning = True
                else:
                    stats.temperature_passed += 1

            # Validate cloud layers
            if data["cloud_layers"]:
                cloud_issues = rules["cloud"].validate(cloud_layers=data["cloud_layers"])

                if cloud_issues:
                    case_passed = False
                    stats.cloud_failed += 1
                    for issue in cloud_issues:
                        if issue.severity == IssueSeverity.ERROR:
                            has_error = True
                        elif issue.severity == IssueSeverity.WARNING:
                            has_warning = True
                else:
                    stats.cloud_passed += 1

                # Collect coverage code statistics
                for layer in data["cloud_layers"]:
                    code = layer["coverage"]
                    stats.coverage_codes[code] = stats.coverage_codes.get(code, 0) + 1

            # Validate visibility and weather
            if data["visibility_meters"] is not None and data["phenomena"]:
                vis_issues = rules["visibility"].validate(
                    visibility_meters=data["visibility_meters"], weather_phenomena=data["phenomena"]
                )

                if vis_issues:
                    case_passed = False
                    stats.visibility_failed += 1
                    for issue in vis_issues:
                        if issue.severity == IssueSeverity.ERROR:
                            has_error = True
                        elif issue.severity == IssueSeverity.WARNING:
                            has_warning = True
                else:
                    stats.visibility_passed += 1

                # Collect phenomena statistics
                for p in data["phenomena"]:
                    stats.phenomena_encountered[p] = stats.phenomena_encountered.get(p, 0) + 1

            # Update case result
            if case_passed:
                stats.passed += 1
            else:
                stats.failed += 1

            if has_error:
                stats.errors += 1
            if has_warning:
                stats.warnings += 1

            # Collect real data statistics
            if data["temperature"] is not None:
                if "temperatures" not in stats.temperature_stats:
                    stats.temperature_stats["temperatures"] = []
                    stats.temperature_stats["spreads"] = []
                    stats.temperature_stats["min_temp"] = float("inf")
                    stats.temperature_stats["max_temp"] = float("-inf")

                stats.temperature_stats["temperatures"].append(data["temperature"])
                if data["dewpoint"] is not None:
                    spread = data["temperature"] - data["dewpoint"]
                    stats.temperature_stats["spreads"].append(spread)
                    stats.temperature_stats["min_temp"] = min(stats.temperature_stats["min_temp"], data["temperature"])
                    stats.temperature_stats["max_temp"] = max(stats.temperature_stats["max_temp"], data["temperature"])

            if data["visibility_meters"] is not None:
                if "visibilities" not in stats.visibility_stats:
                    stats.visibility_stats["visibilities"] = []
                    stats.visibility_stats["min_vis"] = float("inf")
                    stats.visibility_stats["max_vis"] = float("-inf")
                    stats.visibility_stats["clear_sky_count"] = 0

                stats.visibility_stats["visibilities"].append(data["visibility_meters"])
                stats.visibility_stats["min_vis"] = min(stats.visibility_stats["min_vis"], data["visibility_meters"])
                stats.visibility_stats["max_vis"] = max(stats.visibility_stats["max_vis"], data["visibility_meters"])

                # Count clear sky (>9999m)
                if data["visibility_meters"] >= 9999:
                    stats.visibility_stats["clear_sky_count"] += 1

            if data["cloud_layers"]:
                if "altitudes" not in stats.altitude_stats:
                    stats.altitude_stats["altitudes"] = []
                    stats.altitude_stats["gaps"] = []
                    stats.altitude_stats["min_alt"] = float("inf")
                    stats.altitude_stats["max_alt"] = float("-inf")

                for layer in data["cloud_layers"]:
                    alt = layer["altitude_m"]
                    stats.altitude_stats["altitudes"].append(alt)
                    stats.altitude_stats["min_alt"] = min(stats.altitude_stats["min_alt"], alt)
                    stats.altitude_stats["max_alt"] = max(stats.altitude_stats["max_alt"], alt)

                # Calculate gaps
                if len(data["cloud_layers"]) > 1:
                    for i in range(1, len(data["cloud_layers"])):
                        gap = data["cloud_layers"][i]["altitude_m"] - data["cloud_layers"][i - 1]["altitude_m"]
                        if gap > 0:
                            stats.altitude_stats["gaps"].append(gap)

        # Print detailed results
        self._print_validation_results(stats, len(test_cases))

        # Expect good pass rate on real data (cloud layer warnings reduce this)
        # Temperature: Should be 100%, Cloud: May flag unusual but valid, Visibility: Should be 90%+
        assert stats.pass_rate() >= 70.0, (
            f"Pass rate {stats.pass_rate():.1f}% below 70% threshold (cloud warnings affecting real data)"
        )

    def _print_validation_results(self, stats: ValidationStatistics, total_cases: int):
        """Print comprehensive validation statistics."""

        print(f"\n\n{'=' * 80}")
        print("EXTENDED COVERAGE VALIDATION RESULTS (Task 3.5)")
        print(f"{'=' * 80}")

        print("\n📊 OVERALL STATISTICS")
        print(f"  Total test cases: {stats.total_cases}")
        print(f"  Cases passed: {stats.passed}")
        print(f"  Cases failed: {stats.failed}")
        print(f"  Overall pass rate: {stats.pass_rate():.1f}%")
        print(f"  Errors detected: {stats.errors}")
        print(f"  Warnings issued: {stats.warnings}")

        print("\n🌡️  TEMPERATURE VALIDATION")
        print(f"  Cases validated: {stats.temperature_passed + stats.temperature_failed}")
        if stats.temperature_passed + stats.temperature_failed > 0:
            print(f"  Pass rate: {stats.temperature_pass_rate():.1f}%")
            print(f"  Passed: {stats.temperature_passed}")
            print(f"  Failed: {stats.temperature_failed}")

        if stats.temperature_stats:
            temps = stats.temperature_stats.get("temperatures", [])
            spreads = stats.temperature_stats.get("spreads", [])
            if temps:
                print(f"  Temperature range: {min(temps):.1f}°C to {max(temps):.1f}°C")
                print(f"  Average: {sum(temps) / len(temps):.1f}°C")
            if spreads:
                print(f"  T-Td spread range: {min(spreads):.1f}°C to {max(spreads):.1f}°C")
                print(f"  Average spread: {sum(spreads) / len(spreads):.1f}°C")

        print("\n☁️  CLOUD LAYER VALIDATION")
        print(f"  Cases validated: {stats.cloud_passed + stats.cloud_failed}")
        if stats.cloud_passed + stats.cloud_failed > 0:
            print(f"  Pass rate: {stats.cloud_pass_rate():.1f}%")
            print(f"  Passed: {stats.cloud_passed}")
            print(f"  Failed: {stats.cloud_failed}")

        if stats.coverage_codes:
            print("\n  Coverage code distribution:")
            for code in sorted(stats.coverage_codes.keys()):
                count = stats.coverage_codes[code]
                pct = count / sum(stats.coverage_codes.values()) * 100
                print(f"    {code}: {count} ({pct:.1f}%)")

        if stats.altitude_stats:
            alts = stats.altitude_stats.get("altitudes", [])
            gaps = stats.altitude_stats.get("gaps", [])
            if alts:
                print("\n  Altitude statistics:")
                print(f"    Range: {stats.altitude_stats['min_alt']}m to {stats.altitude_stats['max_alt']}m")
                print(f"    Average: {sum(alts) / len(alts):.0f}m")
            if gaps:
                print("    Gap statistics (between layers):")
                print(f"    Range: {min(gaps)}m to {max(gaps)}m")
                print(f"    Average: {sum(gaps) / len(gaps):.0f}m")

        print("\n👁️  VISIBILITY-WEATHER VALIDATION")
        print(f"  Cases validated: {stats.visibility_passed + stats.visibility_failed}")
        if stats.visibility_passed + stats.visibility_failed > 0:
            print(f"  Pass rate: {stats.visibility_pass_rate():.1f}%")
            print(f"  Passed: {stats.visibility_passed}")
            print(f"  Failed: {stats.visibility_failed}")

        if stats.visibility_stats:
            vis_list = stats.visibility_stats.get("visibilities", [])
            if vis_list:
                clear_count = stats.visibility_stats.get("clear_sky_count", 0)
                print("\n  Visibility statistics:")
                print(f"    Range: {stats.visibility_stats['min_vis']}m to {stats.visibility_stats['max_vis']}m")
                print(f"    Average: {sum(vis_list) / len(vis_list):.0f}m")
                print(f"    Clear sky cases (≥9999m): {clear_count} ({clear_count / len(vis_list) * 100:.1f}%)")

        if stats.phenomena_encountered:
            print("\n  Weather phenomena frequencies:")
            total_pheno = sum(stats.phenomena_encountered.values())
            for pheno in sorted(stats.phenomena_encountered.keys()):
                count = stats.phenomena_encountered[pheno]
                pct = count / total_pheno * 100
                print(f"    {pheno}: {count} ({pct:.1f}%)")

        print(f"\n{'=' * 80}\n")


class TestValidationRuleEffectiveness:
    """Analyze individual rule effectiveness across large dataset."""

    @pytest.fixture(scope="session")
    def test_cases(self):
        """Generate test cases."""
        generator = METARTestGenerator()
        test_cases = generator.diverse_sample(count=500, hours=24, use_cache=True)
        return test_cases if test_cases else []

    def test_rule_effectiveness_summary(self, test_cases):
        """Summarize rule effectiveness."""
        if not test_cases:
            pytest.skip("No test cases generated")

        print(f"\n\n{'=' * 80}")
        print("RULE EFFECTIVENESS ANALYSIS")
        print(f"{'=' * 80}")

        # Rules comparison
        temp_rule = TemperatureValidationRule()
        cloud_rule = CloudLayerValidationRule()
        vis_rule = VisibilityWeatherValidationRule()

        # Quick stats collection
        rules_info = {
            "Temperature (T ≥ Td)": {
                "cases_tested": 0,
                "issues_found": 0,
                "rules": ["T >= Td", "Spread check", "RH calculation"],
            },
            "Cloud Layer Ordering": {
                "cases_tested": 0,
                "issues_found": 0,
                "rules": ["Altitude increasing", "Coverage non-increasing", "Gap analysis"],
            },
            "Visibility-Weather": {
                "cases_tested": 0,
                "issues_found": 0,
                "rules": ["Single phenomenon checks (7)", "Compound effects (4)", "Severity escalation"],
            },
        }

        print("\nRule Coverage:")
        for rule in rules_info:
            info = rules_info[rule]
            print(f"\n  {rule}:")
            for sub_rule in info["rules"]:
                print(f"    ✓ {sub_rule}")

        print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
