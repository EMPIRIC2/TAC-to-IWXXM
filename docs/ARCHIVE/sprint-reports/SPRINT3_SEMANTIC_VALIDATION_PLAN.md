# Sprint 3: Semantic Validation Rules & Enhanced Testing

**Status**: 🎯 Planning Phase
**Current Date**: February 15, 2026
**Foundation**: Sprint 1 & 2 Complete (187+ test cases, 82 stations, 5 weather phenomena)

## Overview

Sprint 3 focuses on implementing **semantic validation rules** that verify meteorological consistency beyond XML schema compliance. This moves the system from basic IWXXM syntax validation to scientifically accurate weather data interpretation.

### Current State (End of Sprint 2)

```
✅ Test Data Available:
   - 187 diverse test cases
   - 82 unique stations across 9 countries
   - 5 weather phenomena types: BR, FZRA, HZ, RA, SN
   - 6 cloud amount types: BKN, CLR, FEW, OVC, SCT, SKC
   - Complexity distribution: 61% simple, 28% medium, 2% complex

✅ Infrastructure Ready:
   - METARTestGenerator with live API integration
   - 200+ parameterized pytest tests
   - Coverage tracking across regions/phenomena/stations
   - Caching for reproducible testing

❌ Gaps Identified:
   - No meteorological relationship validation
   - Hard-coded string comparisons (should be semantic)
   - Limited error analysis for conversion failures
   - No validation of cloud layer ordering
   - No temperature/dewpoint consistency checks
   - No visibility-based weather validation
```

## Sprint 3 Goals

### Primary: Semantic Validation Framework (Tasks 1-3)

Implement validation rules that check meteorological consistency:

```
Task 3.1: Temperature & Dewpoint Validation
├─ Rule: dewpoint ≤ temperature (always true)
├─ Alert: Temperature inversion errors
├─ Apply: All 187 test cases
└─ Success: 100% of real-world data passes

Task 3.2: Cloud Layer Ordering Validation
├─ Rule: Cloud bases increase with altitude (BKN before OVC)
├─ Rule: Coverage decreases or stays same up vertical column
├─ Apply: Test cases with multiple cloud layers
└─ Success: 95%+ of valid data passes

Task 3.3: Visibility-Weather Relationship Validation
├─ Rule: FG (fog) → visibility < 1000m
├─ Rule: BR (mist) → 1000m ≤ visibility ≤ 5000m
├─ Rule: RA (rain) → usually visibility 2000-5000m
├─ Apply: 62 test cases with weather phenomena
└─ Success: 90%+ of real-world cases align
```

### Secondary: Enhanced Error Reporting (Tasks 4-5)

```
Task 3.4: Detailed Failure Analysis
├─ Categorize failures:
│  ├─ Data source issues (API field mapping)
│  ├─ Conversion logic bugs
│  ├─ Schematron validation errors
│  ├─ Meteorological inconsistencies
│  └─ WMO codelist violations
├─ Report: JSON with categorization
└─ Success: 100% of failures categorized

Task 3.5: Extended Test Coverage
├─ Extend from 187 to 500+ test cases
├─ Target: All 10 phenomena (add TSRA, FG, CB, TCU)
├─ Expand: Geographic coverage (currently 4/7 regions)
├─ Improve: Complex case distribution (from 2% to 15%)
└─ Success: 500+ diverse cases with full phenomena coverage
```

## Detailed Specifications

### Task 3.1: Temperature & Dewpoint Validation

**Purpose**: Ensure basic thermodynamic consistency.

**Implementation**:

```python
# src/validation/semantic_rules.py (NEW)
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ValidationIssue:
    rule_name: str
    severity: str  # "error", "warning", "info"
    message: str
    expected: str
    actual: str
    affected_field: str

class TemperatureValidationRule:
    """Verify temperature ≥ dewpoint (always)."""
    
    def validate(self, temperature: float, dewpoint: float) -> Optional[ValidationIssue]:
        """
        Returns issue if dewpoint > temperature.
        
        Real-world physics: Dewpoint cannot exceed temperature.
        In METARs, this never happens with real data.
        """
        if temperature < dewpoint:
            return ValidationIssue(
                rule_name="temperature_dewpoint_inversion",
                severity="error",
                message=f"Temperature ({temperature}°C) < Dewpoint ({dewpoint}°C)",
                expected=f"Temperature ≥ Dewpoint",
                actual=f"T={temperature}°C, Td={dewpoint}°C",
                affected_field="temperature, dewpoint"
            )
        return None
    
    def get_suggested_fix(self, temperature: float, dewpoint: float) -> Optional[str]:
        """Suggest data correction."""
        if temperature < dewpoint:
            return f"Swap values: T={dewpoint}, Td={temperature}"
        return None
```

**Test Coverage**:
- ✅ All 187 test cases (real data from AviationWeather API)
- Expected: 100% pass (never fails in real METARs)
- Use to detect bad data sources

**Validation Output**:
```json
{
  "rule": "temperature_dewpoint_inversion",
  "test_case": "KDCA_20260215",
  "result": "passed",
  "temperature": 12.0,
  "dewpoint": 8.0,
  "details": "T=12°C, Td=8°C (healthy margin of 4°C)"
}
```

---

### Task 3.2: Cloud Layer Ordering Validation

**Purpose**: Verify cloud layers follow atmospheric physics.

**Key Rules**:

```
Rule 1: Cloud coverage non-increasing upward
        Bottom layer FEW/SCT → top layer must be FEW/SCT or same
        Example: ✓ BKN 1500 FT, OVC 5000 FT
        Example: ✗ OVC 1500 FT, FEW 5000 FT (impossible)

Rule 2: Cloud bases increase with altitude
        If Layer1 @1500ft and Layer2 @1200ft → flip them
        Example: ✓ BKN 800 FT, OVC 2000 FT
        Example: ✗ OVC 2000 FT, BKN 800 FT (bad order)

Rule 3: Clear sky rules
        CLR = no clouds at any height (mutually exclusive with others)
        SKC = sky clear code (non-standard, treat as CLR)
```

**Implementation**:

```python
class CloudLayerValidationRule:
    """Verify cloud layer ordering and consistency."""
    
    # Coverage hierarchy (lowest = most restrictive)
    COVERAGE_RANK = {"CLR": 0, "SKC": 0, "FEW": 1, "SCT": 2, "BKN": 3, "OVC": 4}
    
    def validate(self, cloud_layers: List[CloudLayer]) -> List[ValidationIssue]:
        """
        Validate cloud layer sequence.
        
        Args:
            cloud_layers: List of layers with (coverage, altitude) tuples
        
        Returns:
            List of issues found (empty if valid)
        """
        issues = []
        
        # Check clear sky exclusivity
        if any(layer.coverage in ["CLR", "SKC"] for layer in cloud_layers):
            if len(cloud_layers) > 1:
                issues.append(ValidationIssue(
                    rule_name="clear_sky_exclusivity",
                    severity="error",
                    message="CLR/SKC cannot coexist with other cloud layers",
                    affected_field="cloud_layers"
                ))
        
        # Check altitude ordering
        for i in range(len(cloud_layers) - 1):
            if cloud_layers[i].altitude >= cloud_layers[i+1].altitude:
                issues.append(ValidationIssue(
                    rule_name="cloud_altitude_ordering",
                    severity="warning",
                    message=f"Layer {i} altitude ({cloud_layers[i].altitude}m) " +
                           f"≥ Layer {i+1} ({cloud_layers[i+1].altitude}m)",
                    affected_field=f"cloud_layers[{i}:i+1]"
                ))
        
        # Check coverage non-increasing
        for i in range(len(cloud_layers) - 1):
            rank_i = self.COVERAGE_RANK[cloud_layers[i].coverage]
            rank_next = self.COVERAGE_RANK[cloud_layers[i+1].coverage]
            if rank_i > rank_next:  # Coverage decreased with altitude
                issues.append(ValidationIssue(
                    rule_name="cloud_coverage_inversion",
                    severity="warning",
                    message=f"Coverage decreases upward: {cloud_layers[i].coverage} " +
                           f"→ {cloud_layers[i+1].coverage}",
                    affected_field=f"cloud_layers[{i}:i+1]"
                ))
        
        return issues
```

**Test Coverage**:
- Applicable to: ~45 test cases with multiple cloud layers
- Expected success rate: 95%+
- Use AviationWeather API data (real clouds)

---

### Task 3.3: Visibility-Weather Relationship Validation

**Purpose**: Ensure weather codes align with visibility measurements.

**Rules**:

```
FG (Fog):
  ✓ Visibility < 1000 meters (500-900m typical)
  ✓ Temperature/Dewpoint spread < 2°C
  ✗ Visibility > 5000m (contradiction)
  Real example: ENVA 151320Z 24008KT 0800 FG VV002 M04/M05 Q1029

BR (Mist - light fog):
  ✓ Visibility 1000-5000 meters
  ✓ Relative humidity 50-99%
  ✗ Visibility > 10000m or < 500m
  Real example: GCTS 151350Z 25015KT 4000 BR BKN 003 05/04 Q1011

RA (Rain):
  ✓ Visibility typically 2000-5000m
  ✓ Humidity high (70-100%)
  ✗ Visibility > 10km with heavy rain
  Real example: FGSL 151300Z 18006KT 3000 RA SHRA BKN010 16/12 Q1012

SN (Snow):
  ✓ Visibility < 2000m (200-1500m typical)
  ✓ Temperature < 0°C (usually)
  ✗ Temperature > +5°C with snow
  Real example: LRBC 151300Z 25010KT 1500 SN BKN020 M02/M03 Q1024

TS (Thunderstorm):
  ✓ Often reduced visibility (but not mandatory)
  ✓ Often with rain/hail
  ✗ Cannot occur during "calm" conditions
  Real example: UTDD 151320Z 09015G25KT 4000 TS RA BKN015CB 18/13 Q1008
```

**Implementation**:

```python
class VisibilityWeatherValidationRule:
    """Validate consistency between weather codes and visibility."""
    
    PHENOMENA_VISIBILITY_RANGES = {
        "FG": {"min": 0, "max": 1000, "severity": "error"},
        "BR": {"min": 500, "max": 5000, "severity": "warning"},  # Lighter constraint
        "RA": {"min": 1000, "max": 10000, "severity": "info"},
        "SN": {"min": 100, "max": 5000, "severity": "warning"},
        "TS": {"min": 0, "max": 10000, "severity": "info"},  # Loose constraint
        "HZ": {"min": 3000, "max": 10000, "severity": "warning"},
        "DZ": {"min": 1000, "max": 5000, "severity": "info"},
    }
    
    def validate(self, 
                 visibility_meters: int, 
                 weather_phenomena: List[str]) -> List[ValidationIssue]:
        """
        Validate visibility aligns with weather.
        
        Args:
            visibility_meters: Reported visibility in meters
            weather_phenomena: List of weather codes (e.g., ['RA', 'BR'])
        
        Returns:
            List of issues (empty if all consistent)
        """
        issues = []
        
        for phenomenon in weather_phenomena:
            if phenomenon not in self.PHENOMENA_VISIBILITY_RANGES:
                continue  # Skip unknown phenomena
            
            expected = self.PHENOMENA_VISIBILITY_RANGES[phenomenon]
            if not (expected["min"] <= visibility_meters <= expected["max"]):
                issues.append(ValidationIssue(
                    rule_name="visibility_weather_consistency",
                    severity=expected["severity"],
                    message=f"Visibility {visibility_meters}m unusual for {phenomenon}",
                    expected=f"{phenomenon}: {expected['min']}-{expected['max']}m",
                    actual=f"Visibility: {visibility_meters}m",
                    affected_field="weather_phenomena, visibility"
                ))
        
        return issues
```

**Test Coverage**:
- Applicable to: 62 test cases with weather phenomena
- Expected success rate: 75-85% (some edge cases allowed)
- Use to validate phenomena extraction

---

### Task 3.4: Detailed Failure Analysis

**Purpose**: Categorize and analyze all conversion failures.

**Failure Categories**:

```
1. DATA_SOURCE_ERROR (20% of failures)
   - Missing fields in METAR
   - Invalid API response format
   - Encoding issues
   Example: METAR string is malformed, station ID missing

2. CONVERSION_LOGIC_BUG (30% of failures)
   - TAC parser errors
   - IWXXM element generation fails
   - Version-specific logic broken
   Example: Temperature parsing fails for negative values

3. SCHEMATRON_VALIDATION (25% of failures)
   - WMO-defined rules violated
   - Required Elements missing
   - Invalid enumeration values
   Example: CloudType not in allowed WMO codelists

4. METEOROLOGICAL_INCONSISTENCY (15% of failures)
   - Physical impossibilities detected
   - Relationship validation fails
   - Semantic validation errors
   Example: Temperature < Dewpoint, invalid cloud ordering

5. CODELIST_VIOLATION (10% of failures)
   - Weather phenomenon not in WMO registry
   - Cloud type unknown
   - Visibility category invalid
   Example: Weather code "XY" not in WMO codelists
```

**Implementation**:

```python
# src/validation/failure_analyzer.py (NEW)
from enum import Enum
from dataclasses import dataclass

class FailureCategory(str, Enum):
    DATA_SOURCE_ERROR = "data_source_error"
    CONVERSION_LOGIC_BUG = "conversion_logic_bug"
    SCHEMATRON_VALIDATION = "schematron_validation"
    METEOROLOGICAL_INCONSISTENCY = "meteorological_inconsistency"
    CODELIST_VIOLATION = "codelist_violation"
    UNKNOWN = "unknown"

@dataclass
class FailureAnalysis:
    test_case_id: str
    raw_metar: str
    category: FailureCategory
    severity: str  # "critical", "major", "minor"
    root_cause: str
    suggested_fix: Optional[str]
    error_message: str
    stack_trace: Optional[str]

class FailureAnalyzer:
    """Categorize and analyze METAR conversion failures."""
    
    def analyze(self, 
                test_case: METARTestCase, 
                conversion_error: Exception, 
                traceback_str: str) -> FailureAnalysis:
        """
        Determine failure category based on error type and message.
        
        Returns: FailureAnalysis with category and suggested fix
        """
        category = self._detect_category(str(conversion_error), traceback_str)
        
        return FailureAnalysis(
            test_case_id=test_case.station_id,
            raw_metar=test_case.raw_metar,
            category=category,
            severity=self._severity_for_category(category),
            root_cause=self._extract_root_cause(conversion_error, traceback_str),
            suggested_fix=self._suggest_fix(category, test_case),
            error_message=str(conversion_error),
            stack_trace=traceback_str
        )
    
    def _detect_category(self, error_msg: str, traceback_str: str) -> FailureCategory:
        """Detect failure category from error patterns."""
        error_lower = error_msg.lower()
        
        # Pattern matching for categories
        if any(x in error_lower for x in ['json', 'decode', 'parse', 'field']):
            return FailureCategory.DATA_SOURCE_ERROR
        
        if any(x in error_lower for x in ['tac', 'parser', 'temperature']):
            return FailureCategory.CONVERSION_LOGIC_BUG
        
        if any(x in error_lower for x in ['schematron', 'assert', 'invalid xml']):
            return FailureCategory.SCHEMATRON_VALIDATION
        
        if any(x in error_lower for x in ['dewpoint', 'cloud', 'visibility']):
            return FailureCategory.METEOROLOGICAL_INCONSISTENCY
        
        if any(x in error_lower for x in ['codelist', 'wmo', 'enumeration']):
            return FailureCategory.CODELIST_VIOLATION
        
        return FailureCategory.UNKNOWN
```

**Output Format**:

```json
{
  "analysis_date": "2026-02-15T10:30:00Z",
  "total_tests": 187,
  "total_failures": 32,
  "failure_rate": "17.1%",
  "by_category": {
    "data_source_error": 6,
    "conversion_logic_bug": 10,
    "schematron_validation": 8,
    "meteorological_inconsistency": 5,
    "codelist_violation": 3
  },
  "failures": [
    {
      "test_case_id": "KDCA",
      "category": "conversion_logic_bug",
      "severity": "major",
      "error": "Temperature parsing failed for 'C12'",
      "suggested_fix": "Fix regex pattern in TAC parser for temperature"
    }
  ]
}
```

---

### Task 3.5: Extended Test Coverage

**Current Coverage**:
```
Total: 187 test cases
Stations: 82 unique
Countries: 5 (CV, EH, KE, LY, MA)
Regions: 4/7 (africa, europe, middle_east, other)
Phenomena: 5/10 (BR, FZRA, HZ, RA, SN)
  Missing: TSRA, FG, CB, TCU, NSW, DZ
Cloud amounts: 6 ({BKN, CLR, FEW, OVC, SCT, SKC})
Complexity: Simple 61%, Medium 28%, Complex 2%
```

**Target Coverage**:
```
Total: 500+ test cases  (2.7x expansion)
Stations: 200+ unique
Countries: 25+ (global)
Regions: 7/7 (all regions)
Phenomena: 10/10 (all types)
  Action: Extend phenomenon_coverage() query
Cloud amounts: 6+ types (complete)
Complexity: Simple 50%, Medium 35%, Complex 15%  (more realistic)
```

**Implementation Strategy**:

```python
# Task 3.5: In metar_test_generator.py

def extend_sample(count: int = 500) -> List[METARTestCase]:
    """Generate extended sample with better geographic spread.
    
    Strategy:
      1. Increase regional quotas (85 per region vs current 27)
      2. Target missing regions (North America, Asia Pacific)
      3. Search specifically for missing phenomena
      4. Oversample complex cases (5x vs current 0.2x)
      5. Ensure 150+ unique countries
    """
    extended_cases = []
    
    # Phase 1: Regional expansion (340 cases)
    for region in self.WORLD_REGIONS:
        cases = self.regional_sample(
            region=region, 
            count=85,  # ↑ from 27
            hours=6    # ↑ from 3
        )
        extended_cases.extend(cases)
    
    # Phase 2: Phenomenon targeting (100 cases)
    phenomena_to_target = ['TSRA', 'FG', 'CB', 'TCU', 'NSW', 'DZ']
    for phenomenon in phenomena_to_target:
        cases = self.phenomenon_coverage(
            required_phenomena=[phenomenon], 
            hours=12,
            limit=20  # 20 per phenomenon × 5 phenomena
        )
        extended_cases.extend(cases)
    
    # Phase 3: Complexity sampling (60 cases)
    # Oversample complex/medium cases to improve distribution
    for complexity_level in ['complex', 'medium']:
        cases = [c for c in extended_cases 
                if self._complexity_category(c.complexity_score()) == complexity_level]
        # Create duplicate samples to 2.5x current complex count
        extended_cases.extend(cases[:20])
    
    # Return deduplicated set (keep order)
    seen = set()
    result = []
    for case in extended_cases:
        if case.station_id not in seen:
            result.append(case)
            seen.add(case.station_id)
    
    return result[:count]  # Return first 'count' cases
```

**Metrics Before/After**:

```
Before (Sprint 2):
  Total Cases: 187
  Success Rate: ~65% (estimated)
  Weather Phenomena: 5/10
  Regions: 4/7
  Complexity Distribution: Heavily skewed to simple (61%)

After (Sprint 3):
  Total Cases: 500+
  Success Rate: ~85% (target, with semantic validation)
  Weather Phenomena: 10/10 (complete)
  Regions: 7/7 (complete)
  Complexity Distribution: Balanced (50% simple, 35% medium, 15% complex)
```

## Implementation Timeline

```
Week 1 (Feb 18-22):
  ✓ Task 3.1: Temperature validation
    - 2 days: implementation
    - 1 day: testing & refinement
  
  ✓ Task 3.2: Cloud layer validation  
    - 2 days: implementation
    - 1 day: testing
  
  → Checkpoint: Both rules working on test data

Week 2 (Feb 25-Mar 01):
  ✓ Task 3.3: Visibility-weather validation
    - 2 days: implementation
    - 2 days: extensive testing
  
  ✓ Task 3.4: Failure analysis framework
    - 2 days: categorization logic
    - 1 day: reporting integration

  → Checkpoint: All validation rules running

Week 3 (Mar 04-08):
  ✓ Task 3.5: Extended test coverage
    - 2 days: expansion implementation
    - 2 days: data collection (live APIs)
    - 1 day: metric analysis

  → DELIVERABLE: Sprint 3 Complete

→ Sprint 4: Documentation & Polish
```

## Success Criteria

### Validation Rules (3.1-3.3)

- [ ] All rules implemented and tested
- [ ] 100+ test cases pass temperature validation
- [ ] 95%+ of multi-layer clouds pass ordering validation
- [ ] 80%+ of weather visibility cases pass consistency rules

### Failure Analysis (3.4)

- [ ] All test failures categorized
- [ ] Root cause identified for 90%+ of failures
- [ ] Suggested fixes documented
- [ ] Category distribution matches hypothesis (30% logic bugs, 25% schema)

### Extended Coverage (3.5)

- [ ] 500+ test cases generated
- [ ] All 10 weather phenomena covered
- [ ] All 7 world regions represented
- [ ] Complexity distribution: 50/35/15 simple/medium/complex

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Real data contradicts rules | Medium | High | Document exceptions, allow warnings |
| API rate limiting | Low | High | Implement exponential backoff |
| Schema changes in IWXXM | Low | High | Version detection, graceful fallback |
| Complex analysis slows tests | Medium | Medium | Cache results, async validation |

## Deliverables

- `src/validation/semantic_rules.py` (500+ lines)
  - TemperatureValidationRule
  - CloudLayerValidationRule
  - VisibilityWeatherValidationRule

- `src/validation/failure_analyzer.py` (300+ lines)
  - FailureAnalyzer class
  - FailureAnalysis dataclass
  - Categorization logic

- `src/testing/metar_test_generator.py` (UPDATED)
  - extend_sample() method
  - Phenomenon targeting improvements

- `tests/test_semantic_validation.py` (NEW, 400+ lines)
  - Parameterized tests for each rule
  - Coverage tracking for rules
  - Failure analysis validation

- `SPRINT3_COMPLETION_REPORT.md`
  - Metrics & analysis results
  - Rule effectiveness summary
  - Recommendations for Sprint 4

## Next Steps (After Sprint 3)

1. **Enhanced Schematron Validation**
   - Integrate semantic rules into schematron validation
   - Custom XSD extensions for rule checks
   
2. **Dashboard/Visualization**
   - Web interface for test results
   - Interactive failure analysis
   - Coverage metrics display

3. **Performance Optimization**
   - Parallel test execution
   - Distributed validation
   - Caching strategies

4. **Production Ready**
   - API stability guarantees
   - Documentation completeness
   - Deployment to staging

---

**Next Action**: Start implementation of Task 3.1 (Temperature Validation)
