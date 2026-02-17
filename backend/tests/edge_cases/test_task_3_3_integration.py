"""Integration tests for Task 3.3: Visibility-Weather Consistency.

Tests enhanced visibility-weather validation against real METAR test data.
"""

import pytest
import re
from src.testing.metar_test_generator import METARTestGenerator
from src.validation.semantic_rules import (
    VisibilityWeatherValidationRule,
    IssueSeverity,
)


@pytest.fixture(scope="session")
def test_cases():
    """Generate test cases from live API data."""
    generator = METARTestGenerator()
    print(f"\n🔄 Generating test cases for Task 3.3...")
    
    test_cases = generator.diverse_sample(count=50, hours=3, use_cache=True)
    
    if not test_cases:
        pytest.skip("Unable to generate test cases")
    
    return test_cases


def parse_visibility_and_phenomena(raw_metar: str):
    """Extract visibility and weather phenomena from METAR.
    
    Visibility patterns:
    - 10SM (10 statute miles)
    - 9999 (meters)
    - 5000 (meters)
    - M0400 (less than 400m)
    
    Phenomena patterns: FG, RA, SN, TS, BR, HZ, DZ, etc.
    """
    # Extract visibility
    vis_meters = None
    
    # Try statute miles first (ends with SM)
    sm_match = re.search(r'(\d+)SM', raw_metar)
    if sm_match:
        sm = int(sm_match.group(1))
        vis_meters = round(sm * 1609.34)  # Convert miles to meters
    else:
        # Try meters (4-digit number)
        # More than 9000m reported as CAVOK
        m_match = re.search(r'(?<![0-9])(\d{3,4})(?![0-9])', raw_metar)
        if m_match:
            vis_str = m_match.group(1)
            if len(vis_str) == 4:
                vis_meters = int(vis_str)
            elif len(vis_str) == 3:
                # 3 digits might be in hundreds of meters
                pass
    
    # Extract weather phenomena
    phenomena_pattern = r'(VC|RE|DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)'
    phenomena = re.findall(phenomena_pattern, raw_metar)
    
    return vis_meters, phenomena


class TestVisibilityWeatherIntegration:
    """Integration tests with real METAR data."""
    
    @pytest.fixture
    def rule(self):
        """Provide visibility-weather validation rule."""
        return VisibilityWeatherValidationRule()
    
    def test_visibility_weather_from_real_metars(self, rule, test_cases):
        """Validate visibility-weather consistency from real METARs.
        
        Expected: Real METARs should have consistent visibility and phenomena.
        """
        checked = 0
        valid = 0
        issues_found = 0
        no_data = 0
        
        for case in test_cases:
            vis, phenomena = parse_visibility_and_phenomena(case.raw_metar)
            
            if not vis or not phenomena:
                no_data += 1
                continue
            
            checked += 1
            
            # Validate
            validation_issues = rule.validate(
                visibility_meters=vis,
                weather_phenomena=phenomena
            )
            
            has_error = any(i.severity == IssueSeverity.ERROR for i in validation_issues)
            has_issue = len(validation_issues) > 0
            
            if not has_error:
                valid += 1
            
            if has_issue:
                issues_found += 1
        
        # Report results
        print(f"\n\n{'='*70}")
        print(f"Visibility-Weather Validation Results (Task 3.3)")
        print(f"{'='*70}")
        print(f"Total test cases: {len(test_cases)}")
        print(f"Cases with visibility & phenomena: {checked}")
        print(f"Valid combinations: {valid}")
        print(f"Cases with issues: {issues_found}")
        print(f"No visibility/phenomena data: {no_data}")
        
        if checked > 0:
            success_rate = valid / checked * 100
            print(f"Success rate: {success_rate:.1f}%")
        print(f"{'='*70}\n")
        
        # Expect at least 85% pass rate (real data may have edge cases)
        if checked > 0:
            assert (valid / checked) >= 0.85, \
                f"Too many invalid combinations: {issues_found}/{checked}"
    
    def test_phenomena_distribution(self, rule, test_cases):
        """Analyze weather phenomena distribution in test data."""
        phenomenon_counts = {}
        visibility_by_phenomenon = {}
        
        for case in test_cases:
            vis, phenomena = parse_visibility_and_phenomena(case.raw_metar)
            
            if not phenomena:
                continue
            
            for p in phenomena:
                phenomenon_counts[p] = phenomenon_counts.get(p, 0) + 1
                
                if p not in visibility_by_phenomenon:
                    visibility_by_phenomenon[p] = []
                
                if vis:
                    visibility_by_phenomenon[p].append(vis)
        
        if not phenomenon_counts:
            pytest.skip("No weather phenomena in test data")
        
        # Report statistics
        print(f"\n\n{'='*70}")
        print(f"Weather Phenomena Distribution (Task 3.3)")
        print(f"{'='*70}")
        print(f"Total phenomena found: {len(phenomenon_counts)}")
        print(f"\nPhenomena frequencies:")
        
        for p in sorted(phenomenon_counts.keys()):
            count = phenomenon_counts[p]
            pct = count / sum(phenomenon_counts.values()) * 100
            
            # Calculate visibility stats for this phenomenon
            if p in visibility_by_phenomenon and visibility_by_phenomenon[p]:
                vis_list = visibility_by_phenomenon[p]
                min_vis = min(vis_list)
                max_vis = max(vis_list)
                avg_vis = sum(vis_list) / len(vis_list)
                print(f"  {p}: {count} ({pct:.1f}%) - "
                      f"vis range: {min_vis}-{max_vis}m (avg {avg_vis:.0f}m)")
            else:
                print(f"  {p}: {count} ({pct:.1f}%)")
        
        print(f"{'='*70}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
