# Environment Variables Reference

Complete reference of all environment variables for METAR-to-IWXXM backend deployment.

---

## Database & Connection

### `DATABASE_URL` (Required)

Connection string for PostgreSQL database.

| Setting | Value |
|---------|-------|
| **Format** | `postgresql+asyncpg://user:password@host:port/db` |
| **Example (Supabase)** | `postgresql+asyncpg://postgres:MyPassword123@db.abcdefg.supabase.co:5432/postgres` |
| **Example (RDS)** | `postgresql+asyncpg://admin:password@mydb.abc123.us-east-1.rds.amazonaws.com:5432/metar` |
| **Default** | None (required—must be set) |
| **Render Setup** | Set in Environment Variables section of Render dashboard |
| **Where to get it** | Supabase: Settings → Database → Connection string (Uvicorn) |

**Notes:**
- Without this, the app will fail to start
- Connection pooling is auto-configured (pool_size=10, max_overflow=20)
- Supabase uses `prepared_statement_cache_size=0` for compatibility

---

### `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

Individual database connection parameters (used if `DATABASE_URL` is not set).

| Variable | Example | Default |
|----------|---------|---------|
| `POSTGRES_HOST` | `db.supabase.co` | `localhost` |
| `POSTGRES_PORT` | `5432` | `5432` |
| `POSTGRES_DB` | `postgres` | `metar` |
| `POSTGRES_USER` | `postgres` | `postgres` |
| `POSTGRES_PASSWORD` | `SecurePass123` | None (required if using this set) |

**Notes:**
- Only used if `DATABASE_URL` is NOT set
- Not recommended for Render (use `DATABASE_URL` instead)

---

## Authentication

### `DISABLE_AUTH` 

Bypass authentication for all requests (for testing/development).

| Setting | Value |
|---------|-------|
| **Format** | Boolean: `true` or `false` |
| **Default** | `false` |
| **Example** | `DISABLE_AUTH=true` (skip auth validation) |
| **Render Setup** | Already set in `render.yaml`; don't change unless you have auth service ready |

**Important:**
- Set to `true` for initial Render testing
- Before production, set to `false` AND configure one of:
  - `AUTH_SERVICE_URL` (proxy-based auth)
  - `GITHUB_CLIENT_ID` + `GITHUB_CLIENT_SECRET` (OAuth)

---

### `AUTH_SERVICE_URL`

URL of the authentication service (if using proxy-based auth).

| Setting | Value |
|---------|-------|
| **Format** | Full URL: `https://auth-service.example.com` |
| **Example** | `https://auth-service.onrender.com` (if auth deployed on Render) |
| **Default** | `http://localhost:8003` |
| **Render Setup** | Set when deploying auth service |

**Example flow:**
1. Frontend sends request with Bearer token
2. Backend calls `{AUTH_SERVICE_URL}/auth/verify` with token
3. Auth service validates and returns user info
4. Backend proceeds or rejects

---

### `ADMIN_USER_ID`

Fallback admin user ID (used when `DISABLE_AUTH=true`).

| Setting | Value |
|---------|-------|
| **Format** | String (any identifier) |
| **Default** | `dev-user-12345` |
| **Example** | `admin@myorg.com` or `user-123` |
| **Render Setup** | Already set in `render.yaml` |

**Notes:**
- Only applies when `DISABLE_AUTH=true`
- Useful for local development and testing

---

### `ADMIN_EMAIL`

Fallback admin email (used when `DISABLE_AUTH=true`).

| Setting | Value |
|---------|-------|
| **Format** | Email address |
| **Default** | `dev@example.com` |
| **Example** | `admin@myorg.com` |
| **Render Setup** | Already set in `render.yaml` |

---

## CORS & Frontend Configuration

### `ALLOWED_ORIGINS` (or `FRONTEND_URL`)

CORS allowed origins for frontend requests.

| Setting | Value |
|---------|-------|
| **Format** | Comma-separated URLs or `*` |
| **Example (dev)** | `http://localhost:3000,http://localhost:5173` |
| **Example (prod)** | `https://metar-to-iwxxm.onrender.com` |
| **Default** | `*` (allow all—not recommended for production) |
| **Render Setup** | Override in Render dashboard Environment Variables |

**Important for Render:**
```
ALLOWED_ORIGINS=https://<your-frontend-domain>.com
```

**Examples:**
```env
# Local development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Production with Render front-end
ALLOWED_ORIGINS=https://metar-to-iwxxm.onrender.com

# Allow multiple domains
ALLOWED_ORIGINS=https://myapp.com,https://staging.myapp.com

# Testing (NOT SECURE for production)
ALLOWED_ORIGINS=*
```

---

### `ENABLE_DEV_CORS_RELAXATION`

Opt-in local debugging switch for difficult CORS preflight failures.

| Setting | Value |
|---------|-------|
| **Format** | Boolean (`true/false`, `1/0`, `yes/no`) |
| **Default** | `false` |
| **Effect when true** | Adds `http://localhost:5173` to allowed origins and sets `allow_headers=["*"]` |
| **Use case** | Local debugging of `OPTIONS /api/v1/convert` returning 400 |
| **Production** | Keep `false`; prefer explicit `ALLOWED_ORIGINS` |

**Example:**
```env
ENABLE_DEV_CORS_RELAXATION=true
```

---

## ICAO/WMO Configuration

### `TRANSLATION_CENTRE_NAME`

Name of your weather service organization.

| Setting | Value |
|---------|-------|
| **Format** | String |
| **Example** | `National Weather Service (NWS)` |
| **Default** | `METAR to IWXXM Translation Service` |
| **Use** | Appears in generated IWXXM XML metadata |

---

### `TRANSLATION_CENTRE_DESIGNATOR`

2-letter ICAO country/region designator.

| Setting | Value |
|---------|-------|
| **Format** | 2 uppercase letters |
| **Example** | `US` (USA), `CA` (Canada), `GB` (UK) |
| **Default** | `XX` |
| **Use** | IWXXM document metadata |

---

### `ICAO_LOCATION_INDICATOR`

4-letter ICAO aerodrome code (where translation happens).

| Setting | Value |
|---------|-------|
| **Format** | 4 uppercase letters |
| **Example** | `KJFK` (JFK), `EGLL` (Heathrow), `UUDD` (Moscow) |
| **Default** | `XXXX` |
| **Use** | IWXXM document metadata |

---

### `SERVICE_ONLINE_SINCE`

Date when this translation service became operational.

| Setting | Value |
|---------|-------|
| **Format** | ISO date: `YYYY-MM-DD` |
| **Example** | `2026-02-17` |
| **Default** | None |
| **Use** | IWXXM document metadata |

---

### `TECHNICAL_CONTACT_EMAIL`

Email for technical support/issues with translation service.

| Setting | Value |
|---------|-------|
| **Format** | Email address |
| **Example** | `support@weather.gov` |
| **Default** | None |
| **Use** | IWXXM document metadata |

---

## Validation & Processing

### `WMO_ONLINE_VALIDATION`

Enable online validation against WMO registry.

| Setting | Value |
|---------|-------|
| **Format** | Boolean: `true` or `false` |
| **Default** | `true` |
| **Example** | `WMO_ONLINE_VALIDATION=false` (offline mode) |
| **Render Setup** | Already set in `render.yaml` |

**Notes:**
- When `true`, validates against live WMO XML Registry
- When `false`, skips WMO validation (faster, less accurate)
- May fail if behind firewall or WMO service is down

---

### `WMO_VALIDATION_TIMEOUT`

Timeout (in seconds) for WMO validation requests.

| Setting | Value |
|---------|-------|
| **Format** | Integer (seconds) |
| **Default** | `5` |
| **Example** | `WMO_VALIDATION_TIMEOUT=10` (10-second timeout) |

---

### `WMO_REGISTRY_CACHE_TTL`

Cache time-to-live (in seconds) for WMO registry data.

| Setting | Value |
|---------|-------|
| **Format** | Integer (seconds) |
| **Default** | `86400` (24 hours) |
| **Example** | `WMO_REGISTRY_CACHE_TTL=3600` (1 hour) |

---

### `SCHEMATRON_USE_DOCKER`

Use Docker container with Java/Saxon XSLT2 processor for Schematron XML validation.

| Setting | Value |
|---------|-------|
| **Format** | Boolean: `true` or `false` |
| **Default** | `true` |
| **Production** | `true` for full ISO Schematron XSLT2 support |
| **Render** | `false` (no Docker-in-Docker on Render) |
| **Local Dev** | `true` (Docker available locally) |

**What Schematron Validation Does:**
- Validates IWXXM XML against WMO/ISO business rules
- Checks semantic constraints that XSD alone can't enforce
- Requires Saxon XSLT2 processor (runs inside Docker)
- Optional step in validation chain (doesn't block if disabled)

**When to disable (`false`):**
- Render deployment (no Docker-in-Docker support)
- Faster validation (skips XSLT2 compilation step, ~2-5 second savings per request)
- Limited resources (Docker startup overhead saved)

**When to enable (`true`):**
- Local development (Docker desktop available)
- Production with full WMO compliance requirements
- Post-deployment if you add separate Schematron microservice

**Render Note:**
- Already set to `false` in [render.yaml](../render.yaml)
- Pure Python lxml validation still active (catches ~80% of business rule violations)
- Trade-off: faster deployment vs. some XSLT2-specific rule checks
- Future path: Deploy dedicated Schematron HTTP service when needed

**What still works when disabled:**
- ✅ METAR input parsing and content validation
- ✅ IWXXM XML generation
- ✅ XSD schema validation (well-formedness, structure)
- ✅ WMO codelist validation (via RDF cache)
- ✅ GML reference validation

**What's skipped when disabled:**
- ⚠️ Advanced ISO Schematron business rules (requires XSLT2)
- ⚠️ XSLT2-specific constraint checking (Saxon/Java)

---

## Statistics & Webhooks

### `ENABLE_STATISTICS`

Collect translation statistics (stored in database).

| Setting | Value |
|---------|-------|
| **Format** | Boolean: `true` or `false` |
| **Default** | `true` |
| **Example** | `ENABLE_STATISTICS=false` (disable tracking) |

**Collected stats:**
- Number of translations
- Success/failure rates
- Processing times

---

### `ENABLE_WEBHOOKS`

Enable outbound webhooks on translation events.

| Setting | Value |
|---------|-------|
| **Format** | Boolean: `true` or `false` |
| **Default** | `false` |
| **Example** | `ENABLE_WEBHOOKS=true` |

---

### `WEBHOOK_URLS`

Comma-separated list of webhook URLs to POST on translation.

| Setting | Value |
|---------|-------|
| **Format** | Comma-separated HTTPS URLs |
| **Example** | `https://myapi.com/webhook,https://analytics.com/events` |
| **Default** | None |
| **Note** | Only used if `ENABLE_WEBHOOKS=true` |

---

### `WEBHOOK_SECRET`

Secret key for HMAC signing of webhook payloads.

| Setting | Value |
|---------|-------|
| **Format** | String (random, >= 32 characters recommended) |
| **Example** | `sk_webhook_abc123xyz...` |
| **Default** | None |
| **Note** | Use for validating webhook authenticity |

---

## Application Runtime

### `PORT`

HTTP server port.

| Setting | Value |
|---------|-------|
| **Format** | Integer (1-65535) |
| **Default** | `8001` |
| **Render** | Automatically set to `$PORT` (injected by Render) |
| **Example** | `PORT=8000` |

**Note:** In Render, use `$PORT` in start command; app auto-detects.

---

### `HOST`

HTTP server bind address.

| Setting | Value |
|---------|-------|
| **Format** | IP address or hostname |
| **Default** | `0.0.0.0` (all interfaces) |
| **Example** | `HOST=127.0.0.1` (localhost only) |
| **Render** | Leave as default (`0.0.0.0`) |

---

### `RELOAD`

Enable code reload on file changes (Uvicorn dev feature).

| Setting | Value |
|---------|-------|
| **Format** | Boolean: `true` or `false` |
| **Default** | `true` |
| **Render Setup** | Set to `false` in `render.yaml` (already configured) |
| **Notes** | Disable in production for faster startup; enable in dev |

---

### `LOG_LEVEL`

Logging verbosity.

| Setting | Value |
|---------|-------|
| **Format** | String: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| **Default** | `INFO` |
| **Example** | `LOG_LEVEL=DEBUG` (verbose logs) |
| **Render Setup** | Already set to `INFO` in `render.yaml` |

---

## Sentry (Error Tracking) — Optional

### `SENTRY_DSN`

Sentry error tracking endpoint.

| Setting | Value |
|---------|-------|
| **Format** | Sentry DSN URL |
| **Example** | `https://key@sentry.io/123456` |
| **Default** | None (Sentry disabled if not set) |
| **Setup** | Create project at https://sentry.io, copy DSN |

**Example in Render:**
```
SENTRY_DSN=https://abc123def456@o12345.ingest.sentry.io/6789012
```

---

## Quick Setup for Render

For a basic Render deployment, you only need:

```env
# [REQUIRED]
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@db.supabase.co:5432/postgres

# [OPTIONAL - recommended]
ALLOWED_ORIGINS=https://my-frontend.onrender.com
TRANSLATION_CENTRE_NAME=My Weather Service
TRANSLATION_CENTRE_DESIGNATOR=XX
ICAO_LOCATION_INDICATOR=XXXX
SERVICE_ONLINE_SINCE=2026-02-17
TECHNICAL_CONTACT_EMAIL=support@example.com

# [OPTIONAL - error tracking]
SENTRY_DSN=https://...
```

All other variables are already set in `render.yaml` with sensible defaults.

---

## For Local Development (with Docker Compose)

Create a `.env` file in the repo root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/metar

# Auth (local dev)
DISABLE_AUTH=true
ADMIN_USER_ID=dev-user
ADMIN_EMAIL=dev@example.com
AUTH_SERVICE_URL=http://localhost:8003

# Frontend
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# ICAO
TRANSLATION_CENTRE_NAME=Local Dev Service
TRANSLATION_CENTRE_DESIGNATOR=XX
ICAO_LOCATION_INDICATOR=KTEST

# App
PORT=8001
HOST=0.0.0.0
RELOAD=true
LOG_LEVEL=DEBUG

# Validation
SCHEMATRON_USE_DOCKER=true
WMO_ONLINE_VALIDATION=false

# Metrics
ENABLE_STATISTICS=true
ENABLE_WEBHOOKS=false
```

---

## Validation

Check that environment variables are working:

```bash
# In Render logs or local terminal
curl http://localhost:8001/health

# Should return:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "gifts_available": true
# }
```

If `/health` returns errors related to environment variables, check Render logs for detailed error messages.

---

## References

- **Full Deployment Guide:** [docs/RENDER_DEPLOYMENT.md](../docs/RENDER_DEPLOYMENT.md)
- **Render.yaml:** [render.yaml](../render.yaml)
- **Backend Code:** [backend/src/config.py](../backend/src/config.py) (where env vars are read)
- **Docker Compose Example:** [docker-compose.yml](../docker-compose.yml)
