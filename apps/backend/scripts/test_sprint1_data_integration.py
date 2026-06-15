"""Test script for Sprint 1: Data Integration components.

Tests:
1. AviationWeather client enhancements (bbox queries, random sampling, caching)
2. OpenAIP client (airport metadata fetching)
3. WMO codelists client (weather phenomenon validation)
4. Airport reconciliation service (multi-source data merging)
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.clients.aviation_weather_client import (
    AviationWeatherClient,
    CachedAviationWeatherClient
)
from src.clients.openaip_client import OpenAIPClient
from src.clients.wmo_codelists_client import WMOCodelistsClient
from src.services.airport_reconciliation import AirportReconciliationService


def test_aviation_weather_enhancements():
    """Test AviationWeather client enhancements."""
    print("\n" + "="*70)
    print("TEST 1: AviationWeather Client Enhancements")
    print("="*70)
    
    client = AviationWeatherClient()
    
    # Test 1.1: Bbox query (Washington DC area)
    print("\n1.1. Testing bbox query (Washington DC area)...")
    dc_bbox = (-77.5, 38.5, -76.5, 39.5)  # (min_lon, min_lat, max_lon, max_lat)
    
    try:
        metars = client.fetch_metars_by_bbox_sync(dc_bbox, hours=3, format_type='json')
        print(f"   ✓ Fetched {len(metars)} METARs from DC area")
        
        if metars:
            sample = metars[0]
            print(f"   ✓ Sample: {sample['station_id']} - {sample.get('raw_text', 'N/A')[:50]}...")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 1.2: Random sampling
    print("\n1.2. Testing random sampling (50 METARs from 5 regions)...")
    
    try:
        sample_metars = client.fetch_random_sample_sync(count=50, hours=3)
        print(f"   ✓ Fetched {len(sample_metars)} random METARs")
        
        # Count by region (simplified - based on longitude)
        regions = {"NA": 0, "Europe": 0, "Asia": 0, "Other": 0}
        for metar in sample_metars:
            lon = metar.get('longitude', 0)
            if -130 <= lon <= -60:
                regions["NA"] += 1
            elif -10 <= lon <= 40:
                regions["Europe"] += 1
            elif 100 <= lon <= 150:
                regions["Asia"] += 1
            else:
                regions["Other"] += 1
        
        print(f"   ✓ Distribution: {regions}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 1.3: Caching
    print("\n1.3. Testing caching...")
    
    try:
        cached_client = CachedAviationWeatherClient()
        
        # First fetch (should hit API)
        metars1 = cached_client.fetch_metars_by_bbox_sync(dc_bbox, hours=3)
        print(f"   ✓ First fetch: {len(metars1)} METARs")
        
        # Second fetch (should hit cache)
        metars2 = cached_client.fetch_metars_by_bbox_sync(dc_bbox, hours=3)
        print(f"   ✓ Second fetch (cached): {len(metars2)} METARs")
        
        if len(metars1) == len(metars2):
            print(f"   ✓ Cache working correctly")
        else:
            print(f"   ! Cache may not be working (different sizes)")
            
    except Exception as e:
        print(f"   ✗ Failed: {e}")


def test_openaip_client():
    """Test OpenAIP client."""
    print("\n" + "="*70)
    print("TEST 2: OpenAIP Client")
    print("="*70)
    
    # Use correct data path
    data_path = backend_dir.parent / "data" / "open-aip"
    client = OpenAIPClient(data_path=data_path)
    
    # Test 2.1: Statistics
    print("\n2.1. Testing OpenAIP statistics...")
    try:
        stats = client.get_statistics()
        print(f"   ✓ Airports loaded: {stats['total_airports']}")
        print(f"   ✓ Countries: {stats['countries']}")
        print(f"   ✓ With elevation: {stats['with_elevation']}")
        print(f"   ✓ With coordinates: {stats['with_coordinates']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 2.2: Get specific airports
    print("\n2.2. Testing specific airport lookup...")
    test_icaos = ['KDCA', 'KJFK', 'KLAX', 'LFPG', 'EGLL']
    
    for icao in test_icaos:
        try:
            airport = client.get_airport_by_icao(icao)
            if airport:
                print(f"   ✓ {icao}: {airport.name} ({airport.country}), "
                      f"Elev: {airport.elevation:.0f}m, Coords: {airport.lat_lon}")
            else:
                print(f"   ! {icao}: Not found in OpenAIP data")
        except Exception as e:
            print(f"   ✗ {icao}: Failed - {e}")
    
    # Test 2.3: Search by country
    print("\n2.3. Testing country search...")
    try:
        us_airports = client.search_airports(country='US', limit=10)
        print(f"   ✓ Found {len(us_airports)} US airports (limited to 10)")
        if us_airports:
            print(f"   ✓ Sample: {us_airports[0].icao_code} - {us_airports[0].name}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")


def test_wmo_codelists_client():
    """Test WMO codelists client."""
    print("\n" + "="*70)
    print("TEST 3: WMO Codelists Client")
    print("="*70)
    
    # Find IWXXM codelists directory
    schemas_dir = backend_dir.parent / "schemas" / "iwxxm" / "IWXXM"
    codelists_dirs = list(schemas_dir.glob("*/rule"))
    
    if not codelists_dirs:
        print("   ! No IWXXM codelists directory found")
        return
    
    # Use latest version directory
    codelists_dir = sorted(codelists_dirs)[-1]
    print(f"\n   Using codelists from: {codelists_dir}")
    
    try:
        client = WMOCodelistsClient(codelists_dir)
        
        # Test 3.1: Statistics
        print("\n3.1. Testing codelist statistics...")
        stats = client.get_statistics()
        print(f"   ✓ Local codelists: {stats['local_codelists']}")
        print(f"   ✓ Cached codelists: {stats['cached_codelists']}")
        print(f"   ✓ Online enabled: {stats['online_enabled']}")
        
        # Test 3.2: List available codelists
        print("\n3.2. Testing available codelists...")
        codelists = client.list_available_codelists()
        print(f"   ✓ Available codelists: {len(codelists)}")
        if codelists:
            print(f"   ✓ Sample: {', '.join(codelists[:5])}")
        
        # Test 3.3: Validate weather phenomena
        print("\n3.3. Testing weather phenomenon validation...")
        test_weather = [
            ('TSRA', True),  # Thunderstorm with rain
            ('NSW', True),   # No significant weather
            ('RA', True),    # Rain
            ('INVALID', False)  # Should fail
        ]
        
        for code, expected in test_weather:
            result = client.validate_weather_phenomenon(code)
            status = "✓" if result == expected else "✗"
            print(f"   {status} '{code}': {result}")
        
        # Test 3.4: Validate cloud amounts
        print("\n3.4. Testing cloud amount validation...")
        test_clouds = [
            ('FEW', True),
            ('SCT', True),
            ('BKN', True),
            ('OVC', True),
            ('INVALID', False)
        ]
        
        for code, expected in test_clouds:
            result = client.validate_cloud_amount(code)
            status = "✓" if result == expected else "✗"
            print(f"   {status} '{code}': {result}")
            
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()


def test_airport_reconciliation():
    """Test airport reconciliation service."""
    print("\n" + "="*70)
    print("TEST 4: Airport Reconciliation Service")
    print("="*70)
    
    try:
        # Use correct data paths
        openaip_client = OpenAIPClient(data_path=backend_dir.parent / "data" / "open-aip")
        aviation_weather_client = AviationWeatherClient()
        gifts_data_path = backend_dir.parent / "data" / "af-airports.csv"
        
        service = AirportReconciliationService(
            openaip_client=openaip_client,
            aviation_weather_client=aviation_weather_client,
            gifts_data_path=gifts_data_path
        )
        
        # Test 4.1: Reconcile major airports
        print("\n4.1. Testing airport reconciliation...")
        test_icaos = ['KDCA', 'KJFK', 'KLAX', 'LFPG', 'EGLL']
        
        for icao in test_icaos:
            reconciled = service.get_airport(icao)
            if reconciled:
                print(f"\n   ✓ {icao}: {reconciled.name}")
                print(f"      Sources: {', '.join(reconciled.sources)}")
                print(f"      Primary: {reconciled.primary_source}")
                print(f"      Coords: ({reconciled.latitude:.4f}, {reconciled.longitude:.4f}) "
                      f"[confidence: {reconciled.coordinate_confidence:.2f}]")
                print(f"      Elevation: {reconciled.elevation:.0f}m "
                      f"[confidence: {reconciled.elevation_confidence:.2f}]")
                
                if reconciled.has_conflicts():
                    print(f"      ⚠ {len(reconciled.conflicts)} conflicts detected:")
                    for conflict in reconciled.conflicts:
                        print(f"        - {conflict.field}: {conflict.winner}={conflict.resolution}")
            else:
                print(f"   ! {icao}: No data found")
        
        # Test 4.2: Statistics
        print("\n4.2. Testing reconciliation statistics...")
        stats = service.get_statistics()
        print(f"   ✓ Total queries: {stats['total_queries']}")
        print(f"   ✓ OpenAIP hits: {stats['openaip_hits']}")
        print(f"   ✓ GIFTs hits: {stats['gifts_hits']}")
        print(f"   ✓ Conflicts detected: {stats['conflicts_detected']}")
        print(f"   ✓ Conflict rate: {stats['conflict_rate']:.1%}")
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all Sprint 1 tests."""
    print("\n" + "#"*70)
    print("# SPRINT 1: Data Integration - Component Testing")
    print("#"*70)
    
    # Test each component
    test_aviation_weather_enhancements()
    test_openaip_client()
    test_wmo_codelists_client()
    test_airport_reconciliation()
    
    print("\n" + "#"*70)
    print("# Sprint 1 Testing Complete")
    print("#"*70 + "\n")


if __name__ == '__main__':
    main()
