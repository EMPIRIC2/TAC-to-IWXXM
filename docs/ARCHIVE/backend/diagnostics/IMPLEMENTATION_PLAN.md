# Implementation Plan: Strict 2023-1 IWXXM Validation with Schematron

## Phase Overview

**Objective**: Implement full 2023-1 IWXXM validation with exact Schematron compliance  
**Constraint**: Must use Docker/Java/Saxon for XSLT2 processing (no shortcuts)  
**Source of Truth**: IWXXM Schematron rules + IWXXM translation repo test pairs  
**Timeline**: 4-5 days focused implementation  

---

## Phase 1: Parser & Diagnostic Fixes (Day 1 - 4 hours)

### 1.1 Fix XML Comparison Tool (Priority: BLOCKING)
**File**: `backend/tests/_comparative_xml_utils.py`  
**Issue**: False test failures due to whitespace/text node handling  
**Approach**: Normalize XML before comparison

**Changes**:
1. Add `normalize_xml_for_comparison()` function
   - Parse with minidom
   - Remove whitespace-only text nodes
   - Return prettified XML string
2. Add `filter_element_children()` function
   - Filter list to element nodes only (nodeType == 1)
   - Ignore text nodes
3. Update `DiffReport.compare_elements()`
   - Normalize both XMLs before comparing
   - Use filtered child element lists
4. Update coordination/lat-lon comparison
   - Handle both 8-decimal and 2-decimal formats
   - Skip UUID differences (cosmetic)

**Expected Result**: BGBW-282350Z test shows PASS or PASS_WITH_NOTES instead of FAIL

---

### 1.2 Fix XSD Diagnostic Exception Handling
**File**: `backend/diagnostics/xsd_schema_analysis.py`  
**Issue**: Uses non-existent `etree.XMLSchemaException`  
**Fix**: Change to `etree.XMLSchemaParseError`  
**Effort**: 15 minutes

---

### 1.3 Rerun BGBW Test
**Test**: `test_metar_converts_to_matching_iwxxm[tac_file0-xml_file0-Amd78-2018]`  
**Expected**: Should now show PASS (previously FAIL)  
**Purpose**: Validate parser fix before moving to Schematron

---

## Phase 2: Docker & Schematron Infrastructure (Day 2 - 6 hours)

### 2.1 Plan Docker/Java/Saxon Setup
**Decision**: Use Docker container with Java + Saxon XSLT2 processor

**Options**:
- **Option A**: Use existing Java Docker image + install Saxon (lightweight)
- **Option B**: Create custom Dockerfile with Saxon built-in (clean, reusable)
- **Option C**: Use pre-built container (if exists)

**Recommended**: Option B (custom Dockerfile)

**Components**:
1. `Dockerfile.schematron` - with Java + Saxon
2. `docker-compose.yml` entry for Schematron service
3. Python subprocess wrapper in validator

**Container Interface**:
```bash
# Input: XML file + Schematron schema
# Output: Validation report JSON with errors
docker run metar-iwxxm-schematron:latest \
  -xml input.xml \
  -sch schema.sch \
  -output json
```

---

### 2.2 Create Custom Dockerfile for Schematron
**File**: `backend/Dockerfile.schematron`

**Content**:
```dockerfile
FROM openjdk:11-jre-slim

# Install Saxon XSLT2 processor
RUN apt-get update && apt-get install -y wget unzip && \
    mkdir -p /opt/saxon && cd /opt/saxon && \
    wget https://sourceforge.net/projects/saxon/files/Saxon-HE/11.4/SaxonHE11-4J.zip && \
    unzip SaxonHE11-4J.zip && \
    rm SaxonHE11-4J.zip

# Install Schematron ISO XSLT
RUN git clone https://github.com/Schematron/schematron.git /opt/schematron

# Copy validation script
COPY schematron-validator.sh /usr/local/bin/

ENTRYPOINT ["schematron-validator.sh"]
```

**Validation Script** (`schematron-validator.sh`):
- Takes XML file + Schematron schema as arguments
- Runs Saxon XSLT2 processor
- Returns JSON validation report

---

### 2.3 Create Docker Compose Entry
**File**: Update `docker-compose.yml`

```yaml
schematron-validator:
  build:
    context: ./backend
    dockerfile: Dockerfile.schematron
  image: metar-iwxxm-schematron:latest
  volumes:
    - ./schemas:/schemas:ro
    - ./test-data:/test-data:ro
  environment:
    - JAVA_OPTS=-Xmx512m
```

---

## Phase 3: Schematron Validator Implementation (Day 3-4 - 8 hours)

### 3.1 Create Schematron Validator with Docker Backend
**File**: `backend/src/utilities/schematron_validator_docker.py`

**Features**:
1. XSLT2 compilation via Docker + Saxon
2. Full Schematron rule validation
3. Detailed error reporting
4. Progress logging (INFO/DEBUG)
5. Caching of compiled schemas

**Interface**:
```python
class SchematronValidatorDocker:
    def __init__(self, schema_path: str, version: str = "2023-1"):
        self.schema_path = schema_path
        self.version = version
        self._docker_client = docker.from_env()
        self._container_image = "metar-iwxxm-schematron:latest"
    
    def validate(self, xml_content: str) -> SchematronResult:
        """
        Validate XML against Schematron schema using Docker.
        
        Returns:
            - validators_passed: List of passing rules
            - validators_failed: List of failing rules with details
            - assertion_errors: Specific assertion failures
            - report_text: Full validation report
        """
```

**Key Methods**:
- `validate(xml_content)` - Main validation entry point
- `_prepare_xml_file()` - Write XML to temp file
- `_run_docker_validation()` - Execute Docker container
- `_parse_schema_report()` - Parse Saxon output
- `_filter_cosmetic_diffs()` - Ignore UIDs, dates, etc.

---

### 3.2 Exact Format Matching
**Critical**: Match IWXXM translation repo test pairs exactly

**Match Criteria**:
- ✅ Element structure (must match 100%)
- ✅ Attribute values (must match 100%)
- ✅ Text content (must match 100%)
- ❌ UUIDs/gml:id values (ignore - cosmetic)
- ❌ Timestamp milliseconds (ignore - system time)
- ❌ Record date values (ignore - report date)
- ✅ Coordinate precision (must match version rules)
- ✅ Elevation values (must match version rules)
- ✅ Codelist references (must match WMO codes)

**Implementation in Validator**:
```python
def _should_ignore_difference(self, path: str, expected: str, actual: str) -> bool:
    """Determine if difference is cosmetic."""
    # Skip: //*/@gml:id, //*/@*[contains(local-name(), 'UUID')]
    # Skip: timePosition millisecond variations
    # Skip: reportStatus variations
    # Keep everything else for validation
    return self._is_cosmetic_attribute(path)
```

---

### 3.3 Integration with Validation Orchestrator
**File**: `backend/src/services/validation_orchestrator.py`

**Changes**:
1. Add Schematron validator to pipeline (Layer 6)
2. Make Docker-based validator the 2023-1 implementation
3. Keep existing validators for other versions
4. Log validation layer results
5. Track pass/fail per layer

---

## Phase 4: Testing & Validation (Day 5 - 8 hours)

### 4.1 Run BGBW Test After Parser Fix
**Test**:
```bash
pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_matching_iwxxm[tac_file0-xml_file0-Amd78-2018] -v
```

**Expected**: PASS (not FAIL)

---

### 4.2 Run 2023-1 Schematron Tests
**Test**:
```bash
pytest tests/test_schematron_validation_2023_1.py -v --tb=short
```

**Coverage**: All Amd79-80-2023 test cases

---

### 4.3 Run Full Test Suite
**Test**:
```bash
pytest tests/test_metar_pairs_comprehensive.py -k "Amd79-80-2023" -v
```

**Expected**:
- BGBW-282350Z: PASS
- All Amd79-80-2023 cases: ≥ 95% PASS rate
- Failures: Document and triage

---

### 4.4 Compare Against IWXXM Translation Repo
**File**: `/root/metar-to-IWXXM/data/iwxxm-translation/Amd79-80-2023/metar/`

**Comparison**:
1. Generate XML for each test case
2. Compare against reference XML
3. Filter cosmetic differences (UUIDs, timestamps)
4. Report exact match rate

**Expected**: ≥ 99% structure match, ≥ 98% content match

---

## Phase 5: Validation Compliance & Documentation (Day 5-6)

### 5.1 Create Validation Report
**Content**:
- Schematron rules passed: X/Y
- Schematron rules failed: List with details
- Test suite pass rate: X%
- Comparison to reference data: X% match
- Known discrepancies: List (if any)

### 5.2 Document Workarounds
**For schema issues we work around**:
- XSD QName resolution (AIXM dependency)
- Namespace resolution
- External schema imports

---

## Implementation Sequence

```
Day 1 (4 hours):
  ✓ Fix XML comparison tool normalization
  ✓ Fix XSD diagnostic exception handling
  ✓ Rerun BGBW test - validate parser fix

Day 2 (6 hours):
  ✓ Plan Docker/Java/Saxon infrastructure
  ✓ Create Dockerfile.schematron with Saxon
  ✓ Update docker-compose.yml

Day 3 (4 hours):
  ✓ Build Docker image locally
  ✓ Test Docker Schematron validation manually

Day 4 (4 hours):
  ✓ Implement Python wrapper (schematron_validator_docker.py)
  ✓ Integration with validation_orchestrator.py

Day 5 (8 hours):
  ✓ Run test suite with Schematron validation
  ✓ Compare against IWXXM translation repo
  ✓ Document any discrepancies

Day 6 (4 hours):
  ✓ Generate final validation report
  ✓ Document workarounds and design decisions
  ✓ Prepare for deployment
```

**Total Effort**: 30 hours across 6 days (or 4-5 focused days)

---

## Key Decision Points

### Docker vs In-Process (DECIDED: Docker)
✅ **Docker** - More robust, external process isolation, can upgrade independently

### Ignore Cosmetic Diffs (DECIDED: Yes)
✅ **Ignore**: UUIDs, timestamps, record dates  
✅ **Enforce**: Schematron rules, element structure, values

### Skip or Full Validation (DECIDED: Full)
✅ **Full validation** - Implement Schematron with XSLT2 support, no shortcuts

### Source of Truth (DECIDED: IWXXM + Schematron)
✅ **Primary**: IWXXM Schematron rules  
✅ **Secondary**: IWXXM translation repo test pairs  

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Docker build fails | Medium | High | Test locally first, use verified base image |
| Saxon requires licensing | Low | High | Use open-source Saxon HE (free) |
| Schema imports on network | Medium | Medium | Cache GML/AIXM schemas locally |
| Cosmetic diff filtering too aggressive | Low | High | Test exhaustively with known pairs |
| Docker performance overhead | Low | Low | Use caching, optimize container |

---

## Files to Create/Modify

### Create (New):
- `backend/Dockerfile.schematron`
- `backend/schematron-validator.sh`
- `backend/src/utilities/schematron_validator_docker.py`
- `backend/tests/test_schematron_validation_2023_1.py`
- `backend/diagnostics/IMPLEMENTATION_PROGRESS.md`

### Modify (Existing):
- `backend/tests/_comparative_xml_utils.py` (normalization fix)
- `backend/diagnostics/xsd_schema_analysis.py` (exception handling)
- `backend/src/services/validation_orchestrator.py` (add Schematron layer)
- `docker-compose.yml` (add schematron service)

---

## Success Criteria

- ✅ BGBW-282350Z passes Schematron validation
- ✅ 100+ test cases run without crashing
- ✅ ≥ 95% of Amd79-80-2023 tests pass
- ✅ XML structure matches reference repo ≥ 99%
- ✅ All validation layers implemented
- ✅ Logging at INFO/DEBUG levels working
- ✅ Docker container builds successfully
- ✅ Schematron rules processed via XSLT2

---

## Next Action

Proceed to implementation Phase 1:
1. Fix XML comparison tool
2. Fix XSD diagnostic
3. Rerun BGBW test

Then move to Phase 2 (Docker setup) based on Phase 1 results.
