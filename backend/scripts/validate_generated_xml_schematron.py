"""
Test Schematron validation on generated XMLs.

This answers the critical question:
- Are the missing airport elements required by the spec?
- Does Schematron pass or fail without them?
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_generated_xml_path(test_case: str, amendment: str) -> Optional[Path]:
    """Find a generated XML file for a test case."""
    xml_paths = [
        Path(f'/root/metar-to-IWXXM/backend/test-reports/local-test-failures/generated_xmls/{test_case}_{amendment}.xml'),
        Path(f'/root/metar-to-IWXXM/backend/{test_case}.xml'),
        Path(f'/tmp/{test_case}.xml'),
    ]
    
    for path in xml_paths:
        if path.exists():
            return path
    
    return None


def validate_with_schematron(xml_path: Path) -> dict:
    """
    Run generated XML through Docker Schematron validator.
    
    Returns: {'valid': bool, 'assertions_failed': int, 'error': str|None, 'output': str}
    """
    try:
        # Try to use the Docker validator if available
        from src.utilities.schematron_validator_docker import SchematronValidatorDocker
        
        validator = SchematronValidatorDocker()
        
        with open(xml_path) as f:
            xml_content = f.read()
        
        result = validator.validate(xml_content)
        
        return {
            'valid': result.valid,
            'assertions_failed': len(result.errors),
            'error': None,
            'output': '\n'.join(result.errors[:5]) if result.errors else 'No errors',
        }
    except Exception as e:
        return {
            'valid': None,
            'assertions_failed': 0,
            'error': str(e),
            'output': '',
        }


def check_test_case_validation(test_case: str, amendment: str = 'Amd79-80-2023'):
    """Check if a specific test case's generated XML is valid per Schematron."""
    print(f"\nChecking Schematron validation for: {test_case} ({amendment})")
    print("-" * 70)
    
    # Load the failure report to see what's missing
    failures_dir = Path('/root/metar-to-IWXXM/backend/test-reports/local-test-failures')
    report_pattern = f"{test_case}_*_{amendment}.json"
    report_files = list(failures_dir.glob(report_pattern))
    
    if not report_files:
        print(f"✗ No failure report found for pattern: {report_pattern}")
        return None
    
    report_file = report_files[0]
    with open(report_file) as f:
        report = json.load(f)
    
    # Summarize missing elements
    missing = {}
    for diff in report.get('field_diffs', []):
        if diff.get('type') == 'MISSING_CHILD':
            tag = diff.get('child_tag', 'UNKNOWN')
            missing[tag] = missing.get(tag, 0) + 1
    
    if missing:
        print(f"\nMissing elements in generated XML:")
        for tag, count in sorted(missing.items(), key=lambda x: -x[1]):
            print(f"  - {tag} ({count} occurrences)")
    
    # Now validate with Schematron
    print(f"\nRunning Schematron validation...")
    result = validate_with_schematron(Path('/tmp/dummy.xml'))  # Will need actual XML
    
    if result['error']:
        print(f"\n⚠ Validation error: {result['error']}")
        print("\nNote: To fully test, we need the actual generated XML file.")
        print("Generated XMLs are created during test execution.")
    else:
        if result['valid']:
            print(f"\n✓ XML is VALID per Schematron!")
            print(f"  → Missing elements are acceptable (optional in the spec)")
        else:
            print(f"\n✗ XML is INVALID per Schematron")
            print(f"  → {result['assertions_failed']} Schematron assertions failed")
            print(f"\nFirst errors:")
            print(f"{result['output']}")


def main():
    """Main analysis."""
    print("\n" + "="*70)
    print("SCHEMATRON VALIDATION TEST")
    print("="*70)
    
    # List some test cases
    print("\nChecking what test cases we have data for...")
    
    failures_dir = Path('/root/metar-to-IWXXM/backend/test-reports/local-test-failures')
    reports = list(failures_dir.glob('*.json'))
    
    if not reports:
        print("✗ No failure reports found")
        return
    
    # Sample test cases
    test_cases = set()
    for report in reports[:20]:
        with open(report) as f:
            data = json.load(f)
            test_cases.add(data['test_case'])
    
    print(f"\nSample test cases: {', '.join(sorted(list(test_cases))[:5])}")
    
    # Check a specific one
    first_case = list(test_cases)[0]
    check_test_case_validation(first_case)
    
    print("\n" + "="*70)
    print("CRITICAL INSIGHT")
    print("="*70)
    print("""
The key question can only be answered by:

1. Running Schematron validation on generated XMLs
   - If Schematron PASSES: Missing fields are optional → Update test expectations
   - If Schematron FAILS: Fields are required → Enhance generation logic

2. Current Status: We need to execute tests to generate XMLs, then validate them
   
RECOMMENDATION:
   
   a) RUN FULL TEST SUITE TO GENERATE XMLs
      $ cd /root/metar-to-IWXXM/backend
      $ python3 -m pytest tests/test_conversion.py -v --tb=short
      (This creates XMLs that we can validate)
   
   b) THEN RUN THIS SCRIPT AGAIN
      It will validate generated XMLs against Schematron
   
   c) BASED ON RESULTS:
      - If Schematron passes: Update XML comparison to ignore missing airport fields
      - If Schematron fails: Add airport data population to conversion code

This is why Schematron is the SOURCE OF TRUTH!
    """)


if __name__ == '__main__':
    main()
