# Render Deployment Checklist

Quick checklist for the current 3-service Render deployment.

## Pre-Deployment

- [ ] `render.yaml` is committed to `main`
- [ ] Render account connected to GitHub repo
- [ ] Backend secret ready: `DATABASE_URL`
- [ ] Auth secrets ready: `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- [ ] Frontend secrets ready: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`

## Create Services

- [ ] Render Dashboard → **New** → **Blueprint**
- [ ] Select repo `joseph-c-mcguire/metar-to-IWXXM`
- [ ] Confirm 3 services are detected:
  - [ ] `metar-to-iwxxm-api` (web)
  - [ ] `metar-to-iwxxm-auth` (web)
  - [ ] `metar-to-iwxxm-frontend` (static_site)

## Validate Build/Start Settings

### Backend (`metar-to-iwxxm-api`)
- [ ] Root dir is `backend`
- [ ] Start command is `uvicorn src.api:app --host 0.0.0.0 --port ${PORT}`
- [ ] Health path is `/health`

### Auth (`metar-to-iwxxm-auth`)
- [ ] Root dir is `auth`
- [ ] Start command is `uvicorn auth.__main__:app --host 0.0.0.0 --port ${PORT}`
- [ ] Health path is `/health`

### Frontend (`metar-to-iwxxm-frontend`)
- [ ] Root dir is `frontend`
- [ ] Build command is `npm ci && npm run build`
- [ ] Publish dir is `dist`

## Configure Env Vars

### Backend
- [ ] `DATABASE_URL` set
- [ ] `ALLOWED_ORIGINS` matches frontend URL

### Auth
- [ ] `SUPABASE_URL` set
- [ ] `SUPABASE_ANON_KEY` set
- [ ] `FRONTEND_BASE_URL` points to deployed frontend URL

### Frontend
- [ ] `VITE_SUPABASE_URL` set
- [ ] `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` set

## Deploy + Verify

- [ ] Deploy all services
- [ ] Backend health passes:
  - [ ] `curl https://metar-to-iwxxm-api.onrender.com/health`
- [ ] Auth health passes:
  - [ ] `curl https://metar-to-iwxxm-auth.onrender.com/health`
- [ ] Frontend opens:
  - [ ] `https://metar-to-iwxxm-frontend.onrender.com`
- [ ] Browser shows no CORS errors during auth/API calls

## Post-Deploy

- [ ] Keep `DISABLE_AUTH=true` for initial smoke tests
- [ ] Plan auth hardening rollout (`DISABLE_AUTH=false`) after validation
- [ ] Add monitoring/alerts (Render notifications, optional Sentry)
