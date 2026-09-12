# API Parameter Fix Summary

## Problem

The `/api/v1/convert` and `/api/v1/convert-zip` endpoints had no visible parameters in the OpenAPI/Swagger documentation because they were manually parsing form data instead of using FastAPI's proper parameter declarations.

## Root Cause

**Before**: Endpoints used `request: Request` and manually parsed form data:
```python
async def convert(
    request: Request,
    user: dict = Depends(verify_supabase_token),
) -> ConversionResponse:
    form = await request.form()
    manual_text = form.get("manual_text", "")
    iwxxm_version = form.get("iwxxm_version", "2025-2")
    # ... more manual parsing
```

**Why this was problematic**:
- ❌ Parameters don't appear in OpenAPI/Swagger UI
- ❌ No automatic type validation
- ❌ No automatic documentation generation
- ❌ Harder for API clients to discover what parameters are available

## Solution

**After**: Endpoints use proper FastAPI parameter declarations:
```python
async def convert(
    files: List[UploadFile] = File(default=[], description="..."),
    manual_text: str = Form(default="", description="..."),
    iwxxm_version: str = Form(default="2025-2", description="..."),
    validate_output: bool = Form(default=False, description="..."),
    user: dict = Depends(verify_supabase_token),
) -> ConversionResponse:
    # Parameters automatically parsed and validated by FastAPI
    files = [f for f in files if f.filename]  # Filter empty uploads
```

## Changes Made

### 1. `/api/v1/convert` Endpoint

**Added Parameters**:
- `files: List[UploadFile]` - Optional uploaded text files (File parameter)
- `manual_text: str` - Optional manual METAR TAC input (Form parameter)
- `iwxxm_version: str` - Target IWXXM version, default "2025-2" (Form parameter)
- `validate_output: bool` - Enable full 7-layer validation, default False (Form parameter)

**Updated Logic**:
- Removed manual form parsing
- Added simple filter to remove empty file uploads: `files = [f for f in files if f.filename]`
- All other logic remains unchanged

### 2. `/api/v1/convert-zip` Endpoint

**Added Parameters**:
- `files: List[UploadFile]` - Optional uploaded text files (File parameter)
- `manual_text: str` - Optional manual METAR TAC input (Form parameter)
- `iwxxm_version: str` - Target IWXXM version, default "2025-2" (Form parameter)

**Updated Logic**:
- Removed manual form parsing
- Added IWXXM version validation (same as `/api/v1/convert`)
- **Updated to use `convert_metar_tac_with_metadata`** instead of `convert_metar_tac` for version support
- Added empty file filter
- All other logic remains unchanged

## Verification

### OpenAPI Schema Check ✅
```
✓ /api/v1/convert parameters:
  ✓ files: array - Optional uploaded text files containing METAR TAC
  ✓ manual_text: string - Optional manual text input (METAR TAC format)
  ✓ iwxxm_version: string - Target IWXXM version: 2025-2 (latest), 2023-1, 2021-2
  ✓ validate_output: boolean - Enable full 7-layer IWXXM validation after conversion

✓ /api/v1/convert-zip parameters:
  ✓ files: array - Optional uploaded text files containing METAR TAC
  ✓ manual_text: string - Optional manual text input (METAR TAC format)
  ✓ iwxxm_version: string - Target IWXXM version: 2025-2 (latest), 2023-1, 2021-2
```

### API Tests ✅
```bash
$ pytest tests/test_api.py -v
======================== 10 passed, 1 warning in 2.73s =========================
```

All existing API tests pass without modification.

### Import Validation ✅
```
✓ API imports successfully
✓ Found 2 convert endpoints
```

## Benefits

1. **✅ Visible in Swagger UI**: All parameters now appear in the interactive API documentation at `/docs`
2. **✅ Automatic Validation**: FastAPI validates types and required fields automatically
3. **✅ Better Developer Experience**: API clients can see all available parameters and their descriptions
4. **✅ Type Safety**: Parameters have proper type hints for IDE autocomplete
5. **✅ Consistent with FastAPI Best Practices**: Uses declarative parameter syntax
6. **✅ Version Support**: Both endpoints now support `iwxxm_version` parameter for dynamic version selection

## Testing

To test the fixed endpoints:

```bash
# Start the server
cd backend
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001

# Open Swagger UI in browser
# http://localhost:8001/docs

# You should now see all parameters with descriptions in the UI
```

## Files Modified

- [src/api.py](../src/api.py)
  - Updated `/api/v1/convert` endpoint signature (lines ~408-500)
  - Updated `/api/v1/convert-zip` endpoint signature (lines ~645-710)
  - Changed from manual form parsing to FastAPI parameter declarations
  - Added version validation to convert-zip endpoint
  - Updated convert-zip to use version-aware conversion function

## Migration Notes

**No Breaking Changes**: The endpoints still accept the same parameters in the same format (multipart/form-data). API clients don't need any changes.

**Improved**: The only difference is that parameters are now properly documented and validated by FastAPI instead of being manually parsed.
