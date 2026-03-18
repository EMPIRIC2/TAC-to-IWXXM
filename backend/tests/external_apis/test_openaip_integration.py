#!/usr/bin/env python3
"""
Test and initialize OpenAIP integration.

This script validates that the OpenAIP service and related components
can be imported and initialized correctly.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir / "src"))

def test_imports():
    """Test that all new modules can be imported."""
    print("\n=== Testing Imports ===")

    # Test OpenAIPService import
    from services.openaip_service import OpenAIPService
    print("✓ OpenAIPService imported OK")
    assert OpenAIPService is not None

    # Test AirportRecordBuilder import
    from utilities.airport_record_builder import AirportRecordBuilder
    print("✓ AirportRecordBuilder imported OK")
    assert AirportRecordBuilder is not None

    # Test GiftsLocationDBAdapter import
    from utilities.gifts_locationdb_adapter import GiftsLocationDBAdapter
    print("✓ GiftsLocationDBAdapter imported OK")
    assert GiftsLocationDBAdapter is not None


def test_openaip_service():
    """Test OpenAIP service initialization and basic operations."""
    print("\n=== Testing OpenAIP Service ===")

    from services.openaip_service import OpenAIPService

    service = OpenAIPService()
    print("✓ OpenAIPService initialized")
    assert service is not None

    # Check cache status
    if service._cache:
        count = len(service._cache)
        print(f"✓ Cache loaded with {count} airports")
        assert count > 0, "Cache should contain airports"
    else:
        print("⚠ Cache is empty - may need initialization")

    # Test looking up a known airport
    enfb = service.get_airport("ENFB")
    if enfb:
        print(f"✓ Found ENFB: {enfb.get('name', 'Unknown')}")
    else:
        print("⚠ ENFB not found in cache (expected until cache is initialized)")


def test_airport_record_builder():
    """Test airport record builder."""
    print("\n=== Testing Airport Record Builder ===")

    from services.openaip_service import OpenAIPService
    from utilities.airport_record_builder import AirportRecordBuilder

    builder = AirportRecordBuilder()
    service = OpenAIPService()

    assert builder is not None
    assert service is not None

    # Test building a record for ENFB from vertical_datum_map
    enfb_record = builder.build_record("ENFB", openaip_data=service.get_airport("ENFB"))

    print("✓ Built record for ENFB")
    print(f"  - Name: {enfb_record.get('name')}")
    print(f"  - IATA: {enfb_record.get('iata')}")
    print(f"  - Status: {enfb_record.get('status')}")
    print(f"  - Source: {enfb_record.get('source')}")

    assert enfb_record is not None

    # Test GIFTs format
    gifts_str = builder.get_gifts_format(enfb_record)
    if gifts_str:
        print(f"✓ Generated GIFTs format: {gifts_str[:60]}...")
    else:
        print("⚠ Could not generate GIFTs format (missing required fields)")


def test_gifts_adapter():
    """Test GIFTs LocationDB adapter."""
    print("\n=== Testing GIFTs LocationDB Adapter ===")

    from utilities.gifts_locationdb_adapter import GiftsLocationDBAdapter

    adapter = GiftsLocationDBAdapter()
    print("✓ GiftsLocationDBAdapter initialized")
    assert adapter is not None

    # Test getting airport data
    enfb_data = adapter.get("ENFB")
    if enfb_data:
        print(f"✓ Retrieved ENFB data: {enfb_data[:60]}...")
    else:
        print("⚠ ENFB data not found")

    # Test validation
    is_valid = adapter.validate_airport("ENFB")
    print(f"✓ Validation check: ENFB valid = {is_valid}")
    assert isinstance(is_valid, bool)


def main():
    """Run all tests."""
    print("=" * 60)
    print("OpenAIP Integration Test Suite")
    print("=" * 60)

    results = {
        "Imports": test_imports(),
        "OpenAIP Service": test_openaip_service(),
        "Airport Record Builder": test_airport_record_builder(),
        "GIFTs Adapter": test_gifts_adapter(),
    }

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All tests passed!")
        print("\nNext steps:")
        print("1. Initialize OpenAIP cache: python3 backend/scripts/fetch_openaip_airports.py")
        print("2. Run conversion tests: cd backend && python3 -m pytest tests/test_metar_pairs_comprehensive.py -xvs")
        return 0
    else:
        print("\n✗ Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
