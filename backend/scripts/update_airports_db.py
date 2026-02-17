#!/usr/bin/env python3
"""
Download and convert OurAirports global database to airports.json format.

Downloads comprehensive airport data from OurAirports.com and converts it
to the JSON format expected by the Airport validator.
"""

import csv
import json
import sys
from pathlib import Path
from urllib.request import urlretrieve
from typing import List, Dict, Any, Optional


def download_ourairports_data(output_path: Path) -> None:
    """Download airports.csv from OurAirports."""
    url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
    print(f"Downloading from {url}...")
    urlretrieve(url, output_path)
    print(f"Downloaded to {output_path}")


def convert_csv_to_json(csv_path: Path, json_path: Path) -> None:
    """Convert OurAirports CSV to airports.json format."""
    # Load vertical datum mapping
    datum_map_path = json_path.parent / "vertical_datum_map.json"
    datum_defaults = {}
    
    try:
        if datum_map_path.exists():
            with open(datum_map_path, 'r', encoding='utf-8') as f:
                datum_data = json.load(f)
                datum_defaults = datum_data.get("country_defaults", {})
            print(f"Loaded vertical datum mappings for {len(datum_defaults)} countries")
    except Exception as e:
        print(f"Warning: Could not load vertical datum mapping: {e}")
    
    airports = []
    skipped = 0
    
    print(f"Reading {csv_path}...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Skip airports without ICAO codes
            icao = row.get('icao_code', '').strip()
            if not icao or icao == '':
                skipped += 1
                continue
            
            # Build airport object
            airport: Dict[str, Any] = {
                'icao': icao,
                'name': row.get('name', '').strip(),
                'type': row.get('type', '').strip(),
            }
            
            # Add optional fields
            iata = row.get('iata_code', '').strip()
            if iata:
                airport['iata'] = iata
            
            city = row.get('municipality', '').strip()
            if city:
                airport['city'] = city
            
            # Country - try iso_country first, then fall back to continent
            country = row.get('iso_country', '').strip()
            if country:
                airport['country'] = country
            
            # Add coordinates if available
            try:
                lat = row.get('latitude_deg', '').strip()
                lon = row.get('longitude_deg', '').strip()
                elev = row.get('elevation_ft', '').strip()
                
                if lat and lon:
                    coords = {
                        'latitude': float(lat),
                        'longitude': float(lon),
                    }
                    if elev:
                        try:
                            coords['elevation_ft'] = int(float(elev))
                        except (ValueError, TypeError):
                            pass
                    
                    # Add vertical datum based on country
                    vertical_datum = "EGM_96"  # Default
                    if country and country in datum_defaults:
                        raw_datum = datum_defaults[country]
                        # Normalize to IWXXM format
                        # Supported natively: EGM_96, NAVD88, AHD
                        if raw_datum in ['EGM96', 'EGM_96']:
                            vertical_datum = "EGM_96"
                        elif raw_datum == 'NAVD88':
                            vertical_datum = "NAVD88"
                        elif raw_datum == 'AHD':
                            vertical_datum = "AHD"
                        else:
                            vertical_datum = f"OTHER:{raw_datum}"
                    coords['vertical_datum'] = vertical_datum
                    
                    airport['coordinates'] = coords
            except (ValueError, TypeError):
                pass
            
            airports.append(airport)
    
    print(f"Converted {len(airports)} airports (skipped {skipped} without ICAO codes)")
    
    # Write JSON
    print(f"Writing to {json_path}...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(airports, f, indent=2, ensure_ascii=False)

    
    print(f"✓ Successfully created {json_path}")
    print(f"  Total airports: {len(airports)}")


def verify_bgbw(json_path: Path) -> None:
    """Verify BGBW is in the database."""
    with open(json_path, 'r', encoding='utf-8') as f:
        airports = json.load(f)
    
    bgbw = None
    for airport in airports:
        if airport.get('icao') == 'BGBW':
            bgbw = airport
            break
    
    if bgbw:
        print("\n✓ BGBW found in database:")
        print(f"  Name: {bgbw.get('name')}")
        print(f"  IATA: {bgbw.get('iata')}")
        if 'coordinates' in bgbw:
            coords = bgbw['coordinates']
            print(f"  Coordinates: {coords.get('latitude')}, {coords.get('longitude')}")
            print(f"  Elevation: {coords.get('elevation_ft')} ft")
    else:
        print("\n✗ BGBW not found in database")


def main():
    """Main execution."""
    # Determine paths
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    data_dir = backend_dir / "src" / "data"
    
    csv_path = data_dir / "airports_download.csv"
    json_path = data_dir / "airports.json"
    backup_path = data_dir / "airports.json.backup"
    
    print("=" * 60)
    print("OurAirports Database Update")
    print("=" * 60)
    
    # Backup existing file
    if json_path.exists():
        print(f"\nBacking up existing file to {backup_path}")
        json_path.rename(backup_path)
    
    try:
        # Download
        download_ourairports_data(csv_path)
        
        # Convert
        convert_csv_to_json(csv_path, json_path)
        
        # Verify
        verify_bgbw(json_path)
        
        # Cleanup
        csv_path.unlink()
        print(f"\nCleaned up temporary file: {csv_path}")
        
        print("\n" + "=" * 60)
        print("✓ Update complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        # Restore backup on error
        if backup_path.exists() and not json_path.exists():
            print("Restoring backup...")
            backup_path.rename(json_path)
        sys.exit(1)


if __name__ == '__main__':
    main()
