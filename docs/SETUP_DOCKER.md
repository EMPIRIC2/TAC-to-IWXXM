# Docker Compose Setup Guide

## Quick Start

### Development Mode (No Auth Required)

```bash
# Copy the environment template
cp .env.example .env

# Start all services with auth disabled (development)
DISABLE_AUTH=true docker-compose up --build
```

Access the application at:
- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:8001
- **Auth Service**: http://localhost:8002
- **API Docs**: http://localhost:8001/docs

### Production Mode (With Supabase)

1. **Set up your `.env` file with valid Supabase credentials:**
```bash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-anon-key
```

2. **Start the services:**
```bash
# Without DISABLE_AUTH, backend will authenticate via Supabase
docker-compose up --build
```

## Services Overview

| Service | Port | Role | Technology |
|---------|------|------|-----------|
| **Auth** | 8002 | Authentication proxy to Supabase | Python 3.12 + FastAPI |
| **Backend** | 8001 | METAR-to-IWXXM conversion API | Python 3.12 + FastAPI + GIFTs |
| **Frontend** | 8000 | Web UI for conversions | Node.js + React + Nginx |

## Environment Variables

### Required (Production)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `VITE_SUPABASE_URL` - Frontend Supabase URL
- `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` - Frontend Supabase key

### Optional (Defaults provided)
- `DISABLE_AUTH` - Set to `true` for development (no Supabase required)
- `VITE_APP_URL` - Frontend app URL (default: http://localhost:8000)
- `VITE_BACKEND_URL` - Backend API URL (default: http://localhost:8001)
- `VITE_AUTH_URL` - Auth service URL (default: http://localhost:8002)
- `FRONTEND_BASE_URL` - Base URL for auth service callbacks (default: http://localhost:8000)

## Common Commands

```bash
# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Remove all data and containers
docker-compose down -v

# Rebuild images
docker-compose up --build

# Run specific service
docker-compose up backend
```

## Troubleshooting

### Backend returns 503 Service Unavailable
**Cause**: Auth service is unreachable or auth credentials are invalid.

**Solutions**:
1. **Development**: Use `DISABLE_AUTH=true docker-compose up`
2. **Production**: Verify Supabase credentials in `.env`
3. Check auth service logs: `docker-compose logs auth`

### Frontend can't reach backend
**Cause**: VITE_BACKEND_URL in frontend build args doesn't match backend service.

**Fix**: Ensure `VITE_BACKEND_URL=http://backend:8000` (internal) or `http://localhost:8001` (external)

### Health checks failing
**Cause**: Services take too long to start or health endpoints are failing.

**Debug**:
```bash
# Check service health
docker-compose ps

# View service logs
docker-compose logs backend  # or auth, frontend
```

## Development vs Production

### Development Mode
- **Use**: `DISABLE_AUTH=true`
- **Settings**: Auth bypassed, local defaults
- **Good for**: Testing, local development, debugging

### Production Mode
- **Use**: Valid Supabase credentials in `.env`
- **Settings**: Full authentication enabled
- **Good for**: Production deployments

## Architecture

```
┌─────────────────────────────────────────────────┐
│               Frontend (Nginx)                   │
│  Port 8000 → React SPA + METAR converter UI   │
└──────────────────┬──────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
    ┌──────────────┐    ┌──────────────┐
    │   Backend    │    │     Auth     │
    │  Port 8001   │    │  Port 8002   │
    │ + GIFTs Lib  │    │ + Supabase   │
    │              │    │              │
    │ Converts     │    │ Verifies JWT │
    │ METAR → XML  │    │ via Supabase │
    └──────────────┘    └──────────────┘
```

## Files Structure

```
.
├── docker-compose.yml     # Docker orchestration
├── .env.example           # Environment variables template
├── auth/
│   └── Dockerfile         # Auth service image
├── backend/
│   └── Dockerfile         # Backend API image
├── frontend/
│   └── Dockerfile         # Frontend image
└── GIFTs/                 # METAR encoding library
```

## Notes

- All services run in the `metar-network` bridge network for inter-service communication
- Healthchecks validated every 30 seconds with 10s timeout
- Services auto-restart unless stopped
- Auth data persists in `auth-data` volume (development)
