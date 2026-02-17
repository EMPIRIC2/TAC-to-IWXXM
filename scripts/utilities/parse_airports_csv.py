#!/usr/bin/env python3
"""
Parse af-airports.csv and generate airports.json for frontend and backend validation.

This script:
1. Reads data/af-airports.csv
2. Filters airports with valid ICAO codes (non-empty)
3. Transforms to a normalized JSON structure
4. Outputs to frontend/src/data/airports.json and backend/src/data/airports.json

Usage:
    python scripts/parse_airports_csv.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def parse_airports_csv(csv_path: Path) -> list[dict[str, Any]]:
    """
    Parse af-airports.csv and return filtered airport data.
    
    Args:
        csv_path: Path to af-airports.csv
        
    Returns:
        List of airport dictionaries with normalized structure
    """
    airports = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            icao_code = row.get('icao_code', '').strip()
            
            # Filter: only include airports with valid ICAO codes
            if not icao_code:
                continue
            
            # Extract and normalize data
            airport = {
                'icao': icao_code,
                'name': row.get('name', '').strip(),
                'city': row.get('municipality', '').strip(),
                'country': row.get('country_name', '').strip(),
                'type': row.get('type', '').strip(),
            }
            
            # Add optional IATA code if present
            iata_code = row.get('iata_code', '').strip()
            if iata_code:
                airport['iata'] = iata_code
            
            # Add coordinates if present
            try:
                lat = float(row.get('latitude_deg', ''))
                lon = float(row.get('longitude_deg', ''))
                elev = row.get('elevation_ft', '').strip()
                
                airport['coordinates'] = {
                    'latitude': lat,
                    'longitude': lon,
                }
                
                if elev:
                    try:
                        airport['coordinates']['elevation_ft'] = int(float(elev))
                    except (ValueError, TypeError):
                        pass
                        
            except (ValueError, TypeError):
                # Skip coordinates if not valid
                pass
            
            airports.append(airport)
    
    return airports


def write_json_output(airports: list[dict[str, Any]], output_path: Path) -> None:
    """
    Write airports data to JSON file.
    
    Args:
        airports: List of airport dictionaries
        output_path: Path to output JSON file
    """
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(airports, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Written {len(airports)} airports to {output_path}")


def main() -> None:
    """Main execution function."""
    # Determine project root (script is in scripts/ directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Input CSV path
    csv_path = project_root / 'data' / 'af-airports.csv'
    
    # Output JSON paths
    frontend_output = project_root / 'frontend' / 'src' / 'data' / 'airports.json'
    backend_output = project_root / 'backend' / 'src' / 'data' / 'airports.json'
    
    print(f"Reading airports from {csv_path}...")
    
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found!")
        return
    
    # Parse CSV
    airports = parse_airports_csv(csv_path)
    
    print(f"Parsed {len(airports)} airports with valid ICAO codes")
    
    # Write outputs
    write_json_output(airports, frontend_output)
    write_json_output(airports, backend_output)
    
    # Print statistics
    airports_with_iata = sum(1 for a in airports if 'iata' in a)
    airports_with_coords = sum(1 for a in airports if 'coordinates' in a)
    
    print(f"\nStatistics:")
    print(f"  Total airports: {len(airports)}")
    print(f"  With IATA codes: {airports_with_iata} ({airports_with_iata/len(airports)*100:.1f}%)")
    print(f"  With coordinates: {airports_with_coords} ({airports_with_coords/len(airports)*100:.1f}%)")
    
    # Show airport types distribution
    type_counts = {}
    for airport in airports:
        airport_type = airport.get('type', 'unknown')
        type_counts[airport_type] = type_counts.get(airport_type, 0) + 1
    
    print(f"\nAirport types:")
    for airport_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {airport_type}: {count}")


if __name__ == '__main__':
    main()
