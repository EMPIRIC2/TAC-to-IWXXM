# Development Guide - METAR to IWXXM

Complete guide for setting up, developing, and deploying the METAR to IWXXM converter.

## Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose (recommended)
- Or: Python 3.11+, Node.js 18+, uv package manager
- Git with submodules support

### Fastest Setup with Docker

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>
cd metar-to-IWXXM

# Create environment file with Supabase credentials
cp .env.example .env
# Edit .env with your Supabase credentials (see Configuration section)

# Start all services
docker-compose up --build

# Services ready at:
# - Frontend: http://localhost:5173 (dev) or 8000 (prod)
# - Backend API: http://localhost:8001/docs
# - Auth Service: http://localhost:8003
```

### Manual Setup (Development)

```bash
# 1. Install auth service
cd auth
uv sync && uv run uvicorn src.__main__:app --reload --port 8003 --host 0.0.0.0

# 2. In another terminal, install backend
cd backend
uv sync && python -m src  # Runs on port 8001

# 3. In another terminal, install frontend
cd frontend
npm install && npm run dev  # Runs on port 5173

# 4. Update .env with Supabase credentials
```

---

## Current CI/CD Status

Primary workflow: `.github/workflows/ci-cd.yml`

- Runs test + coverage jobs for `backend`, `auth`, `GIFTs`, and `frontend`
- Uploads coverage reports to Codecov with per-service flags
- Enforces per-service Codecov gates at 75% via `.codecov.yml`
- Builds and pushes Docker images on `main` after required test jobs pass

### Coverage policy (current)

- `backend`: 75%
- `auth`: 75%
- `frontend`: 75%
- `gifts`: 75%

### Submodule reliability policy

`GIFTs` must use non-shallow submodule initialization in CI. If checkout issues occur (`not our ref`, `did not contain <sha>`), use:

```bash
git submodule sync --recursive
git submodule update --init GIFTs
git -C GIFTs fetch --tags --force origin
git submodule update --init GIFTs
git submodule status GIFTs
```

---

## Architecture Overview

### Services

| Service | Port | Purpose | Tech |
|---------|------|---------|------|
| **Frontend** | 5173 (dev)<br>8000 (prod) | React web app | React + TypeScript + Vite |
| **Auth Service** | 8003 | Auth middleware proxy to Supabase | FastAPI + Python + SQLAlchemy 2.0 |
| **Backend API** | 8001 | METAR→IWXXM conversion | FastAPI + Python + SQLAlchemy 2.0 + GIFTs |
| **Supabase** | Remote | Database + Auth | PostgreSQL + Auth |

### Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (React)                                            │
│ ├─ user registers/logs in                                  │
│ └─ stores session token                                    │
└────────────────┬────────────────────────────────────────────┘
                 │ POST /auth/login
                 ↓
         ┌───────────────────────┐
         │ Auth Service (8003)   │
         │ ├─ CORS enabled       │
         │ └─ Log auth requests  │
         └────────────┬──────────┘
                      │ Proxy to Supabase
                      ↓
         ┌───────────────────────┐
         │ Supabase Auth         │
         │ ├─ Email verification │
         │ └─ JWT issuance       │
         └────────────┬──────────┘
                      │ JWT tokens
                      ↓
         ┌───────────────────────┐
         │ Frontend (localStorage) │
         └────────────┬──────────┘
                      │ GET /api/convert
                      │ Header: Authorization: Bearer <token>
                      ↓
         ┌───────────────────────┐
         │ Backend (8001)        │
         │ ├─ Verify token via   │
         │ │  auth service       │
         │ └─ Convert METAR      │
         └───────────────────────┘
```

---

## Configuration

### Environment Variables

**Root `.env` file** (`.env.example` provided):

```bash
# Supabase Credentials (from Dashboard → Settings → API)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-publishable-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_ACCESS_TOKEN=your-access-token

# Frontend Configuration
VITE_APP_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8001
VITE_AUTH_SERVICE_URL=http://localhost:8003
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-publishable-key

# Auth Service Configuration
FRONTEND_URL=http://localhost:5173
FRONTEND_BASE_URL=http://localhost:5173

# Database (Supabase PostgreSQL transaction pooler - IPv4 compatible)
# ✓ Uses SQLAlchemy 2.0 for both auth service and backend
# From Supabase dashboard: Settings → Database → Connection pooling → Transaction mode
# Port: 6543 (transaction mode) or 5432 (session mode)
DATABASE_URL=postgresql+psycopg2://postgres.YOUR_PROJECT_REF:YOUR_DATABASE_PASSWORD@aws-0-us-west-2.pooler.supabase.com:6543/postgres
DATABASE_PASSWORD=your-secure-password

# Admin Account (for testing -- use strong password)
ADMIN_EMAIL=admin@metar.local
ADMIN_PASSWORD=your-secure-admin-password

# Demo Mode
DEMO_MODE=true
```

### Service-Specific Configuration

**Auth Service** (`auth/.env`):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
FRONTEND_BASE_URL=http://localhost:5173
# Auth service uses SQLAlchemy with psycopg2 dialect
DATABASE_URL=postgresql+psycopg2://postgres.PROJECT_REF:PASSWORD@aws-0-us-west-2.pooler.supabase.com:6543/postgres
```

**Frontend** (`frontend/.env`):
```bash
VITE_AUTH_SERVICE_URL=http://localhost:8003
VITE_BACKEND_URL=http://localhost:8001
VITE_APP_URL=http://localhost:5173
```

**Backend** (`backend/.env`):
```bash
AUTH_SERVICE_URL=http://localhost:8003
SUPABASE_URL=https://your-project.supabase.co
# Backend uses SQLAlchemy 2.0 AsyncSession with psycopg async driver
# URL format: postgresql+asyncpg:// for async operations
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@aws-0-us-west-2.pooler.supabase.com:6543/postgres
```

**Note on DATABASE_URL format**:
- If you have a URL with `postgresql+psycopg2://` scheme (from Supabase docs), the backend will automatically convert it to `postgresql+asyncpg://` for async operations
- Both auth service (SQLAlchemy with psycopg2) and backend (SQLAlchemy with asyncpg) use the same unified ORM layer

---

## Service Details

### Frontend (React + Vite)

**Location:** `/frontend`

**Get Started:**
```bash
cd frontend
npm install
npm run dev          # Start dev server on port 5173
npm run build        # Production build
npm run test         # Run tests
npm run test:coverage # Coverage report
```

**Key Files:**
- `src/app/App.tsx` - Main component
- `src/utils/authService.ts` - Auth client library
- `src/app/components/auth/` - Login/Register/PasswordReset components

**Build Process:**
- Vite-based with TypeScript
- Tailwind CSS for styling
- Vitest + Playwright for testing
- Runs on `http://localhost:5173` (dev) or `http://localhost:8000` (prod)

---

### Auth Service (FastAPI)

**Location:** `/auth`

**Get Started:**
```bash
cd auth
uv sync                                              # Install deps
uv run uvicorn src.__main__:app --reload --port 8003
```

**Key Files:**
- `src/__main__.py` - FastAPI entry point with CORS middleware
- `src/api_supabase.py` - Auth endpoints
- `src/supabase_proxy.py` - Supabase client wrapper

**Endpoints:**
- `POST /auth/register` - Create account
- `POST /auth/login` - Login (returns JWT)
- `GET /auth/me` - Get current user
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Logout
- `POST /auth/password-reset/request` - Request reset
- `POST /auth/password-reset/confirm` - Confirm reset
- `GET /auth/verify` - Verify token (backend use)
- `GET /health` - Health check

**Testing:**
```bash
pytest tests/                    # Run all tests
pytest --cov=src --cov-report=html  # Coverage report
```

---

### Backend API (FastAPI)

**Location:** `/backend`

**Get Started:**
```bash
cd backend
uv sync                  # Install deps (includes SQLAlchemy 2.0 + psycopg[binary])
python -m src            # Runs on port 8001
```

**Key Files:**
- `src/api.py` - FastAPI endpoints
- `src/services/database.py` - SQLAlchemy async engine and session management
- `src/services/statistics.py` - Translation statistics with SQLAlchemy ORM
- `src/models.py` - SQLAlchemy ORM models
- `src/utilities/conversion.py` - METAR→IWXXM conversion
- `src/utilities/security.py` - JWT verification

**Endpoints:**
- `POST /api/convert` - Convert METAR strings to IWXXM XML
- `POST /api/convert/batch` - Batch conversion (returns ZIP)
- `GET /health` - Health check
- `/docs` - Interactive API documentation

**Database:**
The backend uses SQLAlchemy 2.0 with async support:
- Async engine with connection pooling
- Support for both sync and async operations
- Prepared statement caching disabled for Supabase transaction pooler compatibility
- ORM models in `src/models.py` for type safety and query building

**Testing:**
```bash
pytest tests/                    # Run 230+ tests
pytest --cov=src --cov-report=html  # 65% coverage
```

---

## Testing

### Frontend Tests
```bash
cd frontend
npm run test              # Watch mode
npm run test:coverage    # Coverage report
```

### Backend Tests
```bash
cd backend
pytest tests/
pytest --cov=src --cov-report=html
```

### Auth Service Tests
```bash
cd auth
pytest tests/
pytest --cov=src --cov-report=html
```

### Integration Tests
```bash
# Playwright browser E2E — full suite (requires admin credentials)
make test-e2e-playwright

# Credential-free smoke subset (safe for CI / local dev without secrets)
make test-e2e-playwright-smoke

# Equivalent direct command (full suite)
cd frontend && npx playwright test
```

Playwright browser E2E specs are located in the repository-level `tests/` directory (`*.e2e.spec.ts`).
The Playwright runner starts all required local services through `start-dev-servers.sh` for full-stack coverage.

#### Test suites

| Target | Admin credentials | Tests |
|---|---|---|
| `test-e2e-playwright` | Required | All 21 tests (login flows, admin nav, file upload) |
| `test-e2e-playwright-smoke` | **Not required** | 9 tests: service health, auth integration, mocked conversions |

`tests/00-preflight.e2e.spec.ts` sorts first alphabetically and runs before any login-dependent
spec file.  When credentials are missing or wrong it fails immediately with a single descriptive
message rather than producing 12+ repeated timeout failures from every test that calls
`loginAsAdmin`.

### Playwright E2E Environment Controls

- `PLAYWRIGHT_ADMIN_EMAIL`, `PLAYWRIGHT_ADMIN_PASSWORD`: required for admin authentication flows.
- `PLAYWRIGHT_TAC_FIXTURES_DIR`: override TAC fixture location for upload tests.
- `PLAYWRIGHT_REQUIRE_TAC_FIXTURES=1`: fail fast if TAC fixtures are unavailable (default on CI).
- `PLAYWRIGHT_SERVICE_WAIT_TIMEOUT_MS`: startup service health wait timeout in milliseconds.
- `PLAYWRIGHT_FRONTEND_HEALTH_URL`, `PLAYWRIGHT_BACKEND_HEALTH_URL`, `PLAYWRIGHT_AUTH_HEALTH_URL`: optional health endpoint overrides.
- `PLAYWRIGHT_FORCE_SERVICE_HEALTH_WAIT=1`: force health checks for non-local base URLs.
- `PLAYWRIGHT_SKIP_LOCAL_HEALTH_WAIT=1`: disable startup health checks.

Example:

```bash
cd frontend
export PLAYWRIGHT_ADMIN_EMAIL="admin@example.com"
export PLAYWRIGHT_ADMIN_PASSWORD="<password>"
export PLAYWRIGHT_REQUIRE_TAC_FIXTURES=1
export PLAYWRIGHT_SERVICE_WAIT_TIMEOUT_MS=180000
npx playwright test
```

---

## Troubleshooting

### Git submodule failures

Symptoms in CI:

- `fatal: Fetched in submodule path 'GIFTs', but it did not contain <sha>`
- `remote error: upload-pack: not our ref <sha>`

Recovery:

```bash
git submodule sync --recursive
git submodule update --init GIFTs
git -C GIFTs fetch --tags --force origin
git submodule update --init GIFTs
```

### "Failed to fetch" errors
- **Check**: Is auth service running on port 8003?
  ```bash
  curl http://localhost:8003/health
  ```
- **Check**: CORS configuration in `auth/src/__main__.py`
- **Check**: Frontend `.env` has correct `VITE_AUTH_SERVICE_URL`

### Auth service won't start
- **Check**: Port 8003 is available
  ```bash
  lsof -i :8003
  ```
- **Check**: `.env` has `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- **Check**: Database URL is correct (IPv4 pooler recommended)

### Backend can't verify tokens
- **Check**: Auth service is running on port 8003
- **Check**: Backend `.env` has correct `AUTH_SERVICE_URL`
- **Verify**:
  ```bash
  curl -X POST http://localhost:8003/auth/verify \
    -H "Authorization: Bearer <token>"
  ```

### Frontend blank page
- **Check**: `FRONTEND_URL` in `.env` matches running port (5173 for dev)
- **Check**: Frontend `.env` has all required variables
- **Check**: Browser console (F12) for JavaScript errors

---

## Deployment

### Docker Compose (Recommended)
```bash
# Development
docker-compose up --build

# Production (see docker-compose.prod.yml if available)
docker-compose -f docker-compose.yml up -d
```

### Manual Deployment

**Frontend:**
```bash
cd frontend
npm run build     # Creates dist/
# Serve with nginx or static host
```

**Backend & Auth Service:**
```bash
# Use gunicorn or similar
gunicorn src.api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Environment Setup:**
- Use Docker secrets or environment variables (never hardcoded `.env`)
- Set strong `AUTH_JWT_SECRET` in production
- Enable SSL/TLS for all services
- Use Supabase's Session Pooler (port 5432) for stability

---

## Documentation

- [API Reference](./docs/API.md) - Full API endpoint documentation
- [Auth Architecture](./docs/AUTH_MIDDLEWARE_ARCHITECTURE.md) - How auth works
- [Supabase Integration](./docs/SUPABASE_INTEGRATION.md) - Database setup
- [Email Templates](./docs/SUPABASE_EMAIL_TEMPLATES.md) - Email configuration

---

## Help & Support

**Logs:**
```bash
# Auth service logs
docker logs metar-to-iwxxm-auth-1

# Backend logs
docker logs metar-to-iwxxm-backend-1

# Frontend console (in browser F12)
```

**Health Checks:**
```bash
curl http://localhost:8003/health  # Auth
curl http://localhost:8001/health  # Backend
curl http://localhost:5173         # Frontend (should return HTML)
```

---

## Security Notes

- ✅ Never commit `.env` files (use `.env.example`)
- ✅ Store secrets in environment variables, not hardcoded
- ✅ Supabase credentials never exposed to frontend
- ✅ Use strong JWT secrets in production
- ✅ Enable SSL/TLS
- ✅ Regular dependency updates
