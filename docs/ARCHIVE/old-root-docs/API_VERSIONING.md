# API Versioning Guide

## Overview

The METAR to IWXXM Backend API now uses semantic versioning with the `/api/v1/` base path. This document describes the versioning strategy, endpoints, and migration guide for clients.

## API Versions

### Current Version: v1

**Base URL**: `/api/v1`

All conversion endpoints must use the versioned path prefix.

## Endpoints

### Health Check (v-agnostic)

```
GET /health
```

**Description**: Check API health and GIFTs library availability

**Response**: 
```json
{
  "status": "healthy|degraded",
  "version": "0.1.0",
  "gifts_available": true|false
}
```

**Status Codes**:
- `200 OK` - API is operational

---

### Manual Text Conversion

```
POST /api/v1/convert
```

**Description**: Convert METAR/SPECI TAC text to IWXXM XML

**Authentication**: Required (Supabase JWT token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body** (form data):
- `manual_text` (string, optional): METAR text to convert
- `files` (file array, optional): METAR text files to convert

**Response** (200 OK):
```json
{
  "results": [
    {
      "name": "manual_input.txt",
      "content": "<iwxxm:METAR>...</iwxxm:METAR>",
      "source": "manual",
      "size_bytes": 2048
    }
  ],
  "errors": [],
  "total_processed": 1,
  "successful": 1,
  "failed": 0
}
```

**Status Codes**:
- `200 OK` - Conversion successful (may include errors for individual items)
- `400 Bad Request` - Invalid input or all conversions failed
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User lacks permissions

**Example Usage** (TypeScript):
```typescript
import { convertMetarToIwxxm } from '@/utils/api';

const result = await convertMetarToIwxxm({
  manualText: "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
});

console.log(`Converted ${result.successful} items`);
result.results.forEach(r => console.log(r.name));
```

---

### Batch Conversion to ZIP

```
POST /api/v1/convert-zip
```

**Description**: Convert multiple METAR/SPECI TAC to zipped IWXXM XML files

**Authentication**: Required (Supabase JWT token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body** (form data):
- `manual_text` (string, optional): METAR text to convert
- `files` (file array, optional): METAR text files

**Response** (200 OK):
- Content-Type: `application/zip`
- Body: Binary ZIP file containing:
  - `*.xml` files (converted IWXXM output)
  - `errors.txt` (if any conversions failed)

**Status Codes**:
- `200 OK` - ZIP created successfully
- `400 Bad Request` - No valid conversions
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - User lacks permissions

**Example Usage** (TypeScript):
```typescript
import { convertMetarToIwxxmZip, downloadBlob } from '@/utils/api';

const zipBlob = await convertMetarToIwxxmZip({
  files: [file1, file2, file3],
  manualText: "METAR KJFK ..."
});

downloadBlob(zipBlob, 'conversions.zip');
```

---

## Backwards Compatibility

### Migration Path

**Old Endpoints** (⚠️ Deprecated):
- `POST /api/convert` → `POST /api/v1/convert`
- `POST /api/convert-zip` → `POST /api/v1/convert-zip`

**Status**: Endpoints without version prefix are **deprecated** and will be removed in v2.0.0

**Deprecation Timeline**:
- v0.1.0: Non-versioned endpoints still work (with warnings)
- v1.0.0: Versioned endpoints required
- v2.0.0: Non-versioned endpoints removed

### Client Migration Checklist

For existing clients using the old `/api/` paths:

- [ ] Update all API calls to use `/api/v1/` base path
- [ ] Test with new endpoints in staging
- [ ] Update documentation
- [ ] Deploy client changes before v2.0.0 release

---

## Frontend Integration

### Using the API Client

The frontend provides a TypeScript API client in `frontend/src/utils/api.ts`:

```typescript
import {
  checkHealth,
  convertMetarToIwxxm,
  convertMetarToIwxxmZip,
  downloadBlob,
} from '@/utils/api';

// Check health
const health = await checkHealth();
if (health.gifts_available) {
  console.log('Backend is ready');
}

// Single conversion
const result = await convertMetarToIwxxm({
  manualText: "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
});

// Batch to ZIP
const zipBlob = await convertMetarToIwxxmZip({
  files: selectedFiles,
  manualText: additionalMetar
});

downloadBlob(zipBlob, 'iwxxm_output.zip');
```

### Environment Variables

The frontend reads the backend URL from environment variables:

```env
# frontend/.env
VITE_BACKEND_URL=http://localhost:8001
```

The API client automatically constructs:
```
${VITE_BACKEND_URL}/api/v1/convert
${VITE_BACKEND_URL}/api/v1/convert-zip
```

---

## Authentication

All versioned API endpoints require Supabase JWT authentication.

### Obtaining a Token

```typescript
import { supabase } from '@/utils/supabase/client';

const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;
```

### Including in Requests

```typescript
const response = await fetch('/api/v1/convert', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
  },
  body: formData,
});
```

### Error Handling

```typescript
if (response.status === 401) {
  // Token expired or invalid - re-authenticate
  await supabase.auth.signInWithPassword({...});
}

if (response.status === 403) {
  // User lacks permissions - check authorization
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": {
    "message": "All conversions failed",
    "errors": [
      "manual_input: Invalid METAR format",
      "file1.tac: Empty file"
    ],
    "total_errors": 2
  }
}
```

### Common Error Scenarios

| Error | Status | Solution |
|-------|--------|----------|
| Invalid METAR format | 400 | Check TAC compliance |
| Empty input | 400 | Provide valid METAR text |
| Missing auth token | 401 | Sign in and obtain token |
| Invalid token | 401 | Refresh token / re-authenticate |
| User not authorized | 403 | Check user permissions |
| Backend offline | 503 | Check server status |

### Frontend Error Handling Template

```typescript
import { toast } from 'sonner';

try {
  const result = await convertMetarToIwxxm({
    manualText: metarText,
    files: selectedFiles,
  });

  if (result.errors.length > 0) {
    toast.warning(`${result.successful}/${result.total_processed} conversions succeeded`, {
      description: result.errors.join('; '),
    });
  } else {
    toast.success(`Successfully converted ${result.successful} items`);
  }
} catch (error) {
  if (error instanceof Error) {
    toast.error('Conversion failed', { description: error.message });
  }
}
```

---

## API Documentation

### Auto-Generated Docs

Swagger/OpenAPI documentation available at:
```
${BACKEND_URL}/docs
${BACKEND_URL}/redoc
```

### Database & Testing

All endpoints tested with:
- Unit tests in `backend/tests/test_api.py`
- Integration tests in `tests/test_integration.py`
- Minimum 90% code coverage requirement

---

## Versioning Strategy

### Semantic Versioning

The API follows [Semantic Versioning](https://semver.org/):

```
/api/{MAJOR}.{MINOR}.{PATCH}
```

**Version Increments**:

- **Major** (v2.0.0): Breaking changes
  - Removed endpoints
  - Changed request/response formats
  - Required client updates
  
- **Minor** (v1.1.0): New features (backward compatible)
  - New endpoints
  - Optional request parameters
  - No client updates required
  
- **Patch** (v1.0.1): Bug fixes
  - No API changes
  - Internal fixes only

### Future Versions

**Planned for v1.1.0**:
- Batch conversion with progress tracking
- Conversion templates (pre-configured options)
- Metadata enrichment options
- Custom validation rules

**Planned for v2.0.0**:
- Remove non-versioned `/api/` endpoints
- Remove deprecated parameters
- New authentication methods

---

## Deployment

### Docker Deployment

The backend automatically serves versioned APIs. No special configuration needed.

```bash
# Build
docker build -t metar-backend:v1 backend/

# Run
docker run -p 8001:8000 metar-backend:v1
```

### Environment Variables

```env
FRONTEND_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8001
```

### Health Check

```bash
# Check health endpoint (no auth required)
curl http://localhost:8001/health

# Call versioned endpoint (auth required)
curl -H "Authorization: Bearer <token>" \
  -X POST \
  -F "manual_text=METAR KJFK..." \
  http://localhost:8001/api/v1/convert
```

---

## Support

For issues with API versions:

1. Check [API Documentation](../docs/API.md)
2. Review error messages in response
3. Check coverage in [TEST_COVERAGE_README.md](./TEST_COVERAGE_README.md)
4. File GitHub issue with error details and endpoint

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Semantic Versioning](https://semver.org/)
- [REST API Best Practices](https://restfulapi.net/versioning/)
