# Render Deployment Checklist

Quick reference for deploying METAR-to-IWXXM backend to Render.

---

## Pre-Deployment

- [ ] Read [docs/RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) (full guide)
- [ ] Verify `render.yaml` exists at repo root
- [ ] Have PostgreSQL connection string ready
  - [ ] Supabase project created, OR
  - [ ] RDS/other database provisioned
- [ ] Have GitHub account with repo access
- [ ] Render account created at https://render.com

---

## Deployment Steps

### 1. Push render.yaml to GitHub

```bash
git add render.yaml
git commit -m "Add render.yaml for Render deployment"
git push origin main
```

- [ ] File visible on GitHub at `/render.yaml`

### 2. Create Render Service

- [ ] Go to https://render.com/dashboard
- [ ] Click **New → Web Service**
- [ ] Select **Deploy from GitHub**
- [ ] Search for and select `joseph-c-mcguire/metar-to-IWXXM`
- [ ] Click **Connect**

### 3. Configure Environment Variables

In Render dashboard forms, set these variables:

**Required:**
- [ ] `DATABASE_URL` = `postgresql+asyncpg://...` (copy from Supabase/RDS)

**Optional (recommended):**
- [ ] `ALLOWED_ORIGINS` = `*` (or your frontend domain)
- [ ] `TRANSLATION_CENTRE_NAME` = Your organization name
- [ ] `TRANSLATION_CENTRE_DESIGNATOR` = 2-letter code (e.g., US)
- [ ] `ICAO_LOCATION_INDICATOR` = 4-letter code (e.g., KJFK)
- [ ] `SERVICE_ONLINE_SINCE` = Today's date (2026-02-17)
- [ ] `TECHNICAL_CONTACT_EMAIL` = Your email

**Note:** Other variables are already in `render.yaml`

### 4. Verify Build Settings

- [ ] **Root Directory:** `backend`
- [ ] **Build Command:** Auto-filled (or paste from render.yaml)
- [ ] **Start Command:** `python -m src` (auto-filled)
- [ ] **Health Check Path:** `/health` (auto-filled)
- [ ] **Instance Type:** Starter ($7/month)
- [ ] **Auto-deploy:** Enabled

### 5. Deploy

- [ ] Click **Create Web Service**
- [ ] Wait for deployment (2-5 minutes)
- [ ] Check Logs tab for `Application startup complete`

- [ ] **Verify health check:**
  ```bash
  curl https://<your-service>.onrender.com/health
  ```
  Expected response: `{"status": "healthy", ...}`

---

## Post-Deployment

### Immediate Verification

- [ ] Backend health endpoint returns 200
- [ ] Logs show no connection errors
- [ ] Database tables created (no errors in logs)

### Configuration

- [ ] Test with curl/Postman:
  ```bash
  curl -X GET https://<your-service>.onrender.com/health
  ```

### Next Steps (Optional)

- [ ] Deploy auth service or configure GitHub OAuth
- [ ] Deploy frontend (Static Site)
- [ ] Set up custom domain
- [ ] Enable monitoring (Sentry, UptimeRobot)
- [ ] Test API endpoints (see [docs/API.md](docs/API.md))

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Build fails with module error | Missing dependency | Check `backend/pyproject.toml`; ensure `uv pip install --system -e backend` runs |
| "Connection refused" in logs | Database URL invalid/unreachable | Verify `DATABASE_URL`, ensure DB allows Render IPs |
| Health check fails (403/500) | App crash on startup | Check logs for initialization errors, wait 30s for health checks to stabilize |
| "No module GIFTs" | GIFTs not in repo | Ensure `GIFTs/` subdirectory exists, commit and push |
| CORS errors from frontend | Origins not allowed | Set `ALLOWED_ORIGINS` to frontend domain or `*` |

For detailed troubleshooting, see [docs/RENDER_DEPLOYMENT.md → Common Issues](RENDER_DEPLOYMENT.md#common-issues--fixes)

---

## Render Dashboard Links

- **Dashboard:** https://render.com/dashboard
- **This service:** https://render.com/dashboard → your service
- **Overview:** Deployed URL, instance info
- **Logs:** Real-time application logs
- **Deployments:** View deploy history and rollback
- **Environment:** Manage env variables
- **Settings:** Drain period, health checks, notifications

---

## Cost Summary

| Item | Cost | Details |
|------|------|---------|
| Backend (Starter) | $7/mo | 0.5 CPU, 512 MB RAM |
| PostgreSQL | ~$10-15/mo | Supabase free tier OR external |
| **Total** | ~$17-22/mo | Dev/test tier |

Production upgrades available if needed.

---

## Quick Links

- 📖 **Full Guide:** [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md)
- 📋 **Project Structure:** [README.md](README.md)
- 🔌 **API Docs:** [docs/API.md](docs/API.md)
- 🔐 **Auth Docs:** [docs/AUTH_MIDDLEWARE_ARCHITECTURE.md](docs/AUTH_MIDDLEWARE_ARCHITECTURE.md)
- 🛠️ **Development:** [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

---

**Status:** ✅ Ready to deploy (all files prepared)

**Time estimate:** 15-20 minutes from here to live backend
