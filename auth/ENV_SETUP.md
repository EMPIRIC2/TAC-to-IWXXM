# Environment Configuration Guide

## Files Overview

### `.env.example` (🟢 Safe to commit)
Template file with placeholder values for all environment variables needed by the auth service. Use this as a reference for setting up your `.env` file.

**What's included:**
- Supabase configuration template
- Database URL pattern
- Frontend redirect URL
- Demo user credentials (example values only)

**How to use:**
```bash
cp .env.example .env
# Then edit .env with your actual values
```

### `.env` (🔴 Never commit - contains secrets)
Your actual environment configuration with real API keys, database passwords, and other sensitive values.

**⚠️ Security:** This file contains secrets and MUST NOT be committed to version control. It's already listed in `.gitignore` to prevent accidental commits.

**What's included:**
- Real Supabase URL and API keys
- Database connection string with password
- Frontend redirect URL
- Demo user credentials for local testing

## Environment Variables Explained

### Supabase Configuration
```
SUPABASE_URL=https://your-project.supabase.co          # Your Supabase project URL
SUPABASE_ANON_KEY=your-jwt-token-here                  # Anon key for client-side auth
```

### Database Configuration
```
DATABASE_URL=postgresql+psycopg2://user:pass@host/db   # Connection string with password
```

Current setup uses **Supabase transaction pooler (port 6543)** which:
- ✓ Works well with serverless/stateless apps
- ✓ Better connection efficiency
- ⚠️ Does NOT support prepared statements (SQLAlchemy configured to disable them)

**Alternative poolers:**
- Session pooler (port 5432): For long-lived connections, supports prepared statements
- Direct connection: Not recommended (IPv6 only)

### Frontend Configuration
```
FRONTEND_BASE_URL=http://localhost:5173               # Where to redirect after password reset (Vite dev server)
```

### Demo Users (Local Testing Only)
```
DEMO_MODE=true                                         # Enable demo user creation
DEMO_ADMIN_USERNAME=admin                             # Demo admin credentials
DEMO_ADMIN_PASSWORD=Admin123!SecurePass
DEMO_USER_USERNAME=demouser                           # Demo regular user
DEMO_USER_PASSWORD=User123!SecurePass
```

## Docker Integration

The Dockerfile now:
1. ✓ Copies `.env*` files (supports both `.env` and `.env.example`)
2. ✓ Uses Python's `dotenv` package to load environment variables
3. ✓ Provides comments on proper secret management

### Development (Local)
```bash
# Using docker-compose with .env file
docker-compose up auth

# Or with specific .env file
docker run --env-file .env metar-to-iwxxm-auth
```

### Production (Secure Secret Management)
For production deployments, do NOT bake secrets into Docker images:

**Option 1: Docker Secrets (Swarm)**
```bash
docker secret create auth_env /path/to/.env
docker service create --secret auth_env --env-file /run/secrets/auth_env ...
```

**Option 2: Environment Variables**
```bash
docker run \
  -e SUPABASE_URL="https://..." \
  -e SUPABASE_ANON_KEY="..." \
  -e DATABASE_URL="postgresql+psycopg2://..." \
  metar-to-iwxxm-auth
```

**Option 3: Cloud Secret Management**
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

## Security Best Practices

✅ **DO:**
- Keep `.env` in `.gitignore` (already configured)
- Use strong, unique database passwords
- Rotate API keys periodically
- Use environment variables in production instead of `.env` files
- Add `.env` to project's `README.md` setup instructions
- Review secrets before setting up CI/CD

❌ **DON'T:**
- Commit `.env` files to version control
- Share `.env` files via email or messaging
- Use same passwords across environments
- Log or print secrets
- Use demo credentials in production
- Hardcode secrets in source code

## .gitignore Configuration

The following are automatically ignored (don't commit):
```
.env                    # Your actual configuration with secrets
.env.local             # Local overrides
.env.*.local           # Environment-specific secrets
```

The following are safe to commit:
```
.env.example           # Template with placeholders
.gitignore             # This security configuration
```

## Troubleshooting

### "No such file or directory: .env"
This is normal during Docker builds. The `.env` file is optional for containers - use environment variables or mounted files instead.

### "SUPABASE_URL not set"
Verify `.env` file exists in the auth directory and contains `SUPABASE_URL=...`

### "Cannot connect to database"
1. Check `DATABASE_URL` is correct in `.env`
2. Verify database password is correct (special characters should be URL-encoded)
3. Ensure firewall allows connection to Supabase
4. Try using the Session pooler instead of Transaction pooler

### "AUTH key is invalid"
Regenerate Supabase anon key from Supabase dashboard if it's expired or compromised

## Setup Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Fill in real Supabase credentials
- [ ] Set up DATABASE_URL with correct connection string
- [ ] Set FRONTEND_BASE_URL to your frontend URL
- [ ] (Optional) Disable DEMO_MODE for production
- [ ] Verify with: `python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✓ Setup OK' if os.getenv('SUPABASE_URL') else '✗ Missing config')"`
- [ ] Test auth service: `cd .. && docker-compose up auth`

## Related Documentation

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Supabase Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Python dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
