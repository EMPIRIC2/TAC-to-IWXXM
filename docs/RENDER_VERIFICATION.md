# Post-Deployment Verification & Troubleshooting

Complete guide for verifying your Render deployment and fixing common issues.

---

## Part 1: Initial Deployment Verification (First 5 minutes)

After clicking "Create Web Service" in Render, watch the deployment progress.

### Check Logs

In Render Dashboard → Your Service → **Logs** tab:

#### ✅ Expected Success Logs

```
2026-02-17T12:34:56Z   Your service has been deployed
2026-02-17T12:34:57Z   Building...
2026-02-17T12:35:05Z   [+] pip install --upgrade pip uv
2026-02-17T12:35:10Z   [+] uv pip install --system -e backend
2026-02-17T12:35:25Z   [+] uv pip install --system ./GIFTs
2026-02-17T12:35:30Z   [+] Build complete
2026-02-17T12:35:31Z   Starting your service...
2026-02-17T12:35:32Z   INFO:     Uvicorn running on http://0.0.0.0:10000
2026-02-17T12:35:33Z   INFO:     Application startup complete
2026-02-17T12:35:34Z   Health check passed
```

**What this means:** ✅ Build succeeded, server started, ready for requests.

#### ❌ Common Failure Logs

**Problem: ModuleNotFoundError**
```
ModuleNotFoundError: No module named 'src'
```
**Cause:** Root directory not set to `backend` or build command failed

**Fix:**
1. Verify **Root Directory** is `backend` (not the repo root)
2. Check build logs for dependency errors
3. Restart deployment from Render dashboard

---

**Problem: Database Connection Error**
```
sqlalchemy.exc.OperationalError: (asyncpg.exceptions.CannotConnectNowError) cannot connect now
connect() got an error: unable to translate host name "db.invalid.com" to address: Name or service not known
```
**Cause:** `DATABASE_URL` is missing, invalid, or database is inaccessible

**Fix:**
1. In Render dashboard, go to **Environment**
2. Verify `DATABASE_URL` is set and matches your actual database
3. For Supabase: check Settings → Database → Connection string (Uvicorn)
4. Ensure database allows inbound from Render (firewall rules)
5. Redeploy

---

**Problem: Dependency Not Found**
```
ERROR: Could not locate the editable package
ModuleNotFoundError: No module named 'gifts'
```
**Cause:** Build command syntax error or missing `GIFTs` subdirectory

**Fix:**
1. Verify `GIFTs/` exists in your local repo
2. Push to GitHub: `git add GIFTs && git commit -m "..."`
3. Check build command matches:
   ```
   uv pip install --system -e backend && uv pip install --system ./GIFTs
   ```
4. Redeploy

---

### Manual Health Check (after logs show startup complete)

Once logs show `Application startup complete`, wait 30 seconds, then test:

```bash
# Replace <service-name> with your actual Render service name
# (e.g., metar-to-iwxxm-api or similar)

curl -s https://<service-name>.onrender.com/health | jq .
```

**Expected response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "gifts_available": true
}
```

**If this works:** ✅ Backend is live and healthy!

---

## Part 2: Detailed Verification Tests

### Test 1: Database Connectivity

The health endpoint already confirms database connection. To verify more thoroughly:

```bash
# Check database logs (if using Supabase)
# 1. Go to Supabase dashboard
# 2. Project → Logs
# 3. Look for connections from Render IP
# 4. Should see successful connections and no auth errors
```

Or test API endpoint that queries the database:

```bash
curl -s https://<service-name>.onrender.com/translations/statistics | jq .
```

**Expected (if stats enabled):**
```json
{
  "total_translations": 0,
  "successful": 0,
  "failed": 0,
  "last_24h": 0
}
```

---

### Test 2: CORS Headers

Test that CORS is configured correctly:

```bash
# If frontend is on a different domain
curl -i \
  -H "Origin: https://your-frontend-domain.com" \
  https://<service-name>.onrender.com/health
```

**Look for in response headers:**
```
Access-Control-Allow-Origin: https://your-frontend-domain.com
Access-Control-Allow-Credentials: true
```

**If missing:** Edit `ALLOWED_ORIGINS` in Render environment variables.

---

### Test 3: Authentication Status

Since `DISABLE_AUTH=true`:

```bash
# This should work WITHOUT a token
curl -s https://<service-name>.onrender.com/health | jq .

# This should also work (token ignored when auth disabled)
curl -s \
  -H "Authorization: Bearer fake-token-12345" \
  https://<service-name>.onrender.com/health | jq .
```

**Both should return 200.** If not, check logs for auth-related errors.

---

### Test 4: API Endpoints

Test actual translation endpoint:

```bash
# Example: GET request (health check)
curl -s https://<service-name>.onrender.com/health | jq .

# Example: POST request (if you have test data)
# Check API docs at https://<service-name>.onrender.com/docs
```

See [docs/API.md](../docs/API.md) for complete endpoint list.

---

### Test 5: Swagger/OpenAPI Docs

FastAPI auto-generates docs:

```
https://<service-name>.onrender.com/docs
```

Should show:
- ✅ All endpoints listed (health, translate, etc.)
- ✅ Request/response schema models
- ✅ Try-it-out feature works

---

## Part 3: Application Behavior Checks

### Monitor Real-Time Logs

Render Dashboard → **Logs** tab:

```bash
# Watch for:
- "INFO: POST /health" (requests coming in)
- "INFO: POST /translate/metar" (METAR translation requests)
- No ERROR or WARNING logs (exceptions)
- Database connection steadiness
```

**Restart service if:**
- Repeated "connection timeout" errors
- Memory usage growing unbounded (memory leak)
- No responses to requests (deadlock)

---

### Check Memory & CPU Usage

Render Dashboard → **Metrics** tab:

| Metric | Healthy | Warning |
|--------|---------|---------|
| Memory | < 256 MB | > 400 MB (512 MB limit on Starter) |
| CPU | < 50% avg | > 80% sustained |
| Restart Count | 0 | > 0 (indicates crashes) |

**If memory > 400 MB:**
- Possible memory leak in code
- Upgrade to Standard instance (more RAM)
- Set `ENABLE_STATISTICS=false` (reduces memory)

---

### Database Connection Pool Health

In logs, look for:

```
# Healthy:
INFO: Database pool initialized [pool_size=10]
INFO: Connected to PostgreSQL 14.1

# Warning signs:
ERROR: Too many connections
WARNING: Pool exhausted
```

If pool becomes exhausted:
- Increase database `max_connections` setting
- Or increase `pool_size` in backend config
- Or scale down instances temporarily

---

## Part 4: Common Issues & Solutions

### Issue: Service keeps restarting

**Logs show:**
```
Your instance was restarted due to a crash
```

**Diagnosis:**
1. Check logs for error message
2. Look for patterns in errors (database, memory, imports)

**Solutions:**

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | Rebuild (dependencies out of sync) |
| Memory error | Upgrade instance or set `ENABLE_STATISTICS=false` |
| Database connection | Check `DATABASE_URL` env var |
| `KeyError` for env var | Missing required env var—check list |

**To restart:** Render Dashboard → Service → **Restart** button

---

### Issue: Slow responses (> 10 seconds)

**Check:**
1. Is database responding slow? (Supabase dashboard → Performance)
2. Is Schematron validation failing? (check logs for validation errors)
3. Is WMO validation timing out? (set `WMO_VALIDATION_TIMEOUT=10`)

**Fix:**
```env
WMO_ONLINE_VALIDATION=false  # Skip WMO registry checks (faster)
SCHEMATRON_USE_DOCKER=false  # Skip Schematron validation
```

---

### Issue: Frontend can't connect (CORS error)

**Browser console shows:**
```
Access to XMLHttpRequest blocked by CORS policy
Origin 'https://my-frontend.com' not allowed
```

**Fix:**
1. Render dashboard → Service → **Environment**
2. Set `ALLOWED_ORIGINS=https://my-frontend.com`
3. Or test with `ALLOWED_ORIGINS=*` temporarily (not for production!)
4. Redeploy (click **Reboot** or **Deploy**)

---

### Issue: Database says "too many connections"

**Logs show:**
```
FATAL: too many connections for role "postgres"
```

**Causes:**
- Multiple Render services connecting simultaneously
- Database pool not being released
- Frontend/backend mismatch

**Fix:**
1. Check how many services connect to same database
2. Supabase: Settings → Database → Connection Pooling → increase size
3. Or reduce backend `pool_size` temporarily:
   - Check [backend/src/config.py](../backend/src/config.py)
   - Rebuild with `pool_size=5`

---

### Issue: Schematron validation fails

**Logs show:**
```
ValidationError: Schematron validation failed
ERROR: Docker not available
```

**Solutions:**

Option A: Disable Schematron
```env
SCHEMATRON_USE_DOCKER=false
```

Option B: Use alternative validation
- Contact support for HTTP-based validation service
- Or implement custom validation

Option C: Render doesn't support Docker-in-Docker
- This is a Render platform limitation
- Use option A for now

---

## Part 5: Pre-Production Readiness Checklist

Before exposing API to real users:

### Security

- [ ] `DISABLE_AUTH=false` (enable authentication)
- [ ] `ALLOWED_ORIGINS` set to specific frontend domain(s)
- [ ] No sensitive data in logs (`LOG_LEVEL=INFO`, not `DEBUG`)
- [ ] `SENTRY_DSN` set for error tracking
- [ ] Database password strong (avoid `postgres:postgres`)
- [ ] API endpoints don't expose internal errors to clients

### Availability

- [ ] Health endpoint reliably responds (200 OK)
- [ ] Database auto-recovery on Render restart
- [ ] Monitoring/alerting configured (Sentry, UptimeRobot)
- [ ] Logs reviewed for warnings

### Performance

- [ ] Response times < 5 seconds for typical requests
- [ ] Memory stable (no growth over 1 hour)
- [ ] Database pool not exhausted
- [ ] CPU usage < 80% sustained load

### Functionality

- [ ] All API endpoints working (`/health`, `/translate/metar`, etc.)
- [ ] Frontend ↔ Backend communication successful
- [ ] Database queries returning correct data
- [ ] Error handling graceful (500 errors don't crash app)

### Configuration

- [ ] All required env vars set
- [ ] No hardcoded secrets in code
- [ ] Database backups enabled (Supabase auto-backups daily)
- [ ] Service can scale (upgrade instance if needed)

---

## Part 6: Monitoring & Alerts Setup

### Option 1: Sentry (Recommended)

1. Create free account at https://sentry.io
2. Create new project (FastAPI)
3. Copy DSN: `https://key@sentry.io/123456`
4. In Render dashboard:
   - Environment → Add `SENTRY_DSN=https://...`
   - Redeploy
5. Go to Sentry → Alerts → Create (on errors)

### Option 2: UptimeRobot (Availability)

1. Create free account at https://uptimerobot.com
2. Add monitor:
   - Type: HTTPS
   - URL: `https://<service-name>.onrender.com/health`
   - Check every: 5 minutes
3. Set notifications (email/Slack)

### Option 3: Render Notifications

1. Render dashboard → Service → **Settings** → **Notifications**
2. Enable for: Deployment fail, Service crash, Build fail
3. Choose: Email, Slack, etc.

---

## Part 7: Scaling & Optimization

### If hitting resource limits:

**Memory issues:**
```
Upgrade from Starter ($7) to Standard ($12)
Or set ENABLE_STATISTICS=false
Or reduce database connection pool
```

**CPU issues:**
```
May indicate slow code or database queries
Profile with cProfile or database query analysis
Consider upgrading instance temporarily to investigate
```

**Database issues:**
```
Supabase: upgrade from free to Pro ($25)
Or migrate to dedicated PostgreSQL instance
Or optimize queries (check docs/sql-optimization/)
```

---

## Support & Resources

| Resource | Use Case |
|----------|----------|
| [Render Docs](https://render.com/docs) | Platform-specific issues |
| [FastAPI Docs](https://fastapi.tiangolo.com) | API framework questions |
| [Supabase Docs](https://supabase.com/docs) | Database issues |
| [docs/DEVELOPMENT.md](../docs/DEVELOPMENT.md) | Local dev setup |
| [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | System design |

---

## Quick Fixes (Copy-Paste)

### Restart service
```bash
# Via Render dashboard: Service → Restart
```

### Redeploy with latest code
```bash
# Via GitHub: Push changes to main branch
# Or via Render: click "Reboot"
```

### Force rebuild (clear cache)
```bash
# Via Render: Service → Deployments → Click latest → scroll down → Restart
```

### Check if service is alive
```bash
curl -i https://<service-name>.onrender.com/health
# Should return 200 immediately
```

### View tail logs (last 100 lines)
```bash
# Via Render dashboard → Logs tab (auto-scrolling)
```

### Clear environment variable
```bash
# Via Render: Service → Environment → Remove variable → Save
# Redeploy triggered automatically
```

---

**Status:** ✅ Ready to verify! Follow Part 1 after deployment starts.
