"""Integration tests for Task 3.2: Cloud Layer Ordering Validation.

Tests enhanced cloud layer validation against real METAR test data.
"""

import re

import pytest
from src.testing.metar_test_generator import METARTestGenerator
from src.validation.semantic_rules import (
    CloudLayerValidationRule,
    IssueSeverity,
)


@pytest.fixture(scope="session")
def test_cases():
    """Generate test cases from live API data."""
    generator = METARTestGenerator()
    print("\n🔄 Generating test cases for Task 3.2...")

    test_cases = generator.diverse_sample(count=50, hours=3, use_cache=True)

    if not test_cases:
        pytest.skip("Unable to generate test cases")

    return test_cases


def parse_cloud_layers(raw_metar: str):
    """Extract cloud layers from raw METAR text.

    METAR format: ... FEW250 SCT500 BKN1200 OVC2500 ...
    Where coverage code followed by altitude in hundreds of feet.
    """
    # Pattern: coverage_code (FEW/SCT/BKN/OVC/SKC/CLR) followed by digits
    pattern = r"(FEW|SCT|BKN|OVC|SKC|CLR|VV)(\d{3})?"
    matches = re.findall(pattern, raw_metar)

    layers = []
    for coverage, altitude_hundreds in matches:
        if altitude_hundreds:
            # Convert hundreds of feet to meters
            altitude_ft = int(altitude_hundreds) * 100
            altitude_m = round(altitude_ft * 0.3048)  # ft to m conversion
            layers.append({"coverage": coverage, "altitude_m": altitude_m})
        else:
            # CLR/SKC without altitude
            layers.append({"coverage": coverage, "altitude_m": 0})

    return layers


class TestCloudLayerValidationWithRealData:
    """Test cloud layer validation against real METAR data."""

    @pytest.fixture
    def rule(self):
        """Provide cloud layer validation rule."""
        return CloudLayerValidationRule()

    def test_cloud_layers_from_real_metars(self, rule, test_cases):
        """Validate cloud layers from real METAR test cases.

        Expected: Real METARs should have valid cloud ordering.
        """
        errors = []
        valid_count = 0
        invalid_count = 0
        no_clouds_count = 0

        for _i, case in enumerate(test_cases):
            metar_text = case.raw_metar

            # Extract cloud layers from raw METAR
            layers = parse_cloud_layers(metar_text)

            if not layers:
                no_clouds_count += 1
                continue

            # Validate
            issues = rule.validate(layers)

            # Check for critical errors
            has_error = any(j.severity == IssueSeverity.ERROR for j in issues)

            if has_error:
                invalid_count += 1
                errors.append(
                    {
                        "station": case.station_id,
                        "metar": metar_text,
                        "layers": layers,
                        "issues": [{"severity": j.severity.name, "message": j.message} for j in issues],
                    }
                )
            else:
                valid_count += 1

        # Report results
        print(f"\n\n{'=' * 70}")
        print("Cloud Layer Validation Results (Task 3.2)")
        print(f"{'=' * 70}")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Cases with clouds: {valid_count + invalid_count}")
        print(f"Valid cloud sequences: {valid_count}")
        print(f"Invalid cloud sequences: {invalid_count}")
        print(f"Cases without clouds: {no_clouds_count}")

        if valid_count + invalid_count > 0:
            success_rate = valid_count / (valid_count + invalid_count) * 100
            print(f"Success rate: {success_rate:.1f}%")

        # Log any errors for investigation
        if errors:
            print("\nInvalid cases detected:")
            for error in errors[:3]:  # Show first 3
                print(f"  [{error['station']}] {error['metar'][:60]}")
                print(f"    Layers: {[l['coverage'] for l in error['layers']]}")
                print(f"    Issues: {len(error['issues'])}")
        print(f"{'=' * 70}\n")

        # Expect at least 90% of real data to pass validation
        if valid_count + invalid_count > 0:
            assert (valid_count / (valid_count + invalid_count)) >= 0.90, (
                f"Too many invalid cloud sequences: {invalid_count} errors"
            )

    def test_altitude_ordering_statistics(self, rule, test_cases):
        """Compute altitude statistics for cloud layers."""
        layer_counts = []
        altitude_gaps = []
        altitude_ranges = []

        for case in test_cases:
            layers = parse_cloud_layers(case.raw_metar)

            if len(layers) > 1:
                layer_counts.append(len(layers))

                # Sort by altitude for gap analysis
                sorted_layers = sorted(layers, key=lambda x: x["altitude_m"])

                # Calculate gaps
                for i in range(len(sorted_layers) - 1):
                    gap = sorted_layers[i + 1]["altitude_m"] - sorted_layers[i]["altitude_m"]
                    if gap > 0:
                        altitude_gaps.append(gap)

                # Range (max altitude in layer sequence)
                max_alt = max(l["altitude_m"] for l in layers)
                altitude_ranges.append(max_alt)

        if not layer_counts:
            pytest.skip("No multi-layer cloud cases")

        # Calculate statistics
        avg_layers = sum(layer_counts) / len(layer_counts)
        max_layers = max(layer_counts)

        if altitude_gaps:
            min_gap = min(altitude_gaps)
            max_gap = max(altitude_gaps)
            avg_gap = sum(altitude_gaps) / len(altitude_gaps)

            min_range = min(altitude_ranges)
            max_range = max(altitude_ranges)
            avg_range = sum(altitude_ranges) / len(altitude_ranges)
        else:
            min_gap = max_gap = avg_gap = 0
            min_range = max_range = avg_range = 0

        # Report statistics
        print(f"\n\n{'=' * 70}")
        print("Cloud Layer Altitude Statistics (Task 3.2)")
        print(f"{'=' * 70}")
        print(f"Multi-layer sequences: {len(layer_counts)}")
        print(f"Layers per sequence: avg {avg_layers:.1f}, max {max_layers}")
        print("\nAltitude gaps (between layers):")
        print(f"  Min gap: {min_gap:.0f}m")
        print(f"  Max gap: {max_gap:.0f}m")
        print(f"  Avg gap: {avg_gap:.0f}m")
        print("\nCloud layer altitude ranges:")
        print(f"  Min range: {min_range:.0f}m")
        print(f"  Max range: {max_range:.0f}m")
        print(f"  Avg range: {avg_range:.0f}m")
        print(f"{'=' * 70}\n")

        # Sanity checks
        assert max_layers >= 1, "Should have multi-layer sequences"
        assert avg_gap > 0, "Average gap should be positive"

    def test_coverage_distribution(self, rule, test_cases):
        """Analyze cloud coverage distribution."""
        coverage_counts = {}
        coverage_sequences = []

        for case in test_cases:
            layers = parse_cloud_layers(case.raw_metar)

            if layers:
                # Count coverage types
                for layer in layers:
                    cov = layer["coverage"]
                    coverage_counts[cov] = coverage_counts.get(cov, 0) + 1

                # Track sequences
                seq = " → ".join([l["coverage"] for l in sorted(layers, key=lambda x: x["altitude_m"])])
                coverage_sequences.append(seq)

        if not coverage_counts:
            pytest.skip("No cloud data")

        # Report statistics
        print(f"\n\n{'=' * 70}")
        print("Cloud Coverage Distribution (Task 3.2)")
        print(f"{'=' * 70}")
        print("Coverage type frequencies:")
        for coverage in sorted(coverage_counts.keys()):
            count = coverage_counts[coverage]
            pct = count / sum(coverage_counts.values()) * 100
            print(f"  {coverage}: {count} ({pct:.1f}%)")

        print("\nMost common sequences (first 5):")
        from collections import Counter

        seq_counts = Counter(coverage_sequences)
        for seq, count in seq_counts.most_common(5):
            print(f"  {seq}: {count} times")
        print(f"{'=' * 70}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
