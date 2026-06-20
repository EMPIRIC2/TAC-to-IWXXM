# Render Deployment Index

Current Render deployment is a 3-service blueprint defined in `render.yaml`.

## Services

- `metar-to-iwxxm-api` (web, backend)
- `metar-to-iwxxm-auth` (web, auth proxy)
- `metar-to-iwxxm-frontend` (static site)

## Primary Docs

- Deployment guide: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
- Deployment checklist: [RENDER_CHECKLIST.md](./RENDER_CHECKLIST.md)
- Verification guide: [RENDER_VERIFICATION.md](./RENDER_VERIFICATION.md)
- Environment variables: [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)

## Required Secrets by Service

### Backend

- `DATABASE_URL`

### Auth

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

### Frontend

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`

## Health Endpoints

- Backend: `https://metar-to-iwxxm-api.onrender.com/health`
- Auth: `https://metar-to-iwxxm-auth.onrender.com/health`

## Notes

- Backend default remains `DISABLE_AUTH=true` for initial rollout.
- Auth and backend CORS/origin settings must include frontend origin.
- Frontend is deployed as Render `static_site`, not a web service.
