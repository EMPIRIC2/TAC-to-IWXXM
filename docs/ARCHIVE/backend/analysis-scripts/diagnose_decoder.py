#!/usr/bin/env python3
"""
Diagnose what GIFTs metarDecoder returns for airport data.

This will help us understand:
1. What fields are in the decoded output?
2. Are airport lookups happening?
3. What data is missing?
"""

import sys
import pathlib  
import json
from pprint import pprint

# Add GIFTs to path
repo_root = pathlib.Path(__file__).resolve().parent.parent
gifts_dir = repo_root / "GIFTs"
if not gifts_dir.exists():
    gifts_dir = pathlib.Path("/app/GIFTs")

sys.path.insert(0, str(gifts_dir))

try:
    from gifts import metarDecoder
except Exception as e:
    print(f"✗ Failed to import metarDecoder: {e}")
    print(f"  Tried: {gifts_dir}")
    sys.exit(1)


def diagnose_sample_metar():
    """Decode a sample METAR and inspect the output."""
    print("="*70)
    print("METAR DECODER DIAGNOSTIC")
    print("="*70)
    
    # Sample METARs from our test cases
    test_cases = [
        "METAR BGBW 282350Z 24025KT 9999 BKN019 M03/M12 Q1023 NOSIG",  # BGBW
        "METAR EDDH 282350Z 24008KT 9999 BKN022 M02/M13 Q1028 NOSIG",  # Hamburg
    ]
    
    for metar_text in test_cases:
        print(f"\n{'─'*70}")
        print(f"Input METAR: {metar_text}")
        print(f"{'─'*70}")
        
        try:
            decoder = metarDecoder.Annex3()
            decoded = decoder(metar_text)
            
            print("\n✓ Decoding successful!")
            print(f"\nType of decoded: {type(decoded)}")
            print(f"\nAvailable attributes/methods:")
            
            if hasattr(decoded, '__dict__'):
                attrs = decoded.__dict__
                print(f"Instance attributes: {list(attrs.keys())}")
                
                # Check for airport-related fields
                airport_fields = ['name', 'iataID', 'position', 'str', 'aerodrome']
                print(f"\nAirport-related fields:")
                for field in airport_fields:
                    if field in attrs:
                        print(f"  ✓ {field}: {attrs[field]}")
                    else:
                        print(f"  ✗ {field}: NOT PRESENT")
                
                # Print first few fields as example
                print(f"\nFirst 10 fields:")
                for i, (k, v) in enumerate(list(attrs.items())[:10]):
                    print(f"  {k}: {v}")
            else:
                print(f"Dir: {[x for x in dir(decoded) if not x.startswith('_')][:20]}")
            
        except Exception as e:
            print(f"✗ Decoding failed: {e}")
            import traceback
            traceback.print_exc()


def check_gifts_config():
    """Check GIFTs configuration for airport lookups."""
    print("\n" + "="*70)
    print("GIFTS CONFIGURATION CHECK")
    print("="*70)
    
    try:
        from gifts.common import MetarConfig
        
        config = MetarConfig
        print(f"\n✓ MetarConfig imported")
        
        # Check for airport-related config
        airport_attrs = ['airport', 'aviation', 'metar', 'config', 'db']
        
        for attr in dir(config):
            if any(x in attr.lower() for x in ['airport', 'lookup', 'db', 'data', 'csv']):
                print(f"  Found: {attr}")
                try:
                    val = getattr(config, attr)
                    if not callable(val):
                        print(f"    Value: {val}")
                except:
                    pass
                    
    except Exception as e:
        print(f"✗ Failed to check MetarConfig: {e}")


def check_airport_data_file():
    """Check if airport CSV exists and is accessible."""
    print("\n" + "="*70)
    print("AIRPORT DATA FILE CHECK")
    print("="*70)
    
    airport_csv = pathlib.Path("/root/metar-to-IWXXM/data/af-airports.csv")
    
    if airport_csv.exists():
        print(f"\n✓ Airport CSV found: {airport_csv}")
        with open(airport_csv) as f:
            lines = f.readlines()
        print(f"  Records: {len(lines) - 1}")
        print(f"  Header: {lines[0].strip()[:80]}...")
        
        # Check if BGBW is in database
        bgbw_lines = [l for l in lines if 'BGBW' in l]
        if bgbw_lines:
            print(f"\n  BGBW found in database:")
            print(f"    {bgbw_lines[0][:90]}...")
    else:
        print(f"\n✗ Airport CSV NOT found: {airport_csv}")


def main():
    diagnose_sample_metar()
    check_gifts_config()
    check_airport_data_file()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
Based on this diagnostic:
1. If 'name' and 'iataID' are present in decoded → lookup IS working
2. If they're missing → lookup needs to be enabled or data source verified
3. Check if 'position' field has coordinates or if ARP needs to be built

The key question: Does the decoded object from metarDecoder
have the airport metadata fields populated?
    """)


if __name__ == '__main__':
    main()
