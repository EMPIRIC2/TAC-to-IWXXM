# Deploying to Render (Backend + Auth + Frontend)

For observability stack setup (Grafana + Prometheus + Loki), see `docs/RENDER_OBSERVABILITY.md`.

This guide covers the current `render.yaml` topology:

- `metar-to-iwxxm-api` (Web Service, FastAPI backend)
- `metar-to-iwxxm-auth` (Web Service, FastAPI auth proxy)
- `metar-to-iwxxm-frontend` (Static Site, Vite build)

## Prerequisites

- Render account with GitHub integration
- Access to this repository
- Supabase project (for auth service):
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
- PostgreSQL connection string for backend:
  - `DATABASE_URL=postgresql+asyncpg://...`

## Step 1: Confirm `render.yaml` is in repo root

```bash
git add render.yaml
git commit -m "Update Render blueprint"
git push origin main
```

## Step 2: Create services from Blueprint

1. Go to Render Dashboard.
2. Click **New** → **Blueprint**.
3. Select this GitHub repo and branch `main`.
4. Render will detect all 3 services from `render.yaml`.

## Step 3: Required environment variables

Set the following in Render dashboard before first successful deployment.

### Backend (`metar-to-iwxxm-api`)

Required:

- `DATABASE_URL`

Recommended override:

- `ALLOWED_ORIGINS=https://<your-frontend-domain>.onrender.com`

Already set in `render.yaml`:

- `DISABLE_AUTH=true`
- `AUTH_SERVICE_URL=https://metar-to-iwxxm-auth.onrender.com`
- `SCHEMATRON_USE_DOCKER=false`
- `WMO_ONLINE_VALIDATION=true`

### Auth (`metar-to-iwxxm-auth`)

Required:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

Already set in `render.yaml`:

- `FRONTEND_BASE_URL=https://metar-to-iwxxm-frontend.onrender.com`
- `CORS_ORIGINS=https://metar-to-iwxxm-frontend.onrender.com`

### Frontend (`metar-to-iwxxm-frontend`)

Required:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`

Already set in `render.yaml`:

- `VITE_APP_URL=https://metar-to-iwxxm-frontend.onrender.com`
- `VITE_BACKEND_URL=https://metar-to-iwxxm-api.onrender.com`
- `VITE_AUTH_SERVICE_URL=https://metar-to-iwxxm-auth.onrender.com`

## Step 4: Build/start configuration reference

### Backend

- Root dir: `backend`
- Build:

```bash
pip install --upgrade pip && pip install . && pip install ../GIFTs
```

- Start:

```bash
uvicorn src.api:app --host 0.0.0.0 --port ${PORT}
```

- Health check: `/health`

### Auth

- Root dir: `auth`
- Build:

```bash
pip install --upgrade pip && pip install .
```

- Start:

```bash
uvicorn auth.__main__:app --host 0.0.0.0 --port ${PORT}
```

- Health check: `/health`

### Frontend

- Root dir: `frontend`
- Build:

```bash
npm ci && npm run build
```

- Publish directory: `dist`

## Step 5: Verify deployment

1. Backend health:

```bash
curl https://metar-to-iwxxm-api.onrender.com/health
```

2. Auth health:

```bash
curl https://metar-to-iwxxm-auth.onrender.com/health
```

3. Frontend loads:

- Open `https://metar-to-iwxxm-frontend.onrender.com`

4. Confirm no browser CORS errors for calls from frontend to auth/backend.

## Notes

- `DISABLE_AUTH=true` keeps backend auth bypass enabled for initial rollout.
- To enforce auth later, set backend `DISABLE_AUTH=false` and ensure auth service remains healthy.
- `SCHEMATRON_USE_DOCKER=false` is intentional on Render due to Docker-in-Docker limits.

## Common issues

### Backend fails on startup

- Usually missing/invalid `DATABASE_URL`.

### Auth returns startup error

- Usually missing `SUPABASE_URL` or `SUPABASE_ANON_KEY`.

### Frontend auth links redirect to localhost

- Ensure auth `FRONTEND_BASE_URL` points to deployed frontend URL.

### Browser CORS errors

- Ensure backend `ALLOWED_ORIGINS` and auth `CORS_ORIGINS` include the exact frontend origin.
