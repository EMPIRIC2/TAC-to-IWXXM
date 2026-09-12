# Validation Issue Schema Fix Summary

## Problem Description

All validators were creating `ValidationIssue` objects with incorrect field names, causing Pydantic validation errors:
```
ValidationError: 1 validation error for ValidationIssue
level
  Field required
```

## Root Cause

The `ValidationIssue` Pydantic model (defined in `src/schemas/validation.py`) expects these fields:
- `layer`: ValidationLayer (required)
- **`level`**: ValidationLevel (required) 
- `message`: str (required)
- `location`: Optional[str]
- `code`: Optional[str]
- `suggestion`: Optional[str]

But validators were using old field names:
- `severity` instead of `level`
- `details` (dict) instead of structured location/code strings
- `xpath` instead of `location`
- `error_type` as standalone field instead of mapped to `code`

## Affected Tests

Before fix: **18+ tests failing** with ValidationError
- 11 tests in `test_xsd_validator.py`
- 4 tests in `test_validation_orchestrator.py`
- 3 tests in `test_gml_validator.py`
- Additional failures cascading through integration tests

After fix: **0 ValidationIssue errors** ✅

## Files Modified

### 1. src/utilities/xsd_validator.py (4 instancesfixed)

#### Instance 1: XML Syntax Error Handling (Lines 112-120)
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    severity=ValidationSeverity.ERROR,  # ❌ Wrong field
    message=f"XML parsing failed: {str(e)}",
    details={  # ❌ Wrong field
        "error": str(e),
        "line": getattr(e, 'lineno', None),
        "column": getattr(e, 'offset', None)
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    level=ValidationSeverity.ERROR,  # ✅ Correct
    message=f"XML parsing failed: {str(e)}",
    location=f"line {getattr(e, 'lineno', '?')}, column {getattr(e, 'offset', '?')}",  # ✅ Correct
    code="XML_SYNTAX_ERROR"  # ✅ Added
)
```

#### Instance 2: Schema Not Found (Lines 133-140)
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    severity=ValidationSeverity.ERROR,
    message=f"Schema not available: {str(e)}",
    details={"version": version}
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    level=ValidationSeverity.ERROR,
    message=f"Schema not available for version {version}: {str(e)}",
    code="SCHEMA_NOT_FOUND"
)
```

#### Instance 3: XSD Validation Errors (Lines 152-163)
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    severity=ValidationSeverity.ERROR,
    message=error.message,
    xpath=error.path,  # ❌ Wrong field
    details={
        "line": error.line,
        "column": error.column,
        "domain": error.domain_name,
        "type": error.type_name,
        "level": error.level_name
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    level=ValidationSeverity.ERROR,
    message=error.message,
    location=f"line {error.line}, column {error.column}" if error.line else error.path,  # ✅ Correct
    code=error.type_name or "XSD_VALIDATION_ERROR"  # ✅ Correct
)
```

#### Instance 4: Unexpected Errors (Lines 182-189)
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    severity=ValidationSeverity.ERROR,
    message=f"Validation error: {str(e)}",
    details={"error_type": type(e).__name__}
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.XML_SCHEMA,
    level=ValidationSeverity.ERROR,
    message=f"Validation error: {str(e)}",
    code=type(e).__name__  # ✅ Correct
)
```

### 2. src/utilities/gml_validator.py (4 instances fixed)

#### Instance 1: XML Syntax Error
**Changes**: Same pattern as XSD validator - `severity` → `level`, `details` → `code`

#### Instance 2: Duplicate GML IDs
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.GML_REFERENCES,
    severity=ValidationSeverity.ERROR,
    message=f"Duplicate gml:id '{gml_id}' found at {len(locations)} locations",
    details={
        "gml_id": gml_id,
        "locations": locations,
        "count": len(locations)
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.GML_REFERENCES,
    level=ValidationSeverity.ERROR,
    message=f"Duplicate gml:id '{gml_id}' found at {len(locations)} locations: {', '.join(locations)}",
    code="DUPLICATE_GML_ID"
)
```

#### Instance 3: Broken XLink References
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.GML_REFERENCES,
    severity=ValidationSeverity.ERROR,
    message=f"Broken reference: xlink:href='{href}' points to non-existent gml:id",
    xpath=xpath,  # ❌ Wrong field
    details={
        "href": href,
        "target_id": target_id,
        "available_ids": list(id_registry.keys())[:10]
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.GML_REFERENCES,
    level=ValidationSeverity.ERROR,
    message=f"Broken reference: xlink:href='{href}' points to non-existent gml:id '{target_id}'",
    location=xpath,  # ✅ Correct
    code="BROKEN_XLINK_HREF"
)
```

#### Instance 4: Unexpected Errors
**Changes**: `severity` → `level`, `details` → `code`

### 3. src/utilities/schematron_validator.py (5 instances fixed)

#### Instance 1: Failed Assertions  
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.SCHEMATRON,
    severity=ValidationSeverity.ERROR,
    message=message.strip() if message else 'Schematron assertion failed',
    xpath=location,
    details={
        'pattern_id': pattern_id,
        'test': test,
        'version': version
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.SCHEMATRON,
    level=ValidationSeverity.ERROR,
    message=message.strip() if message else 'Schematron assertion failed',
    location=location,  # ✅ Correct
    code=pattern_id  # ✅ Correct
)
```

#### Instance 2: Successful Reports (Warnings)
**Changes**: Same pattern, but with `level=ValidationSeverity.WARNING`

#### Instances 3-5: Error handling
**Changes**: XML parsing, schema not found, unexpected errors - same pattern as XSD validator

### 4. src/utilities/codelist_parser.py (4 instances fixed)

#### Instance 1: XML Syntax Error
**Changes**: `severity` → `level`, `details` → `code`

#### Instance 2: Codelist Not Found (Warning)
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.WMO_CODELISTS,
    severity=ValidationSeverity.WARNING,
    message=f"Code list '{codelist_name}' not found in loaded RDF files",
    xpath=xpath,
    details={
        "codelist": codelist_name,
        "href": href,
        "available_lists": list(self._cache.keys())[:10]
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.WMO_CODELISTS,
    level=ValidationSeverity.WARNING,
    message=f"Code list '{codelist_name}' not found in loaded RDF files",
    location=xpath,  # ✅ Correct
    code="CODELIST_NOT_FOUND"
)
```

#### Instance 3: Invalid Codelist Value
**Before**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.WMO_CODELISTS,
    severity=ValidationSeverity.ERROR,
    message=f"Invalid code '{potential_code}' for codelist '{codelist_name}'",
    xpath=xpath,
    details={
        "code": potential_code,
        "codelist": codelist_name,
        "href": href,
        "valid_codes": sorted(list(self.get_codes(codelist_name)))[:20]
    }
)
```

**After**:
```python
issue = ValidationIssue(
    layer=ValidationLayer.WMO_CODELISTS,
    level=ValidationSeverity.ERROR,
    message=f"Invalid code '{potential_code}' for codelist '{codelist_name}'. Valid codes include: {', '.join(valid_codes)}",
    location=xpath,
    code="INVALID_CODELIST_VALUE"
)
```

#### Instance 4: Unexpected Errors
**Changes**: `severity` → `level`, `details` → `code`

### 5. tests/test_xsd_validator.py (1 instance fixed)

**Before**:
```python
for issue in result.issues:
    assert issue.message
    assert issue.layer == ValidationLayer.XML_SCHEMA
    assert issue.severity == ValidationSeverity.ERROR  # ❌ Wrong field
    assert issue.details is not None  # ❌ Wrong field
```

**After**:
```python
for issue in result.issues:
    assert issue.message
    assert issue.layer == ValidationLayer.XML_SCHEMA
    assert issue.level == ValidationSeverity.ERROR  # ✅ Correct
    assert issue.location or issue.code  # ✅ Correct
```

## Pattern Summary

### Field Mappings Applied

| Old Field | New Field(s) | Notes |
|-----------|-------------|-------|
| `severity` | `level` | Direct rename |
| `details` (dict) | `location` + `code` + enhanced message | Data moved to appropriate fields |
| `xpath` | `location` | Direct rename |
| `error_type` in details | `code` | Extracted from details dict |
| Extra context in details | Inline in `message` | E.g., "Invalid code 'X'. Valid: A, B, C" |

### Standard Code Values Added

- `XML_SYNTAX_ERROR`
- `SCHEMA_NOT_FOUND`
- `XSD_VALIDATION_ERROR`
- `DUPLICATE_GML_ID`
- `BROKEN_XLINK_HREF`
- `CODELIST_NOT_FOUND`
- `INVALID_CODELIST_VALUE`
- `SCHEMATRON_NOT_FOUND`
- Plus exception class names (e.g., `FileNotFoundError`, `KeyError`)

## Impact

### Tests Fixed
- ✅ All 11 `test_xsd_validator.py` tests now pass (except 3 caching tests - different issue)
- ✅ All `test_gml_validator.py` tests pass
- ✅ All `test_schematron_validator.py` tests pass  
- ✅ All `test_codelist_parser.py` tests pass
- ✅ `test_validation_orchestrator.py` tests no longer fail due to ValidationIssue errors

### Backward Compatibility
**Breaking Change**: Any code accessing `.severity`, `.details`, or `.xpath` on ValidationIssue objects will break.

**Migration**: Update to use `.level`, `.location`, `.code` instead.

### Error Messages Improved
Old format (details hidden in dict):
```
message: "Invalid code 'FOO' for codelist 'CloudType'"
details: {"code": "FOO", "codelist": "CloudType", "valid_codes": ["CU", "CB", ...]}
```

New format (context in message):
```
message: "Invalid code 'FOO' for codelist 'CloudType'. Valid codes include: CU, CB, CI, ..."
code: "INVALID_CODELIST_VALUE"
location: "/iwxxm:METAR/iwxxm:cloud[1]"
```

## Verification

Run validationtests to confirm fix:
```bash
# Should pass without ValidationError
python3 -m pytest tests/test_xsd_validator.py -v
python3 -m pytest tests/test_gml_validator.py -v
python3 -m pytest tests/test_schematron_validator.py -v
python3 -m pytest tests/test_validation_orchestrator.py -v
```

All validator tests now pass except for 3 caching tests (different root cause - schema loading errors).
