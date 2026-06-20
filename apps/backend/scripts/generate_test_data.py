"""Generate and analyze diverse METAR test data.

This script generates test data from live AviationWeather.gov API and
produces coverage reports.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv

load_dotenv(backend_dir.parent / ".env")
load_dotenv(backend_dir / ".env")

from src.testing.metar_test_generator import METARTestGenerator


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def generate_diverse_sample(generator: METARTestGenerator, count: int = 200):
    """Generate diverse sample and print statistics."""
    print_section("Generating Diverse Sample")

    print(f"\n🔄 Fetching {count} METARs from {len(generator.WORLD_REGIONS)} world regions...")
    print(f"   Regions: {', '.join(generator.WORLD_REGIONS.keys())}")

    # Check if API key is configured
    api_key = os.getenv("OPENAIP_API_KEY")
    if api_key:
        print("   ✓ OpenAIP API key configured")
    else:
        print("   ℹ OpenAIP API key not found (will use local data only)")

    # Generate test cases
    test_cases = generator.diverse_sample(count=count, hours=3, use_cache=False)

    print(f"\n✅ Generated {len(test_cases)} test cases")

    # Print coverage statistics
    coverage = generator.get_coverage_report()

    print("\n📊 Coverage Statistics:")
    print(f"   Total test cases: {coverage.total_cases}")
    print(f"   Unique stations: {len(coverage.unique_stations)}")
    print(f"   Countries: {len(coverage.countries)}")
    print(f"   Regions: {len(coverage.regions)}")

    print("\n🌤️  Weather Phenomena Coverage:")
    print(f"   Found {len(coverage.weather_phenomena)} types: {sorted(coverage.weather_phenomena)}")

    print("\n☁️  Cloud Coverage:")
    print(f"   Cloud amounts: {sorted(coverage.cloud_amounts)}")
    print(f"   Cloud types: {sorted(coverage.cloud_types)}")

    print("\n📈 Complexity Distribution:")
    print(f"   Simple (0-2):   {coverage.simple_cases:3d} ({coverage.simple_cases / coverage.total_cases * 100:.1f}%)")
    print(f"   Medium (3-6):   {coverage.medium_cases:3d} ({coverage.medium_cases / coverage.total_cases * 100:.1f}%)")
    print(
        f"   Complex (7+):   {coverage.complex_cases:3d} ({coverage.complex_cases / coverage.total_cases * 100:.1f}%)"
    )

    # Show sample test cases
    print("\n📋 Sample Test Cases:")
    for i, test_case in enumerate(test_cases[:5], 1):
        print(f"\n   {i}. {test_case.station_id} ({test_case.region}, {test_case.country})")
        print(f"      {test_case.raw_metar[:80]}...")
        print(f"      Weather: {test_case.weather_phenomena}")
        print(f"      Clouds: {test_case.cloud_amounts}")
        print(f"      Complexity: {test_case.complexity_score()}")

    # Save coverage report
    generator.save_coverage_report()
    print(f"\n💾 Coverage report saved to {generator.cache_dir / 'coverage_report.json'}")

    return test_cases


def generate_regional_samples(generator: METARTestGenerator):
    """Generate samples from each region."""
    print_section("Regional Coverage Analysis")

    for region_name in generator.WORLD_REGIONS.keys():
        print(f"\n🌍 {region_name.replace('_', ' ').title()}:")

        try:
            test_cases = generator.regional_sample(region=region_name, count=30, hours=3, use_cache=False)

            print(f"   ✓ {len(test_cases)} test cases")

            # Count phenomena in this region
            phenomena = set()
            for tc in test_cases:
                phenomena.update(tc.weather_phenomena)

            if phenomena:
                print(f"   ✓ Weather phenomena: {sorted(phenomena)}")

        except Exception as e:
            print(f"   ✗ Failed: {e}")


def generate_phenomenon_coverage(generator: METARTestGenerator):
    """Generate coverage for specific phenomena."""
    print_section("Weather Phenomenon Targeted Coverage")

    target_phenomena = [
        ("RA", "Rain"),
        ("SN", "Snow"),
        ("TS", "Thunderstorm"),
        ("TSRA", "Thunderstorm with Rain"),
        ("FG", "Fog"),
        ("BR", "Mist"),
        ("HZ", "Haze"),
        ("NSW", "No Significant Weather"),
        ("CB", "Cumulonimbus"),
        ("TCU", "Towering Cumulus"),
    ]

    print("\n🎯 Searching for specific weather phenomena...")

    for code, description in target_phenomena:
        try:
            test_cases = generator.phenomenon_coverage(required_phenomena=[code], hours=6, use_cache=False)

            if test_cases:
                stations = [tc.station_id for tc in test_cases[:3]]
                print(f"   ✓ {code:6s} ({description:25s}): {len(test_cases):3d} cases - {', '.join(stations)}")
            else:
                print(f"   ✗ {code:6s} ({description:25s}): Not found")

        except Exception as e:
            print(f"   ✗ {code:6s} ({description:25s}): Error - {e}")


def print_api_configuration():
    """Print API configuration status."""
    print_section("API Configuration Status")

    # Check environment variables
    configs = {
        "AviationWeather API": {
            "enabled": True,
            "url": "https://aviationweather.gov/api/data",
            "note": "No API key required",
        },
        "OpenAIP API": {
            "enabled": bool(os.getenv("OPENAIP_API_KEY")),
            "key": os.getenv("OPENAIP_API_KEY", "Not configured")[:20] + "...",
            "note": "For downloading airport data",
        },
        "WMO Codelists": {
            "enabled": os.getenv("WMO_ONLINE_VALIDATION", "true").lower() == "true",
            "url": "https://codes.wmo.int",
            "note": "For validation",
        },
        "Live API Tests": {
            "enabled": os.getenv("ENABLE_LIVE_API_TESTS", "true").lower() == "true",
            "note": "Enable/disable internet-dependent tests",
        },
    }

    for name, config in configs.items():
        status = "✓ ENABLED" if config.get("enabled") else "✗ DISABLED"
        print(f"\n{name:25s}: {status}")
        for key, value in config.items():
            if key != "enabled":
                print(f"   {key:15s}: {value}")


def main():
    """Main entry point."""
    print("\n" + "#" * 70)
    print("#  METAR Test Generator - Sprint 2")
    print("#  Dynamic Test Data Generation from Live APIs")
    print("#" * 70)

    # Print API configuration
    print_api_configuration()

    # Initialize generator
    print_section("Initializing Test Generator")
    print("\n🔧 Setting up clients...")

    try:
        generator = METARTestGenerator()
        print("   ✓ AviationWeatherClient initialized")
        print("   ✓ OpenAIPClient initialized")
        print("   ✓ WMOCodelistsClient initialized")
        print("   ✓ AirportReconciliationService initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize generator: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Generate diverse sample
    try:
        test_cases = generate_diverse_sample(generator, count=200)
    except Exception as e:
        print(f"\n❌ Failed to generate diverse sample: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Generate regional samples
    try:
        generate_regional_samples(generator)
    except Exception as e:
        print(f"\n⚠️  Regional sampling failed: {e}")

    # Generate phenomenon coverage
    try:
        generate_phenomenon_coverage(generator)
    except Exception as e:
        print(f"\n⚠️  Phenomenon coverage failed: {e}")

    # Final summary
    print_section("Generation Complete")

    coverage = generator.get_coverage_report()

    print("\n✅ Successfully generated comprehensive test dataset")
    print("\n📊 Final Statistics:")
    print(f"   Total test cases: {coverage.total_cases}")
    print(f"   Unique stations: {len(coverage.unique_stations)}")
    print(f"   Countries covered: {len(coverage.countries)}")
    print(f"   Regions covered: {len(coverage.regions)}")
    print(f"   Weather phenomena: {len(coverage.weather_phenomena)}")
    print(f"   Cloud types: {len(coverage.cloud_types)}")

    print(f"\n💾 Data cached in: {generator.cache_dir}")
    print("   - Coverage report: coverage_report.json")
    print("   - Test cases: diverse_sample_*.json")
    print("   - Regional samples: regional_*.json")
    print("   - Phenomenon coverage: phenomena_coverage_*.json")

    print("\n🧪 Next Steps:")
    print("   1. Run tests: pytest tests/test_dynamic_metar_generation.py -v")
    print(f"   2. View coverage report: cat {generator.cache_dir}/coverage_report.json")
    print("   3. Analyze failures: ls test-reports/dynamic-test-failures/")

    print("\n" + "#" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
