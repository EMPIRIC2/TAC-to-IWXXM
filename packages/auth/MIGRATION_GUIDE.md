# Auth Middleware Implementation - Quick Start Guide

## What Changed

The architecture has been refactored so that the **auth service acts as a middleware proxy** between your frontend/backend and Supabase. This provides better security, centralized control, and easier monitoring.

### Before
```
Frontend ──────► Supabase (direct)
Backend ───────► Supabase (direct)
```

### After
```
Frontend ──┐
           ├──► Auth Service ──► Supabase
Backend ───┘    (Port 8002)
```

## Setup Steps

### 1. Install Auth Service Dependencies

```bash
cd auth
uv pip install -e .
```

### 2. Create Root .env File

```bash
# Copy example and edit with your Supabase credentials
cp .env.example .env

# Add these values:
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-from-supabase-dashboard
```

### 3. Start Services with Docker Compose

```bash
docker-compose up --build
```

Services will start on:
- Frontend: http://localhost:5173 (Vite dev server) or 8000 (production)
- Backend: http://localhost:8001
- Auth Service: http://localhost:8003

### 4. Test Authentication

Open http://localhost:8000 in your browser. The frontend now communicates with the auth service, which proxies to Supabase.

## What Was Modified

### New Files Created

1. **`/auth/src/supabase_proxy.py`** - Supabase client wrapper
   - Handles all communication with Supabase
   - Provides async methods for auth operations
   
2. **`/auth/src/api_supabase.py`** - New API endpoints
   - POST `/auth/register` - Register via Supabase
   - POST `/auth/login` - Login via Supabase
   - POST `/auth/logout` - Logout from Supabase
   - GET `/auth/me` - Get current user
   - POST `/auth/refresh` - Refresh token
   - POST `/auth/password-reset/request` - Request reset
   - POST `/auth/password-reset/confirm` - Confirm reset
   - GET `/auth/verify` - Verify token (for backend)

3. **`/frontend/src/utils/authService.ts`** - Frontend auth client
   - Replaces direct Supabase calls
   - Calls auth service API instead
   - Manages tokens in localStorage

4. **`/docs/AUTH_MIDDLEWARE_ARCHITECTURE.md`** - Full documentation

### Modified Files

1. **`/auth/src/__main__.py`**
   - Now imports `api_supabase` instead of `api`
   - Added CORS middleware

2. **`/auth/pyproject.toml`**
   - Added `supabase>=2.0.0` dependency

3. **`/backend/src/utilities/security.py`**
   - Changed from direct Supabase JWKS verification
   - Now calls auth service's `/auth/verify` endpoint

4. **`/docker-compose.yml`**
   - Auth service: Added `SUPABASE_URL` and `SUPABASE_ANON_KEY` env vars
   - Backend: Added `AUTH_SERVICE_URL=http://auth:8000`
   - Frontend: Changed to use `VITE_AUTH_SERVICE_URL`

5. **Environment Files** (`.env.example`)
   - Updated to reflect new architecture
   - Frontend  no longer needs Supabase keys
   - Auth service needs Supabase credentials

## Frontend Changes Needed

The frontend needs to be updated to use the new `authService.ts` instead of direct Supabase calls. 

**Example migration:**

```typescript
// OLD - Direct Supabase
import { supabase } from './utils/supabase/client';
const { data, error } = await supabase.auth.signInWithPassword({email, password});

// NEW - Via Auth Service
import { login } from './utils/authService';
const result = await login({email, password});
```

You'll need to update these files:
- `/frontend/src/app/components/auth/Login.tsx`
- `/frontend/src/app/components/auth/Register.tsx` 
- `/frontend/src/app/components/auth/PasswordReset.tsx`
- Any other files that import from `./utils/supabase/client`

## Benefits

1. ✅ **Security**: Supabase credentials never exposed to frontend
2. ✅ **Centralized**: All auth logic in one service
3. ✅ **Monitoring**: Easy to log all auth events
4. ✅ **Testing**: Mock auth service instead of Supabase
5. ✅ **Flexible**: Easy to add rate limiting, 2FA, custom claims

## Troubleshooting

### Auth service fails to start
- Check that SUPABASE_URL and SUPABASE_ANON_KEY are set in `.env`
- Verify the Supabase URL format: `https://projectref.supabase.co`

### Backend can't verify tokens
- Ensure AUTH_SERVICE_URL is set correctly in docker-compose
- Check auth service is healthy: `curl http://localhost:8002/health`

### Frontend gets CORS errors
- Auth service has CORS middleware enabled for all origins
- In production, restrict `allow_origins` in `/auth/src/__main__.py`

## Next Steps

1. Update frontend components to use `/frontend/src/utils/authService.ts`
2. Test registration and login flows
3. Update any existing user sessions (users will need to re-login)
4. Review and customize CORS settings for production
5. Add monitoring/logging as needed

## Documentation

Full documentation: [docs/AUTH_MIDDLEWARE_ARCHITECTURE.md](../docs/AUTH_MIDDLEWARE_ARCHITECTURE.md)
