# Documentation Archive

This folder contains outdated or superseded documentation that is kept for historical reference only.

## Archived Files

### Outdated Architecture Docs

The following documents describe architecture or implementation approaches that have been superseded by newer approaches:

**SUPABASE_AUTH_IMPLEMENTATION.md** (Archived)
- **Reason**: Describes direct Supabase integration approach that was replaced with auth middleware proxy
- **Successor**: See [AUTH_MIDDLEWARE_ARCHITECTURE.md](../docs/AUTH_MIDDLEWARE_ARCHITECTURE.md) in parent directory
- **Why Changed**: Auth middleware provides better security isolation and centralized auth control

**SUPABASE_AUTH_QUICKSTART.md** (Archived)  
- **Reason**: Quick start for direct Supabase integration (old approach)
- **Successor**: See [DEVELOPMENT.md](../DEVELOPMENT.md) for current quick start
- **Why Changed**: Auth now goes through middleware proxy for security

## Kept Documentation

The following documentation remains active and relevant:

- **API.md** - RESTful API endpoint reference
- **AUTH_MIDDLEWARE_ARCHITECTURE.md** - How the auth middleware proxy works
- **SUPABASE_INTEGRATION.md** - Database connection configuration and pooling details
- **SUPABASE_EMAIL_TEMPLATES.md** - Email template configuration for Supabase Auth

## For New Developers

📖 **Start here**: [DEVELOPMENT.md](../DEVELOPMENT.md) in the project root for complete setup and development guide.

## Historical Context

The project initially used direct Supabase integration in the frontend and backend. This was later refactored to use an auth middleware proxy service for:

1. **Better Security**: Supabase credentials never exposed to frontend
2. **Centralized Control**: Single point for auth logic, logging, and monitoring
3. **Flexibility**: Easy to add rate limiting, custom claims, alternative auth providers
4. **Testability**: Mock auth service instead of Supabase in tests

This refactoring is thoroughly documented in [AUTH_MIDDLEWARE_ARCHITECTURE.md](../docs/AUTH_MIDDLEWARE_ARCHITECTURE.md).
