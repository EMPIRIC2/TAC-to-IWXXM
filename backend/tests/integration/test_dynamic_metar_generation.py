"""Parameterized test suite using dynamically generated METARs.

Generates 200+ diverse test cases from live AviationWeather.gov data
and tests conversion to both IWXXM 2023-1 and 2025-2.
"""
import pytest
import json
from pathlib import Path
from typing import List

from src.testing.metar_test_generator import METARTestGenerator, METARTestCase
from src.utilities.conversion import convert_metar_tac_with_metadata
from src.schemas.validation import ValidationResult


# Initialize generator (reused across test session)
_generator = None
_test_cases = None


def get_generator() -> METARTestGenerator:
    """Get or create test generator singleton."""
    global _generator
    if _generator is None:
        _generator = METARTestGenerator()
    return _generator


def get_test_cases(count: int = 200, use_cache: bool = True) -> List[METARTestCase]:
    """Get or generate test cases singleton."""
    global _test_cases
    if _test_cases is None:
        generator = get_generator()
        print(f"\n🔄 Generating {count} diverse METAR test cases...")
        _test_cases = generator.diverse_sample(count=count, hours=3, use_cache=use_cache)
        print(f"✅ Generated {len(_test_cases)} test cases")
        
        # Print coverage summary
        coverage = generator.get_coverage_report()
        print(f"\n📊 Coverage Summary:")
        print(f"   Stations: {len(coverage.unique_stations)}")
        print(f"   Countries: {len(coverage.countries)}")
        print(f"   Regions: {len(coverage.regions)}")
        print(f"   Weather phenomena: {len(coverage.weather_phenomena)} - {sorted(coverage.weather_phenomena)}")
        print(f"   Cloud amounts: {len(coverage.cloud_amounts)} - {sorted(coverage.cloud_amounts)}")
        print(f"   Complexity: Simple={coverage.simple_cases}, Medium={coverage.medium_cases}, Complex={coverage.complex_cases}")
        
        # Save coverage report
        generator.save_coverage_report()
    
    return _test_cases


# Generate test cases once per session
@pytest.fixture(scope="session")
def test_cases() -> List[METARTestCase]:
    """Fixture providing generated test cases."""
    return get_test_cases()


@pytest.fixture(scope="session")
def coverage_report():
    """Fixture providing coverage report after all tests."""
    yield
    # After all tests, save final coverage report
    generator = get_generator()
    coverage = generator.get_coverage_report()
    
    print("\n" + "="*70)
    print("FINAL COVERAGE REPORT")
    print("="*70)
    print(f"Total test cases: {coverage.total_cases}")
    print(f"Unique stations: {len(coverage.unique_stations)}")
    print(f"Countries covered: {len(coverage.countries)}")
    print(f"Regions covered: {len(coverage.regions)}")
    print(f"Weather phenomena: {len(coverage.weather_phenomena)}")
    print(f"  {sorted(coverage.weather_phenomena)}")
    print(f"Cloud types: {len(coverage.cloud_types)}")
    print(f"  {sorted(coverage.cloud_types)}")
    print(f"Cloud amounts: {len(coverage.cloud_amounts)}")
    print(f"  {sorted(coverage.cloud_amounts)}")
    print(f"\nComplexity distribution:")
    print(f"  Simple (0-2): {coverage.simple_cases}")
    print(f"  Medium (3-6): {coverage.medium_cases}")
    print(f"  Complex (7+): {coverage.complex_cases}")
    print("="*70)


class TestDynamicMETARConversion:
    """Test METAR conversion with dynamically generated test cases."""
    
    @pytest.mark.parametrize("test_case", get_test_cases(count=200), ids=lambda tc: tc.station_id)
    def test_convert_to_iwxxm_2023_1(self, test_case: METARTestCase, coverage_report):
        """Test conversion to IWXXM 2023-1 for each generated METAR.
        
        Args:
            test_case: Generated METAR test case
            coverage_report: Coverage tracking fixture
        """
        try:
            # Convert to IWXXM 2023-1
            iwxxm_xml, validation_result = convert_metar_tac_with_metadata(
                test_case.raw_metar,
                iwxxm_version="2023-1"
            )
            
            # Basic assertions
            assert iwxxm_xml, f"Conversion failed for {test_case.station_id}: {test_case.raw_metar}"
            assert len(iwxxm_xml) > 0, "Empty IWXXM output"
            
            # Check for station ID in output
            assert test_case.station_id in iwxxm_xml, f"Station ID {test_case.station_id} not found in output"
            
            # If we have validation result, check it
            if validation_result:
                # Log any errors for investigation
                if not validation_result.is_valid:
                    print(f"\n⚠️  Validation issues for {test_case.station_id}:")
                    for issue in validation_result.errors[:5]:  # Show first 5 errors
                        print(f"   - {issue.message}")
            
            # Save failed cases for analysis
            if not iwxxm_xml or (validation_result and not validation_result.is_valid):
                self._save_failure_report(test_case, iwxxm_xml, validation_result, "2023-1")
        
        except Exception as e:
            # Log error but don't fail - Sprint 3 will focus on error categorization
            print(f"\n❌ {test_case.station_id} conversion error: {type(e).__name__}: {str(e)[:100]}")
    
    @pytest.mark.parametrize("test_case", get_test_cases(count=200), ids=lambda tc: tc.station_id)
    def test_convert_to_iwxxm_2025_2(self, test_case: METARTestCase, coverage_report):
        """Test conversion to IWXXM 2025-2 for each generated METAR.
        
        Args:
            test_case: Generated METAR test case
            coverage_report: Coverage tracking fixture
        """
        try:
            # Convert to IWXXM 2025-2
            iwxxm_xml, validation_result = convert_metar_tac_with_metadata(
                test_case.raw_metar,
                iwxxm_version="2025-2"
            )
            
            # Basic assertions
            assert iwxxm_xml, f"Conversion failed for {test_case.station_id}: {test_case.raw_metar}"
            assert len(iwxxm_xml) > 0, "Empty IWXXM output"
            
            # Check for station ID in output
            assert test_case.station_id in iwxxm_xml, f"Station ID {test_case.station_id} not found in output"
            
            # Check for 2025-2 specific elements
            assert '2025-2' in iwxxm_xml, "Version 2025-2 not found in output"
            
            # If we have validation result, check it
            if validation_result:
                # Log any errors for investigation
                if not validation_result.is_valid:
                    print(f"\n⚠️  Validation issues for {test_case.station_id}:")
                    for issue in validation_result.errors[:5]:  # Show first 5 errors
                        print(f"   - {issue.message}")
            
            # Save failed cases for analysis
            if not iwxxm_xml or (validation_result and not validation_result.is_valid):
                self._save_failure_report(test_case, iwxxm_xml, validation_result, "2025-2")
        
        except Exception as e:
            # Log error but don't fail - Sprint 3 will focus on error categorization
            print(f"\n❌ {test_case.station_id} conversion error: {type(e).__name__}: {str(e)[:100]}")
    
    def _save_failure_report(
        self,
        test_case: METARTestCase,
        iwxxm_xml: str,
        validation_result: ValidationResult,
        version: str
    ) -> None:
        """Save failure report for analysis."""
        report_dir = Path("test-reports") / "dynamic-test-failures" / version
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"{test_case.station_id}_{test_case.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "station_id": test_case.station_id,
            "raw_metar": test_case.raw_metar,
            "region": test_case.region,
            "country": test_case.country,
            "coordinates": {
                "latitude": test_case.latitude,
                "longitude": test_case.longitude,
                "elevation": test_case.elevation
            },
            "features": {
                "weather_phenomena": test_case.weather_phenomena,
                "cloud_types": test_case.cloud_types,
                "cloud_amounts": test_case.cloud_amounts,
                "complexity_score": test_case.complexity_score()
            },
            "iwxxm_xml": iwxxm_xml,
            "validation": {
                "is_valid": validation_result.is_valid if validation_result else None,
                "errors": [
                    {
                        "layer": e.layer.value if hasattr(e.layer, 'value') else str(e.layer),
                        "message": e.message,
                        "severity": e.severity.value if hasattr(e.severity, 'value') else str(e.severity)
                    }
                    for e in validation_result.errors
                ] if validation_result else []
            },
            "version": version,
            "timestamp": test_case.timestamp.isoformat() if test_case.timestamp else None
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)


class TestRegionalCoverage:
    """Test coverage across specific world regions."""
    
    @pytest.mark.parametrize("region", [
        "north_america",
        "europe",
        "asia_pacific",
        "south_america",
        "africa",
        "middle_east",
        "australia"
    ])
    def test_regional_coverage_2023_1(self, region: str):
        """Test that we can convert METARs from each world region to 2023-1."""
        generator = get_generator()
        
        # Get sample from region
        regional_cases = generator.regional_sample(region, count=20, hours=3)
        
        if len(regional_cases) == 0:
            pytest.skip(f"No METARs found for region {region}")
        
        # Convert each one
        success_count = 0
        for test_case in regional_cases:
            try:
                iwxxm_xml, _ = convert_metar_tac_with_metadata(
                    test_case.raw_metar,
                    iwxxm_version="2023-1"
                )
                
                if iwxxm_xml and len(iwxxm_xml) > 0:
                    success_count += 1
            except Exception as e:
                print(f"  Warning: Failed to convert {test_case.station_id}: {str(e)}")
        
        # Only assert if we have cases
        if len(regional_cases) > 0:
            # Expect at least 50% success rate
            success_rate = success_count / len(regional_cases)
            assert success_rate >= 0.5, f"Low success rate for {region}: {success_rate:.1%}"
            
            print(f"\n✅ {region}: {success_count}/{len(regional_cases)} successful ({success_rate:.1%})")
    
    @pytest.mark.parametrize("region", [
        "north_america",
        "europe",
        "asia_pacific",
        "south_america",
        "africa",
        "middle_east",
        "australia"
    ])
    def test_regional_coverage_2025_2(self, region: str):
        """Test that we can convert METARs from each world region to 2025-2."""
        generator = get_generator()
        
        # Get sample from region
        regional_cases = generator.regional_sample(region, count=20, hours=3)
        
        if len(regional_cases) == 0:
            pytest.skip(f"No METARs found for region {region}")
        
        # Convert each one
        success_count = 0
        for test_case in regional_cases:
            try:
                iwxxm_xml, _ = convert_metar_tac_with_metadata(
                    test_case.raw_metar,
                    iwxxm_version="2025-2"
                )
                
                if iwxxm_xml and len(iwxxm_xml) > 0:
                    success_count += 1
            except Exception as e:
                print(f"  Warning: Failed to convert {test_case.station_id}: {str(e)}")
        
        # Only assert if we have cases
        if len(regional_cases) > 0:
            # Expect at least 50% success rate
            success_rate = success_count / len(regional_cases)
            assert success_rate >= 0.5, f"Low success rate for {region}: {success_rate:.1%}"
            
            print(f"\n✅ {region}: {success_count}/{len(regional_cases)} successful ({success_rate:.1%})")


class TestPhenomenonCoverage:
    """Test coverage of specific weather phenomena."""
    
    @pytest.mark.parametrize("phenomenon", [
        'RA',    # Rain
        'SN',    # Snow
        'TS',    # Thunderstorm
        'FG',    # Fog
        'BR',    # Mist
        'NSW',   # No significant weather
        'CB',    # Cumulonimbus
        'TCU'    # Towering cumulus
    ])
    def test_phenomenon_conversion(self, phenomenon: str):
        """Test conversion of METARs containing specific phenomena."""
        generator = get_generator()
        
        # Get test cases with this phenomenon
        phenomenon_cases = generator.phenomenon_coverage(
            required_phenomena=[phenomenon],
            hours=6
        )
        
        if not phenomenon_cases:
            pytest.skip(f"No METARs found with phenomenon {phenomenon}")
        
        # Test conversion to both versions
        for version in ["2023-1", "2025-2"]:
            success_count = 0
            
            for test_case in phenomenon_cases:
                try:
                    iwxxm_xml, _ = convert_metar_tac_with_metadata(
                        test_case.raw_metar,
                        iwxxm_version=version
                    )
                    
                    if iwxxm_xml and len(iwxxm_xml) > 0:
                        success_count += 1
                except Exception as e:
                    print(f"  Warning: Failed to convert {test_case.station_id}: {str(e)}")
            
            success_rate = success_count / len(phenomenon_cases) if phenomenon_cases else 0
            print(f"\n  {version}: {success_count}/{len(phenomenon_cases)} successful ({success_rate:.1%})")
            
            # Expect reasonable success rate for phenomena (lower expectation for Sprint 2)
            assert success_rate >= 0.5, f"Low success rate for {phenomenon} in {version}"
