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

## Architecture Overview

### Services

| Service | Port | Purpose | Tech |
|---------|------|---------|------|
| **Frontend** | 5173 (dev)<br>8000 (prod) | React web app | React + TypeScript + Vite |
| **Auth Service** | 8003 | Auth middleware proxy to Supabase | FastAPI + Python |
| **Backend API** | 8001 | METAR→IWXXM conversion | FastAPI + Python + GIFTs |
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
SUPABASE_PUBLICABLE_KEY=your-anon-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_ACCESS_TOKEN=your-access-token

# Frontend Configuration
VITE_APP_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8001
VITE_AUTH_SERVICE_URL=http://localhost:8003
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-anon-key

# Auth Service Configuration
FRONTEND_URL=http://localhost:5173
FRONTEND_BASE_URL=http://localhost:5173

# Database
DATABASE_URL=postgresql+psycopg2://postgres.PROJECT_REF:PASSWORD@aws-0-us-west-2.pooler.supabase.com:6543/postgres
DATABASE_PASSWORD=your-password

# Admin Account (for testing)
ADMIN_EMAIL=admin@metar.local
ADMIN_PASSWORD=<use .env file with secure password>

# Demo Mode
DEMO_MODE=true
```

### Service-Specific Configuration

**Auth Service** (`auth/.env`):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
FRONTEND_BASE_URL=http://localhost:5173
DATABASE_URL=postgresql+psycopg2://postgres.PROJECT_REF:PASSWORD@...
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
```

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
uv sync                  # Install deps
python -m src            # Runs on port 8001
```

**Key Files:**
- `src/api.py` - FastAPI endpoints
- `src/utilities/conversion.py` - METAR→IWXXM conversion
- `src/utilities/security.py` - JWT verification

**Endpoints:**
- `POST /api/convert` - Convert METAR strings to IWXXM XML
- `POST /api/convert/batch` - Batch conversion (returns ZIP)
- `GET /health` - Health check
- `/docs` - Interactive API documentation

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
cd frontend
npm run test:e2e         # Playwright E2E tests
```

---

## Troubleshooting

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
