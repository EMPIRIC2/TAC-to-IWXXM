# Architecture Documentation: Auth Service Middleware

## Overview

The auth service now acts as a **middleware proxy** between the frontend/backend and Supabase. This provides:

- **Centralized authentication logic**
- **Easier monitoring and logging**
- **Consistent token handling**
- **Security isolation** (Supabase keys never exposed to frontend)
- **Future flexibility** to switch auth providers

## Architecture Diagram

```
┌──────────┐           ┌──────────────┐           ┌──────────┐
│          │   HTTP    │              │   HTTP    │          │
│ Frontend ├──────────►│ Auth Service ├──────────►│ Supabase │
│          │◄──────────┤  (Port 8002) │◄──────────┤   Auth   │
└──────────┘  Tokens   │              │  JWKS     └──────────┘
                       └──────▲───────┘
                              │
                       ┌──────┴───────┐
                       │              │
                       │   Backend    │
                       │ (Port 8001)  │
                       │              │
                       └──────────────┘
                      Verifies tokens
                     via auth service
```

## Service Responsibilities

### Auth Service (Port 8002)
- Proxies registration requests to Supabase
- Proxies login requests to Supabase
- Returns Supabase tokens to clients
- Provides token verification endpoint for backend
- Handles password reset flows
- **Environment Variables:**
  - `SUPABASE_URL` - Your Supabase project URL
  - `SUPABASE_ANON_KEY` - Supabase anonymous key (server-side only)
  - `FRONTEND_BASE_URL` - For password reset redirects

### Backend (Port 8001)
- Validates tokens by calling auth service's `/auth/verify` endpoint
- No direct Supabase communication
- **Environment Variables:**
  - `AUTH_SERVICE_URL` - URL of auth service (default: http://auth:8000 in Docker)

### Frontend (Port 8000)
- Calls auth service API for all auth operations
- Stores tokens in localStorage
- Automatically refreshes expired tokens
- No direct Supabase SDK usage for auth
- **Environment Variables:**
  - `VITE_AUTH_SERVICE_URL` - URL of auth service (default: http://localhost:8002)

## API Endpoints

### Auth Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/logout` | Sign out current user |
| GET | `/auth/me` | Get current user info |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/password-reset/request` | Send password reset email |
| POST | `/auth/password-reset/confirm` | Confirm password reset |
| GET | `/auth/verify` | Verify token (backend use) |
| GET | `/health` | Health check |

## Token Flow

### Registration Flow
```
1. Frontend → POST /auth/register {email, password, metadata}
2. Auth Service → Supabase: sign_up()
3. Supabase → Auth Service: {user, session: {access_token, refresh_token}}
4. Auth Service → Frontend: Return tokens
5. Frontend: Store tokens in localStorage
```

### Login Flow
```
1. Frontend → POST /auth/login {email, password}
2. Auth Service → Supabase: sign_in_with_password()
3. Supabase → Auth Service: {user, session: {access_token, refresh_token}}
4. Auth Service → Frontend: Return tokens
5. Frontend: Store tokens in localStorage
```

### Backend Verification Flow
```
1. Frontend → Backend API with Authorization: Bearer <token>
2. Backend → Auth Service: GET /auth/verify with token
3. Auth Service → Supabase: Verify token
4. Auth Service → Backend: {user_id, email, metadata}
5. Backend: Process request with user info
```

## Migration Guide

### Frontend Changes

**Before (Direct Supabase):**
```typescript
import { supabase } from './utils/supabase/client';

// Login
const { data, error } = await supabase.auth.signInWithPassword({
  email, password
});
```

**After (Via Auth Service):**
```typescript
import { login } from './utils/authService';

// Login
const result = await login({ email, password });
// Tokens automatically stored
```

### Backend Changes

**Before (Direct JWKS verification):**
```python
# Fetched JWKS from Supabase
# Verified JWT locally
from utilities.security import verify_supabase_token
```

**After (Via Auth Service):**
```python
# Same function name, different implementation
# Now calls auth service to verify
from utilities.security import verify_supabase_token
```

## Setup Instructions

1. **Set Environment Variables**
   ```bash
   # Root .env file
   cp .env.example .env
   # Edit .env and add your Supabase credentials
   ```

2. **Install Auth Service Dependencies**
   ```bash
   cd auth
   uv pip install -e .
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Test Authentication**
   ```bash
   # Register a user
   curl -X POST http://localhost:8002/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
   
   # Login
   curl -X POST http://localhost:8002/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
   ```

## Benefits

1. **Security**: Supabase credentials never exposed to frontend
2. **Monitoring**: Single point to log all auth events
3. **Rate Limiting**: Easier to implement at auth service level
4. **Caching**: Can cache user lookups at auth service
5. **Flexibility**: Easy to add 2FA, custom claims, etc.
6. **Testing**: Mock auth service in tests instead of Supabase

## Future Enhancements

- Add rate limiting on auth endpoints
- Implement auth event logging
- Add 2FA support
- Cache frequently accessed user data
- Support multiple auth providers (Google, GitHub, etc.)
