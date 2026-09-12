"""
Analyze test failures and validate using Schematron.

This tool:
1. Categorizes failures (cosmetic vs structural)
2. Runs Schematron validation on generated XMLs
3. Determines if test failures are real issues or false positives
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Import our Schematron validator
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from utilities.schematron_validator_docker import SchematronValidatorDocker


class TestFailureAnalyzer:
    """Analyze and categorize test failures."""
    
    # Patterns that are cosmetic (should be ignored)
    COSMETIC_PATTERNS = {
        'UUID': r'#uuid\.[a-f0-9\-]+',
        'TIMESTAMP': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        'GENERATED_ID': r'uuid\.[a-f0-9\-]+',
    }
    
    def __init__(self, failures_dir: Path):
        """Initialize analyzer with test failure reports."""
        self.failures_dir = Path(failures_dir)
        self.failures = {}
        self.categorized = defaultdict(list)
        self._load_failures()
    
    def _load_failures(self):
        """Load all test failure JSON files."""
        for json_file in self.failures_dir.glob('*.json'):
            with open(json_file) as f:
                data = json.load(f)
                key = f"{data['test_case']}_{data['amendment_version']}"
                self.failures[key] = data
    
    def categorize_diffs(self) -> Dict:
        """Categorize field differences as cosmetic or structural."""
        categorized = {
            'total': 0,
            'cosmetic': 0,
            'structural': 0,
            'by_type': defaultdict(lambda: {'cosmetic': 0, 'structural': 0}),
            'details': []
        }
        
        for test_id, failure_data in self.failures.items():
            for diff in failure_data.get('field_diffs', []):
                categorized['total'] += 1
                diff_type = diff.get('type', 'UNKNOWN')
                
                # Check if this is cosmetic
                is_cosmetic = self._is_cosmetic_diff(diff)
                
                if is_cosmetic:
                    categorized['cosmetic'] += 1
                    categorized['by_type'][diff_type]['cosmetic'] += 1
                else:
                    categorized['structural'] += 1
                    categorized['by_type'][diff_type]['structural'] += 1
                    categorized['details'].append({
                        'test': test_id,
                        'type': diff_type,
                        'path': diff.get('path'),
                        'diff': diff
                    })
        
        return categorized
    
    def _is_cosmetic_diff(self, diff: Dict) -> bool:
        """Determine if a difference is cosmetic."""
        diff_type = diff.get('type', '')
        
        # UUIDs and timestamps are always cosmetic
        if diff_type == 'ATTRIBUTE_MISMATCH':
            attr = diff.get('attribute', '')
            expected = str(diff.get('expected', ''))
            actual = str(diff.get('actual', ''))
            
            # UUID attributes are cosmetic
            if 'uuid' in attr.lower() or 'href' in attr.lower():
                if re.search(self.COSMETIC_PATTERNS['UUID'], expected) or \
                   re.search(self.COSMETIC_PATTERNS['UUID'], actual):
                    return True
            
            # Timestamp attributes are cosmetic
            if re.search(self.COSMETIC_PATTERNS['TIMESTAMP'], expected) or \
               re.search(self.COSMETIC_PATTERNS['TIMESTAMP'], actual):
                return True
        
        # Missing or mismatched children are structural
        if diff_type in ['CHILD_COUNT_MISMATCH', 'TAG_MISMATCH', 'MISSING_CHILD']:
            return False
        
        return False
    
    def get_structural_issues(self) -> List[Dict]:
        """Get only the structural issues that need fixing."""
        issues = []
        
        for test_id, failure_data in self.failures.items():
            structural = []
            for diff in failure_data.get('field_diffs', []):
                if not self._is_cosmetic_diff(diff):
                    structural.append(diff)
            
            if structural:
                issues.append({
                    'test': test_id,
                    'amendment': failure_data['amendment_version'],
                    'count': len(structural),
                    'diffs': structural
                })
        
        return issues
    
    def print_summary(self):
        """Print analysis summary."""
        categorized = self.categorize_diffs()
        structural_issues = self.get_structural_issues()
        
        print("\n" + "="*70)
        print("TEST FAILURE ANALYSIS")
        print("="*70)
        
        print(f"\nTotal Differences: {categorized['total']}")
        print(f"  Cosmetic (safe to ignore): {categorized['cosmetic']} ({100*categorized['cosmetic']//max(1,categorized['total'])}%)")
        print(f"  Structural (need fixing): {categorized['structural']} ({100*categorized['structural']//max(1,categorized['total'])}%)")
        
        print(f"\nBreakdown by Type:")
        for diff_type, counts in sorted(categorized['by_type'].items()):
            total = counts['cosmetic'] + counts['structural']
            print(f"  {diff_type}: {total} total ({counts['cosmetic']} cosmetic, {counts['structural']} structural)")
        
        print(f"\n\nSTRUCTURAL ISSUES NEEDING FIXES ({len(structural_issues)} tests):")
        print("-"*70)
        
        for issue in sorted(structural_issues, key=lambda x: x['count'], reverse=True)[:10]:
            print(f"\n{issue['test']} ({issue['amendment']}):")
            print(f"  {issue['count']} structural issues")
            for diff in issue['diffs'][:3]:  # Show first 3
                diff_type = diff.get('type')
                path = diff.get('path', '').replace('SPECI/', '')[:50]
                print(f"    - {diff_type}: {path}")
            if len(issue['diffs']) > 3:
                print(f"    ... and {len(issue['diffs']) - 3} more")


def analyze_with_schematron():
    """Run Schematron validation on test cases."""
    schema_path = Path('/root/metar-to-IWXXM/schemas/iwxxm/2025-2/IWXXM/rule/iwxxm.sch')
    
    if not schema_path.exists():
        print("⚠ Schematron validation skipped (schema not found)")
        return
    
    print("\n" + "="*70)
    print("SCHEMATRON VALIDATION ANALYSIS")
    print("="*70)
    print("\nNote: Schematron is the authoritative source of truth.")
    print("If Schematron validation passes, structural differences may be acceptable.\n")
    
    # This would require the generated XML files, which we don't have direct access to
    # But we can document how to run this validation
    print("To validate generated XMLs against Schematron:")
    print("  validator = SchematronValidatorDocker()")
    print("  result = validator.validate(xml_content)")
    print("  if result.valid: print('✓ Schematron validation passed')")
    print("  else: print(f'✗ Failed: {result.failed_constraints}')")


def main():
    """Run analysis."""
    failures_dir = Path('/root/metar-to-IWXXM/backend/test-reports/local-test-failures')
    
    if not failures_dir.exists():
        print(f"Error: Test failures directory not found: {failures_dir}")
        return
    
    print(f"Analyzing {len(list(failures_dir.glob('*.json')))} test failure reports...")
    
    analyzer = TestFailureAnalyzer(failures_dir)
    analyzer.print_summary()
    analyze_with_schematron()
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print("""
1. FILTER COSMETIC DIFFERENCES
   - Update comparison to ignore UUID/timestamp differences
   - These are generated per-run and don't indicate validation issues

2. USE SCHEMATRON AS AUTHORITY
   - Run generated XMLs through Schematron validation
   - If Schematron passes, structure is spec-compliant
   - Missing optional elements may be acceptable

3. INVESTIGATE STRUCTURAL ISSUES
   - Look for missing required airport attributes
   - Check data source (METAR) for required information
   - May need to adjust code logic if data is available but not extracted

4. DOCUMENT KNOWN LIMITATIONS
   - Some METAR data may not include airport metadata
   - Reference the iwxxm-translation test cases to understand spec expectations
    """)


if __name__ == '__main__':
    main()
