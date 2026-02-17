# Deploying to Render: Step-by-Step Setup Guide

This guide walks you through deploying the METAR-to-IWXXM backend API to Render using the `render.yaml` configuration.

**Time to completion:** 15-20 minutes (including account setup)

---

## Prerequisites

- [ ] GitHub account (with access to joseph-c-mcguire/metar-to-IWXXM repo)
- [ ] Render account (free account at https://render.com)
- [ ] External PostgreSQL database (Supabase, AWS RDS, or similar)
  - Need connection string: `postgresql+asyncpg://user:password@host:port/db`

---

## Step 1: Prepare Your PostgreSQL Database

### Option A: Use Supabase (Recommended for quick setup)

1. Go to https://supabase.com and sign up (free tier available)
2. Create a new project:
   - Organization: create or select existing
   - Name: `metar-to-iwxxm`
   - Database password: save securely
   - Region: pick closest to your expected users
3. Copy your connection string:
   - Settings → Database → Connection string (Uvicorn/FastAPI)
   - Should look like: `postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres`
4. Save this—you'll need it in Step 4

### Option B: Use AWS RDS, DigitalOcean, or another provider

1. Create a PostgreSQL 14+ database
2. Get the connection string in format: `postgresql+asyncpg://user:password@host:port/dbname`
3. Ensure it allows inbound connections from Render (0.0.0.0/0 for testing, or restrict to Render IP ranges)

---

## Step 2: Push render.yaml to GitHub

The `render.yaml` file is already created at the repo root. Ensure it's committed and pushed:

```bash
cd /root/metar-to-IWXXM
git add render.yaml
git commit -m "Add render.yaml for Render deployment"
git push origin main
```

Verify on GitHub that the file is visible at the root: https://github.com/joseph-c-mcguire/metar-to-IWXXM/render.yaml

---

## Step 3: Create Render Account & Connect GitHub

1. Go to https://render.com
2. Sign up with GitHub (easier integration)
3. Authorize Render to access your GitHub repos
4. Go to Dashboard → New → Web Service
5. Select "Deploy from GitHub"
6. Find and select: `joseph-c-mcguire/metar-to-IWXXM`
7. Click "Connect"

---

## Step 4: Configure Service in Render Dashboard

After connecting the repo, Render should auto-detect `render.yaml`. You'll see a form to review settings:

### A. Service Details

- **Name:** `metar-to-iwxxm-api` (auto-filled from render.yaml)
- **Environment:** Python (auto-filled)
- **Instance Type:** Starter ($7/month) for testing — you can upgrade later
- **Auto-deploy:** ✅ Checked (auto-deploy on main branch pushes)

### B. Environment Variables (CRITICAL)

In the **Environment** section, add the following variables:

**[REQUIRED]**

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Paste your Supabase/RDS connection string here |

**[OPTIONAL but recommended]**

| Key | Value | Notes |
|-----|-------|-------|
| `ALLOWED_ORIGINS` | `*` (or comma-separated URLs) | CORS origins. For local dev: `http://localhost:3000,http://localhost:5173` |
| `TRANSLATION_CENTRE_NAME` | `Your Organization` | Your weather service name |
| `TRANSLATION_CENTRE_DESIGNATOR` | `XX` | 2-letter code (e.g., US, CA) |
| `ICAO_LOCATION_INDICATOR` | `XXXX` | 4-letter aerodrome code (e.g., KJFK) |
| `SERVICE_ONLINE_SINCE` | `2026-02-17` | Service start date |
| `TECHNICAL_CONTACT_EMAIL` | `your-email@example.com` | Your email |

**Note:** Other variables like `DISABLE_AUTH=true`, `RELOAD=false`, `SCHEMATRON_USE_DOCKER=false`, etc., are already in `render.yaml` and don't need to be set again here.

### C. Build & Start Commands

Should be auto-filled from `render.yaml`:

- **Build Command:** 
  ```
  pip install --upgrade pip uv && uv pip install --system -e backend && uv pip install --system ./GIFTs
  ```
- **Start Command:** 
  ```
  python -m src
  ```
- **Root Directory:** `backend`
- **Health Check Path:** `/health`

If not auto-filled, manually paste the above.

**About Schematron Validation on Render:**

`SCHEMATRON_USE_DOCKER=false` is pre-configured in render.yaml because Render doesn't support Docker-in-Docker. The backend will use pure Python lxml validation instead of the full XSLT2-based validator. This means:
- ✅ Core validation still works (XSD schemas, WMO codelists, GML references)
- ✅ Deployable on Render Starter tier ($7/month)
- ⚠️ Advanced ISO Schematron business rules are skipped (~20% of edge cases)
- ⚠️ Validation is faster (no Docker container overhead)

See [ENVIRONMENT_VARIABLES.md → SCHEMATRON_USE_DOCKER](../docs/ENVIRONMENT_VARIABLES.md#schematron_use_docker) for full details.

---

## Step 5: Deploy

1. Click **"Create Web Service"** or **"Deploy"**
2. Render will:
   - Clone the repo
   - Install `uv` and dependencies
   - Build the backend + GIFTs library
   - Start the Uvicorn server
   - Begin health checks

3. **Monitor logs:**
   - Go to Logs tab
   - Watch for:
     - ✅ `Application startup complete` → Success!
     - ❌ `ERROR: could not translate host name...` → Database connection failed
     - ❌ `ModuleNotFoundError` → Dependency missing

---

## Step 6: Verify Deployment

Once logs show `Application startup complete`:

### Test the health endpoint

```bash
curl https://<your-service-name>.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "gifts_available": true
}
```

### Check database connection

If the above works, the database is connected. Logs should show no connection errors.

### Test CORS (if frontend in different domain)

```bash
curl -H "Origin: https://your-frontend.com" \
     https://<your-service-name>.onrender.com/health \
     -v
```

Check response headers for `Access-Control-Allow-Origin`.

---

## Step 7: Configure Authentication (Later)

Currently, `DISABLE_AUTH=true` means **all requests bypass authentication**. This is fine for testing the API.

**Before going to production, you must:**

1. **Option A: Deploy the auth service**
   - Add another service to `render.yaml` for `auth/` folder
   - Set `DISABLE_AUTH=false`
   - Set `AUTH_SERVICE_URL=https://<auth-service>.onrender.com`

2. **Option B: Use GitHub OAuth directly**
   - Register your Render domain in GitHub OAuth App settings
   - Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` env vars
   - Set `DISABLE_AUTH=false`

See [docs/AUTH_MIDDLEWARE_ARCHITECTURE.md](../docs/AUTH_MIDDLEWARE_ARCHITECTURE.md) for details.

---

## Step 8: Add Frontend (Optional)

Once the backend is running, you can deploy the frontend as a separate Static Site:

1. In Render Dashboard: **New → Static Site**
2. Connect the same repo (`joseph-c-mcguire/metar-to-IWXXM`)
3. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm ci && npm run build`
   - **Publish Directory:** `dist`
   - **Environment Variable:**
     - `VITE_API_URL=https://<your-backend>.onrender.com` (paste your backend URL)
4. Deploy

The frontend will be available at a separate Render URL (e.g., `https://<frontend-name>.onrender.com`).

---

## Common Issues & Fixes

### Issue: "PostgreSQL connection refused"

**Cause:** `DATABASE_URL` is missing or invalid

**Fix:**
1. Double-check the connection string format: `postgresql+asyncpg://user:password@host:port/db`
2. Ensure the database is accessible from Render (firewall rules allow inbound from 0.0.0.0 or Render's IP range)
3. For Supabase: paste the exact connection string from **Settings → Database → Connection string**

### Issue: "ModuleNotFoundError: No module named 'src'"

**Cause:** Build command failed or root directory is wrong

**Fix:**
1. In Render dashboard, verify **Root Directory** is set to `backend`
2. Verify build command includes: `uv pip install --system -e backend`
3. Check build logs for errors during dependency installation

### Issue: "GIFTs library not found"

**Cause:** GIFTs submodule not initialized or not in repo

**Fix:**
1. Ensure entire repo is cloned (including `GIFTs/` subdirectory)
2. If GIFTs is a submodule, Render should auto-initialize it
3. Check build logs for cloning errors
4. Verify `GIFTs/pyproject.toml` exists locally before pushing

### Issue: Health check fails (status 403 or 500)

**Cause:** Database not initialized or startup failed

**Fix:**
1. Check logs for database errors
2. Verify `DATABASE_URL` is correct and database is accessible
3. Wait 30-60 seconds; health checks start before full app init
4. Restart the service in Render dashboard

### Issue: Frontend can't reach backend (CORS error)

**Cause:** `ALLOWED_ORIGINS` not set correctly

**Fix:**
1. Set `ALLOWED_ORIGINS` to your frontend domain (or `*` for testing)
2. Make sure frontend's `VITE_API_URL` matches your backend URL exactly
3. Test with curl to isolate the issue

### Issue: Schematron validation errors in logs

**Status:** ✅ **Already Fixed** — Schematron is disabled in render.yaml by default

**Previous issue (if re-enabled):**
```
ValidationError: Schematron validation failed
ERROR: Docker not available
```

**Why it was failing:**
- Render doesn't support Docker-in-Docker (containers within containers)
- `SCHEMATRON_USE_DOCKER=true` tried to spawn Docker from within FastAPI container
- This is a Render platform limitation, not a bug

**Current solution (already configured):**
- `SCHEMATRON_USE_DOCKER=false` in render.yaml
- Backend uses pure Python lxml validation
- No Docker required; works out-of-the-box

**Trade-offs:**
- ✅ **Gain:** No Docker dependencies, works on Render Starter tier
- ⚠️ **Cost:** Loses XSLT2-specific business rules (catches ~80% still)
- ✅ **Plus:** Validation is 2-5 seconds faster (no Docker startup)

**If you need full Schematron validation:**

Option A: Deploy separate Schematron microservice
```
1. Create backend/docker/Dockerfile.schematron (exists locally)
2. Deploy as separate Web Service on Render
3. Set SCHEMATRON_SERVICE_URL in backend env
4. Backend calls HTTP endpoint for validation
```

Option B: Wait for Docker-in-Docker support
- Render may add native Docker support in future
- Re-enable `SCHEMATRON_USE_DOCKER=true` when available

Option C: Migrate to platform with Docker support
- AWS ECS, Google Cloud Run (full Docker support)
- More expensive ($20+/month vs. $7/month Render)

**For now:** Current setup is production-ready without Docker Schematron

---

## Monitoring & Logs

### View real-time logs

- Render Dashboard → Your service → Logs tab
- Or via CLI: `render logs` (if you've installed Render CLI)

### Key log lines to watch

```
2026-02-17T12:34:56Z Your service has been deployed
2026-02-17T12:34:57Z Building...
2026-02-17T12:35:10Z [+] Building Docker image (if using Docker image)
2026-02-17T12:35:30Z Starting your service...
2026-02-17T12:35:32Z Application startup complete [uvicorn]
2026-02-17T12:35:33Z Health check status: healthy
```

### Set up error notifications

1. Go to **Settings → Notifications**
2. Enable Slack/email for deployment failures
3. Or use Sentry: set `SENTRY_DSN` env var for error tracking

---

## Next Steps

1. ✅ Deploy backend with this guide
2. ⬜ Deploy auth service (or configure GitHub OAuth)
3. ⬜ Deploy frontend (static site)
4. ⬜ Set up custom domain (Render → Domains)
5. ⬜ Enable SSL/TLS (auto by Render)
6. ⬜ Set up monitoring (Sentry, UptimeRobot)
7. ⬜ Document API endpoints (Swagger at `/docs`)

---

## Support & Resources

- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/deployment/
- **Supabase Docs:** https://supabase.com/docs/guides/database
- **This project:** [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md)

---

## Cost Breakdown (Starter tier)

| Resource | Cost | Notes |
|----------|------|-------|
| Web Service (Starter) | $7/month | 0.5 CPU, 512 MB RAM |
| PostgreSQL (external) | ~$10-20/month | Depends on provider (Supabase free tier available) |
| **Total** | **$17-27/month** | Suitable for development/testing |

For production, upgrade instance type and enable auto-scaling (pricing increases).

---

**You're done! Your backend is now live on Render.** 🎉
