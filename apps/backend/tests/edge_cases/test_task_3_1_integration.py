"""Integration tests for Task 3.1: Temperature & Dewpoint Validation.

Tests the TemperatureValidationRule against real test case data.
This validates that semantic validation works correctly with production data.
"""

import pytest

from src.testing.metar_test_generator import METARTestGenerator
from src.validation.semantic_rules import (
    IssueSeverity,
    SemanticValidationEngine,
    TemperatureValidationRule,
)


@pytest.fixture(scope="session")
def test_cases():
    """Generate test cases from live API data."""
    generator = METARTestGenerator()
    print("\n🔄 Generating diverse METAR test cases for Task 3.1...")

    test_cases = generator.diverse_sample(count=100, hours=3, use_cache=True)

    if not test_cases:
        pytest.skip("Unable to generate test cases")

    return test_cases


class TestTemperatureValidationWithRealData:
    """Test temperature validation against real METAR data."""

    @pytest.fixture
    def rule(self):
        """Provide temperature validation rule."""
        return TemperatureValidationRule()

    @pytest.fixture
    def engine(self):
        """Provide validation engine."""
        return SemanticValidationEngine()

    def parse_temp_dewpoint(self, raw_metar: str):
        """Extract temperature and dewpoint from raw METAR text.

        METAR format: ... TT/Td ...
        Where TT is temperature and Td is dewpoint
        Format: 21/15, M02/M10, etc.
        """
        import re

        # Pattern: temperature/dewpoint with optional minus sign
        # e.g., "21/15", "M02/M10", "05/03"
        pattern = r"(M?\d{2})/(M?\d{2})"
        match = re.search(pattern, raw_metar)

        if match:
            temp_str, dewpoint_str = match.groups()

            # Parse temperature
            temp = -int(temp_str[1:]) if temp_str.startswith("M") else int(temp_str)
            # Parse dewpoint
            dewpoint = -int(dewpoint_str[1:]) if dewpoint_str.startswith("M") else int(dewpoint_str)

            return temp, dewpoint

        return None, None

    def test_temperature_validation_with_real_metars(self, rule, test_cases):
        """Validate temperature across real METAR test cases.

        Expected: Real METARs should have valid thermodynamics (T >= Td).
        """
        errors = []
        valid_count = 0
        invalid_count = 0
        missing_count = 0

        for i, case in enumerate(test_cases):
            metar_text = case.raw_metar

            # Extract temperature and dewpoint from raw METAR
            T, Td = self.parse_temp_dewpoint(metar_text)

            if T is None or Td is None:
                missing_count += 1
                continue

            # Validate
            issues = rule.validate(temperature=T, dewpoint=Td)

            # Check for critical errors
            has_error = any(i.severity == IssueSeverity.ERROR for i in issues)

            if has_error:
                invalid_count += 1
                errors.append(
                    {
                        "station": case.station_id,
                        "metar": metar_text,
                        "temperature": T,
                        "dewpoint": Td,
                        "issues": [{"severity": i.severity.name, "message": i.message} for i in issues],
                    }
                )
            else:
                valid_count += 1
                # Calculate RH for valid data
                rh = rule.calculate_relative_humidity(T, Td)
                # Sanity check
                assert 0 <= rh <= 105, f"RH out of bounds: {rh}% for T={T}, Td={Td}"

        # Report results
        print(f"\n\n{'=' * 70}")
        print("Temperature Validation Results (Task 3.1)")
        print(f"{'=' * 70}")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Valid (T >= Td): {valid_count}")
        print(f"Invalid (T < Td): {invalid_count}")
        print(f"Missing data: {missing_count}")

        if valid_count + invalid_count > 0:
            success_rate = valid_count / (valid_count + invalid_count) * 100
            print(f"Success rate: {success_rate:.1f}%")

        # Log any errors for investigation
        if errors:
            print("\nInvalid cases detected:")
            for error in errors[:5]:  # Show first 5
                print(f"  [{error['station']}] {error['metar'][:50]}")
                print(f"    T={error['temperature']}°C, Td={error['dewpoint']}°C")
        print(f"{'=' * 70}\n")

        # Expect at least 95% of real data to pass validation
        if valid_count + invalid_count > 0:
            assert (valid_count / (valid_count + invalid_count)) >= 0.95, (
                f"Too many invalid thermodynamics: {invalid_count} errors"
            )

    def test_engine_processes_all_cases(self, engine, test_cases):
        """Test that the validation engine processes all test cases without crashes.

        Expected: Engine should handle all cases gracefully.
        """
        processed = 0
        errors = []

        for i, case in enumerate(test_cases):
            try:
                # Import re for parsing
                import re

                # Parse temperature and dewpoint
                temp_pattern = r"(M?\d{2})/(M?\d{2})"
                temp_match = re.search(temp_pattern, case.raw_metar)

                T = None
                Td = None
                if temp_match:
                    temp_str, dewpoint_str = temp_match.groups()
                    T = -int(temp_str[1:]) if temp_str.startswith("M") else int(temp_str)
                    Td = -int(dewpoint_str[1:]) if dewpoint_str.startswith("M") else int(dewpoint_str)

                # Run full validation
                issues = engine.validate_metar_data(
                    temperature=T,
                    dewpoint=Td,
                    cloud_layers=None,
                    visibility_meters=None,
                    weather_phenomena=case.weather_phenomena,
                )

                # Generate report
                report = engine.generate_report(issues, station_id=case.station_id, raw_metar=case.raw_metar)

                # Report should be valid
                assert "station_id" in report
                assert "is_valid" in report
                assert "summary" in report

                processed += 1

            except Exception as e:
                errors.append({"station": case.station_id, "metar": case.raw_metar[:50], "error": str(e)})

        # Report results
        print(f"\n\n{'=' * 70}")
        print("Engine Processing Results")
        print(f"{'=' * 70}")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Successfully processed: {processed}")
        print(f"Processing errors: {len(errors)}")

        if errors:
            print("\nFirst processing error:")
            print(f"  [{errors[0]['station']}] {errors[0]['metar']}")
            print(f"  Error: {errors[0]['error'][:100]}")
        print(f"{'=' * 70}\n")

        # All cases should be processable
        assert len(errors) == 0, f"Engine crashed on {len(errors)} cases"
        assert processed == len(test_cases), f"Only processed {processed}/{len(test_cases)}"

    def test_relative_humidity_statistics(self, rule, test_cases):
        """Compute RH statistics across all test cases.

        Expected: RH should follow realistic distribution.
        """
        import re

        rh_values = []
        spreads = []

        for case in test_cases:
            # Parse temperature and dewpoint
            temp_pattern = r"(M?\d{2})/(M?\d{2})"
            temp_match = re.search(temp_pattern, case.raw_metar)

            if temp_match:
                temp_str, dewpoint_str = temp_match.groups()
                T = -int(temp_str[1:]) if temp_str.startswith("M") else int(temp_str)
                Td = -int(dewpoint_str[1:]) if dewpoint_str.startswith("M") else int(dewpoint_str)

                if T >= Td:
                    rh = rule.calculate_relative_humidity(T, Td)
                    rh_values.append(rh)
                    spreads.append(T - Td)

        if not rh_values:
            pytest.skip("No valid temperature data")

        # Calculate statistics
        min_rh = min(rh_values)
        max_rh = max(rh_values)
        avg_rh = sum(rh_values) / len(rh_values)

        min_spread = min(spreads)
        max_spread = max(spreads)
        avg_spread = sum(spreads) / len(spreads)

        # Report statistics
        print(f"\n\n{'=' * 70}")
        print("Relative Humidity Statistics (Task 3.1)")
        print(f"{'=' * 70}")
        print(f"Sample size: {len(rh_values)} METARs")
        print(f"RH range: {min_rh:.1f}% - {max_rh:.1f}%")
        print(f"RH average: {avg_rh:.1f}%")
        print(f"T-Td spread: {min_spread:.1f}°C - {max_spread:.1f}°C")
        print(f"Average spread: {avg_spread:.1f}°C")
        print(f"{'=' * 70}\n")

        # Sanity checks
        assert 0 <= min_rh <= 100, "Min RH out of bounds"
        assert 0 <= max_rh <= 105, "Max RH out of bounds"
        assert avg_rh > 0, "Average RH is zero"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
