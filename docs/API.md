# API Documentation

## Overview

The METAR to IWXXM Converter API provides endpoints for converting METAR/SPECI TAC messages to IWXXM XML format.

**Base URL**: `http://localhost:8000`  
**Version**: 0.1.0  
**Interactive Docs**: Visit `/docs` (Swagger UI) or `/redoc` (ReDoc)

## Endpoints

### Health Check

```
GET /health
```

Check service health and GIFTs library availability.

**Response** (`HealthResponse`):
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "gifts_available": true
}
```

---

### Convert METAR to IWXXM

```
POST /api/convert
```

Convert uploaded METAR TAC files and/or manual text to IWXXM XML.

**Request** (multipart/form-data):
- `files` (optional): One or more METAR TAC files
- `manual_text` (optional): Manual METAR/SPECI TAC text

**Response** (`ConversionResponse`):
```json
{
  "results": [
    {
      "name": "manual_input.txt",
      "content": "<?xml version='1.0' encoding='utf-8'?><iwxxm:METAR...>",
      "source": "manual",
      "size_bytes": 1452
    }
  ],
  "errors": [],
  "total_processed": 1,
  "successful": 1,
  "failed": 0
}
```

**Examples**:

```bash
# Manual text input
curl -X POST http://localhost:8000/api/convert \
     -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"

# File upload
curl -X POST http://localhost:8000/api/convert \
     -F "files=@metar1.tac" \
     -F "files=@metar2.tac"

# Combined
curl -X POST http://localhost:8000/api/convert \
     -F "files=@metar.tac" \
     -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
```

---

### Convert to ZIP Archive

```
POST /api/convert-zip
```

Convert inputs and stream a ZIP archive of IWXXM XML outputs.

**Request** (multipart/form-data):
- `files` (optional): One or more METAR TAC files
- `manual_text` (optional): Manual METAR/SPECI TAC text

**Response**: `application/zip`
- Filename: `iwxxm_batch_YYYYMMDDTHHMMSSz.zip`
- Contains: `*.xml` files + optional `errors.txt`

**Example**:

```bash
curl -X POST http://localhost:8000/api/convert-zip \
     -F "files=@metar1.tac" \
     -F "files=@metar2.tac" \
     -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005" \
     -o iwxxm_batch.zip
```

---

## Data Models

### ConversionResult

A single conversion result from METAR TAC to IWXXM XML.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Output filename (e.g., "manual_input.txt", "KJFK.txt") |
| `content` | string | IWXXM XML document as UTF-8 text |
| `source` | string? | Source of input: "manual", "file", or filename |
| `size_bytes` | integer? | Size of XML output in bytes |

### ConversionResponse

Response from `/api/convert` containing results and errors.

| Field | Type | Description |
|-------|------|-------------|
| `results` | ConversionResult[] | Successfully converted IWXXM XML documents |
| `errors` | string[] | Error messages for failed conversions |
| `total_processed` | integer | Total number of inputs processed |
| `successful` | integer | Number of successful conversions |
| `failed` | integer | Number of failed conversions |

### ErrorDetail

Detailed error response for failed requests (HTTP 400).

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | High-level error message |
| `errors` | string[] | Detailed error messages for each failure |
| `total_errors` | integer | Total number of errors encountered |

### HealthResponse

Health check response.

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Service health status ("healthy" or "degraded") |
| `version` | string | API version |
| `gifts_available` | boolean | Whether GIFTs submodule is properly loaded |

---

## Error Handling

### 400 Bad Request

Returned when all conversions fail or no valid input is provided.

```json
{
  "detail": {
    "message": "All conversions failed",
    "errors": [
      "empty.tac: empty file",
      "invalid.tac: Decoding/encoding error: ..."
    ],
    "total_errors": 2
  }
}
```

### 500 Internal Server Error

Returned for unexpected server errors.

---

## Tags

- **Health**: Health check endpoints
- **Conversion**: METAR to IWXXM conversion endpoints

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

These interfaces allow you to:
- Explore all endpoints with detailed schemas
- Try out API calls directly in the browser
- View request/response examples
- Download OpenAPI specification

---

## Response Validation

All responses are validated using Pydantic models, ensuring:
- Type safety and correctness
- Automatic OpenAPI schema generation
- Rich IDE autocomplete support
- Runtime validation of all fields

---

## Client Libraries

Since this API follows OpenAPI 3.0 specification, you can generate client libraries for various languages:

```bash
# Download OpenAPI spec
curl http://localhost:8000/openapi.json > openapi.json

# Generate Python client (example using openapi-generator)
openapi-generator-cli generate -i openapi.json -g python -o ./client
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployments, consider adding:
- Rate limiting middleware
- API key authentication
- Request size limits
