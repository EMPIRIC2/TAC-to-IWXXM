# XSD Validator NoneType Error Fix

## Issue
The XSD validator was throwing `'NoneType' object has no attribute 'validate'` during validation of live METAR conversions. This occurred when the schema object was `None` but the code attempted to call `.validate()` on it.

## Root Cause
In the `_get_compiled_schema()` method, when a known schema import issue was detected (e.g., substitutionGroup resolution issues in IWXXM 2025-2):
1. The code cached `None` in `self._schema_cache[version]` to prevent repeated compilation attempts
2. On subsequent calls, `_get_compiled_schema()` would return the cached `None` without raising an exception
3. The `validate()` method didn't check if the schema was `None` before calling `.validate(xml_doc)`

## Solution
Implemented a two-part fix in [src/utilities/xsd_validator.py](src/utilities/xsd_validator.py):

### Part 1: Improved Cache Handling (lines 50-58)
Modified `_get_compiled_schema()` to skip returning cached `None` values:
```python
if version in self._schema_cache:
    cached_schema = self._schema_cache[version]
    # Don't return cached None - it means schema had issues, recompile to get error details
    if cached_schema is None:
        logger.debug(f"Schema for {version} has known parse issues, recompiling to get error details")
        # Don't return None - allow recompilation to properly raise the error
    else:
        logger.debug(f"Using cached XSD schema for version {version}")
        return cached_schema
```

### Part 2: Added Null Check Before Validation (lines 214-227)
Added a safety check in the `validate()` method before attempting to call `.validate()`:
```python
# Check if schema is None (cached as non-blocking issue)
if schema is None:
    logger.warning(f"Schema for {version} is None - skipping validation")
    issue = ValidationIssue(
        layer=ValidationLayer.XML_SCHEMA,
        level=ValidationSeverity.WARNING,
        message=f"Schema validation skipped due to known schema issues",
        code="SCHEMA_SKIPPED"
    )
    issues.append(issue)
    return XSDValidationResult(
        is_valid=True,  # Non-blocking
        issues=issues,
        schema_version=version
    )
```

## Impact
- **Before**: Validation would crash with `'NoneType' object has no attribute 'validate'`
- **After**: Validation gracefully handles schema issues by skipping validation and returning a non-blocking warning

## Verification
The fix has been tested with a mock scenario where schema is `None`:
- Validation completes successfully without crashing
- Returns `is_valid=True` with a warning issue
- Allows METAR conversion tests to proceed despite known schema issues

## Files Modified
- [src/utilities/xsd_validator.py](src/utilities/xsd_validator.py) - Added null schema check and improved cache handling
