"""
Deep-dive analysis of airport element generation issue.

Investigates why AirportHeliport elements are missing required attributes.
"""

import json
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List


def analyze_missing_children():
    """Analyze the pattern of missing children across all tests."""
    failures_dir = Path('/root/metar-to-IWXXM/backend/test-reports/local-test-failures')
    
    missing_children = Counter()
    missing_by_amendment = {}
    
    for json_file in failures_dir.glob('*.json'):
        with open(json_file) as f:
            data = json.load(f)
            amendment = data['amendment_version']
            
            if amendment not in missing_by_amendment:
                missing_by_amendment[amendment] = Counter()
            
            for diff in data.get('field_diffs', []):
                if diff.get('type') == 'MISSING_CHILD':
                    tag = diff.get('child_tag', 'UNKNOWN')
                    missing_children[tag] += 1
                    missing_by_amendment[amendment][tag] += 1
    
    print("\n" + "="*70)
    print("MISSING CHILD ELEMENTS ANALYSIS")
    print("="*70)
    
    print("\nMost Commonly Missing Elements (across all tests):")
    print("-"*70)
    for tag, count in missing_children.most_common(10):
        total_tests = len(list(failures_dir.glob('*.json')))
        pct = 100 * count // (total_tests * 3)  # Rough percentage
        print(f"  {tag:30} {count:4} occurrences")
    
    print("\n\nMissing Elements by Amendment:")
    print("-"*70)
    for amendment in sorted(missing_by_amendment.keys()):
        print(f"\n{amendment}:")
        for tag, count in missing_by_amendment[amendment].most_common():
            print(f"  {tag:30} {count:4} occurrences")


def check_reference_data():
    """Check what airport data is available in iwxxm-translation."""
    ref_dir = Path('/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar')
    airport_csv = Path('/root/metar-to-IWXXM/data/af-airports.csv')
    
    print("\n" + "="*70)
    print("REFERENCE DATA AVAILABILITY")
    print("="*70)
    
    # Check airport CSV
    if airport_csv.exists():
        with open(airport_csv) as f:
            lines = f.readlines()
        print(f"\n✓ Airport data file exists: {airport_csv.name}")
        print(f"  Contains {len(lines)-1} airport records")
        print(f"  Columns: {lines[0].strip().split(',')[:5]}...")
    else:
        print(f"\n✗ Airport data file not found: {airport_csv}")
    
    # Check IWXXM reference XMLs
    if ref_dir.exists():
        xml_files = list(ref_dir.glob('*.xml'))
        print(f"\n✓ Reference IWXXM XMLs available: {len(xml_files)} files")
        
        # Check one for airport structure
        sample_xml = ref_dir / 'BGBW-282350Z.xml'
        if sample_xml.exists():
            with open(sample_xml) as f:
                content = f.read()
            
            # Count airport elements
            airport_blocks = len(re.findall(r'<iwxxm:AirportHeliport>', content))
            location_ident = len(re.findall(r'<iwxxm:locationIndicatorICAO>', content))
            arp_blocks = len(re.findall(r'<iwxxm:ARP>', content))
            
            print(f"\nSample: {sample_xml.name}")
            print(f"  AirportHeliport elements: {airport_blocks}")
            print(f"  locationIndicatorICAO elements: {location_ident}")
            print(f"  ARP (Aerodrome Reference Point): {arp_blocks}")


def understand_issue():
    """Explain the core issue."""
    print("\n" + "="*70)
    print("ROOT CAUSE ANALYSIS")
    print("="*70)
    
    print("""
The test failures show a consistent pattern:

ISSUE: AirportHeliportTimeSlice elements are missing required/optional children
  - Expected: 6 children (name, locationIndicatorICAO, designatorIATA, ARP, etc.)
  - Actual: 3 children (only some minimal set)

LIKELY CAUSES:

1. INCOMPLETE IMPLEMENTATION
   - The conversion code may only generate minimal airport data
   - Missing logic to populate: name, IATA code, ARP (lat/lon), etc.
   - These fields may require additional data sources

2. DATA SOURCE LIMITATIONS
   - METAR reports may not include detailed airport metadata
   - METAR only has ICAO code and runway info
   - Full airport details (IATA, ARP) require an airport database

3. OPTIONAL vs REQUIRED
   - Some missing elements may be optional in certain schemas
   - Schematron validation will clarify which MUST be present

NEXT STEPS:

1. Review iwxxm-translation reference XMLs for expected structure
   - See what fields are populated in reference
   - Understand if ALL are required or some are optional

2. Run Schematron validation on your generated XMLs
   - Schematron is the authoritative source
   - If Schematron passes, structure is spec-compliant
   - If it fails, Schematron will show which elements are truly required

3. Check data availability:
   - Airport CSV has metadata - can we use it to backfill missing fields?
   - Are IATA codes and ARP coordinates in the database?
   - Should we add logic to look up airport data?

4. Update comparison logic:
   - Don't use structural matching as test criteria
   - Use Schematron validation as the test
   - Only fail if Schematron validation fails
    """)


if __name__ == '__main__':
    analyze_missing_children()
    check_reference_data()
    understand_issue()
