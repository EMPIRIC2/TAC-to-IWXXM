# IWXXM Dynamic Version Switching Research Report

## Executive Summary

**Finding: GIFTs DOES NOT currently support dynamic version switching at runtime without modifying config files.**

- GIFTs encoder hardcodes IWXXM version to **2023-1**
- Backend API does NOT accept version parameters
- Version is configured in `xmlConfig.py` line 29 (`_iwxxm = '2023-1'`)
- Implementation would require modifying encoder instantiation patterns
- Backend validation infrastructure IS in place to support multiple versions

---

## 1. Current State: Version Hardcoding in GIFTs

### Source of Hardcoding
**File:** `GIFTs/gifts/common/xmlConfig.py` (lines 29-32)

```python
# IWXXM release name
_iwxxm = '2023-1'
_release = '2023-1'

IWXXM_URI = 'http://icao.int/iwxxm/%s' % _iwxxm
IWXXM_URL = 'https://schemas.wmo.int/iwxxm/%s/iwxxm.xsd' % _release
```

### How It Gets Used

1. **Common.py:** Sets namespace in encoder base class
   ```python
   # File: GIFTs/gifts/common/Common.py lines 34-35
   self.NameSpaces = {'aixm': '...',
                      'iwxxm': des.IWXXM_URI,  # Uses hardcoded 2023-1
   ```

2. **metarEncoder.py:** Uses IWXXM_URI in XML schema location
   ```python
   # File: GIFTs/gifts/metarEncoder.py line 76
   self.XMLDocument.set('xsi:schemaLocation', '%s %s' % (des.IWXXM_URI, des.IWXXM_URL))
   ```

3. **All code paths use `des.IWXXM_URI` from imported xmlConfig**

---

## 2. Encoder Instantiation Pattern (No Version Parameters)

### METAR Encoder
**File:** `GIFTs/gifts/METAR.py`

```python
class Encoder(E.Encoder):
    def __init__(self, geoLocationsDB):
        super(Encoder, self).__init__()
        # ... no version parameter accepted
        self.decoder = metarDecoder.Annex3()
        self.encoder = metarEncoder.Annex3()
```

### TAF Encoder
**File:** `GIFTs/gifts/TAF.py`

```python
class Encoder(E.Encoder):
    def __init__(self, geoLocationsDB):
        super(Encoder, self).__init__()
        # ... no version parameter accepted
        self.decoder = tafDecoder.Decoder()
        self.encoder = tafEncoder.Encoder()
```

### Base Encoder Class
**File:** `GIFTs/gifts/common/Encoder.py`

```python
class Encoder(object):
    def __init__(self):
        # ... no version parameter
        os.environ['TZ'] = 'GMT0'

    def encode(self, text, receiptTime=None, **attrs):
        # ... kwargs ignored for version
```

**Conclusion:** No encoder accepts version parameters.

---

## 3. Backend Conversion Functions (No Version Parameters)

### Convert Function
**File:** `backend/src/utilities/conversion.py` (lines 56-81)

```python
def convert_metar_tac(tac_text: str) -> str:
    """Convert METAR/SPECI TAC text to IWXXM XML.
    
    Args:
        tac_text: METAR or SPECI TAC format text
    
    Returns:
        XML string in IWXXM format
    """
    if metarDecoder is None or metarEncoder is None:
        raise ConversionError(...)
    
    try:
        decoder = metarDecoder.Annex3()      # ← No version param
        encoder = metarEncoder.Annex3()      # ← No version param
    except Exception as e:
        raise ConversionError(...)
    
    # ... conversion proceeds with hardcoded 2023-1 version
```

### Backend API Endpoints
**File:** `backend/src/api.py`

The `/api/v1/convert` endpoint does NOT accept version:

```python
@app.post("/api/v1/convert", response_model=ConversionResponse, tags=["Conversion"])
async def convert(
    files: List[UploadFile] = File(default=[], description="METAR TAC files"),
    manual_text: str = Form(default="", description="Manual METAR text"),
    user: dict = Depends(verify_supabase_token),
) -> ConversionResponse:
    # NO version parameter
    xml_text = convert_metar_tac(manual_text.strip())  # ← Hardcoded version
```

**Conclusion:** Backend API does not expose version selection.

---

## 4. What IWXXM Versions Are Supported (Infrastructure)

### Backend Validation Infrastructure
**File:** `backend/src/schemas/iwxxm_validation.py` (lines 65-70)

```python
class IWXXMVersion(str, Enum):
    """Supported IWXXM versions."""
    VERSION_2016 = "2016-1"
    VERSION_2018 = "2018-2"
    VERSION_3_0 = "3.0"  # Used in some Amd78-2018 test data
    VERSION_2021_2 = "2021-2"
    VERSION_2023_1 = "2023-1"
    VERSION_2025_2 = "2025-2"
```

The backend CAN validate these versions (lines 108-110):

```python
def is_supported_iwxxm_version(version: str) -> bool:
    """Check if an IWXXM version is supported."""
    return version in SUPPORTED_IWXXM_VERSIONS
```

**Important:** This is validation only, NOT encoding.

---

## 5. Test Data: What IWXXM Versions Exist

### Amendment Folder Structure & Versions

| Amendment | Folder | IWXXM Version File | Actual NS in XML |
|-----------|--------|---------------------|-----------------|
| Amd77-2016 | `Amd77-2016/` | ❌ Missing | `http://icao.int/iwxxm/2.1` |
| Amd78-2018 | `Amd78-2018/` | ❌ Missing | `http://icao.int/iwxxm/3.0` |
| Amd79-80-2021 | `Amd79-80-2021/` | ✅ `2021-2` | ← Content matches |
| Amd79-80-2023 | `Amd79-80-2023/` | ✅ `2023-1` | ← Content matches |

### Test File Verification

```bash
# Amd77-2016 uses IWXXM 2.1
$ grep -o 'xmlns:iwxxm="[^"]*"' data/iwxxm-translation/Amd77-2016/metar/metar-A3-1.xml
xmlns:iwxxm="http://icao.int/iwxxm/2.1"

# Amd78-2018 uses IWXXM 3.0
$ grep -o 'xmlns:iwxxm="[^"]*"' data/iwxxm-translation/Amd78-2018/metar/BGBW-282350Z.xml
xmlns:iwxxm="http://icao.int/iwxxm/3.0"

# Amd79-80-2021 uses IWXXM 2021-2
$ cat data/iwxxm-translation/Amd79-80-2021/IWXXM_VERSION
2021-2

# Amd79-80-2023 uses IWXXM 2023-1
$ cat data/iwxxm-translation/Amd79-80-2023/IWXXM_VERSION
2023-1
```

---

## 6. Validation Tools Support Version Arguments

### Only for Validation, NOT Encoding

**File:** `GIFTs/validation/iwxxmValidator.py` (lines 108-109)

```python
parser.add_argument("-v", "--version", 
    help="IWXXM version major.minor number to validate against, default '2023-1'",
    type=str, default="2023-1")
```

This is for validating XML against specific schema versions, NOT for encoding.

---

## 7. Current Version Mismatch Issue

The backend tests reveal a mismatch (lines from `backend/tests/test_iwxxm_examples.py`):

```python
def test_metar_examples_older_2023_1_produces_valid_subtree(
    tac_path: pathlib.Path, xml_path: pathlib.Path
) -> None:
    """
    Test that older METAR/SPECI TAC produces valid IWXXM output.
    
    Older test data uses earlier IWXXM versions (2016, 2018, 2021-2).
    GIFTs encoder produces IWXXM 2023-1 (now 2025-2 per code).  ← HARDCODED
    """
```

Tests only validate subtree matching because **GIFTs always produces the current hardcoded version**, not the test data version.

---

## 8. Intended Architecture: Version Parameter Exists in Frontend

**File:** `frontend/supabase/functions/server/index.tsx` (lines 357-360)

```typescript
// Conversion parameters
const {
  bulletinId = 'SAAA00',
  issuingCenter = 'KWBC',
  iwxxmVersion = '3.0',  // ← Parameter defined but NOT USED
  strictValidation = true,
  includeNilReasons = true,
  // ...
} = params || {};
```

This suggests the **intent was to support version switching**, but:
1. GIFTs encoder doesn't support it
2. Backend doesn't expose it
3. Frontend parameter is accepted but not passed to backend

---

## How to Implement Runtime Version Switching

### Option 1: Modify xmlConfig.py with Environment Variable (Simplest)

```python
import os

# IWXXM release name - can be overridden at runtime
_iwxxm = os.getenv('IWXXM_VERSION', '2023-1')
_release = os.getenv('IWXXM_RELEASE', '2023-1')

IWXXM_URI = 'http://icao.int/iwxxm/%s' % _iwxxm
IWXXM_URL = 'https://schemas.wmo.int/iwxxm/%s/iwxxm.xsd' % _release
```

**Pros:** Minimal changes, works with Docker
**Cons:** Only per-process, not per-request

### Option 2: Parameterize Encoder Constructors (Proper Solution)

Modify encoder classes to accept version parameter:

```python
# GIFTs/gifts/common/Encoder.py
class Encoder(object):
    def __init__(self, iwxxm_version='2023-1'):
        self.iwxxm_version = iwxxm_version
        os.environ['TZ'] = 'GMT0'

# GIFTs/gifts/METAR.py
class Encoder(E.Encoder):
    def __init__(self, geoLocationsDB, iwxxm_version='2023-1'):
        super(Encoder, self).__init__(iwxxm_version)
        self.decoder = metarDecoder.Annex3()
        self.encoder = metarEncoder.Annex3(iwxxm_version)
```

Then modify Common.py to use instance variable:

```python
class Base(object):
    def __init__(self, iwxxm_version='2023-1'):
        self._iwxxm_version = iwxxm_version
        self.NameSpaces = {
            'iwxxm': 'http://icao.int/iwxxm/%s' % self._iwxxm_version,
            # ... other namespaces
        }
```

**Pros:** Per-request version switching, clean API
**Cons:** Requires changes to many encoder classes

### Option 3: Pass Version Through Backend API (Full Integration)

Update `backend/src/api.py`:

```python
@app.post("/api/v1/convert", response_model=ConversionResponse, tags=["Conversion"])
async def convert(
    files: List[UploadFile] = File(default=[]),
    manual_text: str = Form(default=""),
    iwxxm_version: str = Form(default="2023-1"),  # ← ADD THIS
    user: dict = Depends(verify_supabase_token),
) -> ConversionResponse:
    xml_text = convert_metar_tac(manual_text.strip(), iwxxm_version=iwxxm_version)
```

Update `backend/src/utilities/conversion.py`:

```python
def convert_metar_tac(tac_text: str, iwxxm_version: str = '2023-1') -> str:
    decoder = metarDecoder.Annex3()
    encoder = metarEncoder.Annex3(iwxxm_version)  # ← Pass version
    # ... rest of function
```

**Pros:** Full end-to-end version switching
**Cons:** Requires Option 2 (parameterization) as prerequisite

---

## Summary Table

| Aspect | Current State | Supported? |
|--------|--------------|------------|
| GIFTs accepts version parameter | ❌ No | No |
| Backend accepts version parameter | ❌ No | No |
| API endpoint has version parameter | ❌ No | No |
| Environment variable override | ❌ No | No |
| Backend validation infrastructure | ✅ Yes | Yes (validation only) |
| Test data for multiple versions | ✅ Yes | 2016-1, 2018-2, 2021-2, 2023-1 |
| Version feature toggles | ❌ No | No |
| Configuration injection | ❌ No | No |

---

## Recommendations

### Short-term (Quick Fix)
1. Add environment variable support to `xmlConfig.py`
2. Document how to override via `IWXXM_VERSION` env var
3. No code changes needed for GIFTs usage

### Medium-term (Proper Solution)
1. Parameterize all encoder classes with version
2. Expose version parameter in backend API endpoints
3. Pass through from frontend to backend
4. Validate version against supported list

### Long-term (Architecture)
1. Support multiple IWXXM schema sets in GIFTs
2. Dynamic schema loading based on version
3. Multi-version validation pipeline
4. Per-amendment encoder instances

---

## Files Requiring Changes (By Option)

### Option 1 (Environment Variable)
- `GIFTs/gifts/common/xmlConfig.py` (2-3 lines)

### Option 2 (Full Parameterization)
- `GIFTs/gifts/common/Encoder.py` (add parameter to `__init__`)
- `GIFTs/gifts/common/Common.py` (use dynamic namespace)
- `GIFTs/gifts/METAR.py` (pass to super)
- `GIFTs/gifts/TAF.py` (pass to super)
- `GIFTs/gifts/SWA.py`, `TCA.py`, `VAA.py` (similar)
- `GIFTs/gifts/metarEncoder.py`, `tafEncoder.py`, etc. (pass to init)

### Option 3 (Full End-to-End)
- All files from Option 2, plus:
- `backend/src/utilities/conversion.py` (add version param)
- `backend/src/api.py` (expose version in endpoints)
- `frontend/supabase/functions/server/index.tsx` (use version param)

