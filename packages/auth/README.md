# Authentication Service - Supabase Middleware Proxy

[![codecov](https://codecov.io/gh/joseph-c-mcguire/metar-to-IWXXM/graph/badge.svg)](https://codecov.io/gh/joseph-c-mcguire/metar-to-IWXXM)

A middleware authentication service that proxies requests between the frontend/backend and Supabase, providing centralized auth management, security isolation, and easier monitoring.

## Purpose

This auth service provides:

- **Middleware Proxy**: Routes auth requests between clients and Supabase
- **Security Isolation**: Supabase credentials never exposed to frontend
- **Token Management**: Issues and verifies Supabase JWT tokens
- **User Registration & Login**: Proxies to Supabase authentication
- **Password Reset**: Email-based password recovery via Supabase
- **Backend Verification**: Provides token verification endpoint for backend services

## Architecture

The service acts as a secure proxy:

```
Frontend (5173) ──┐
                  ├──► Auth Service (Port 8003) ──► Supabase Auth
Backend (8001) ──┘     Middleware Proxy
```

Benefits:
- **Centralized auth logic** - All auth flows go through one service
- **Security** - Supabase keys never exposed to clients
- **Monitoring** - Single point to log auth events
- **Flexibility** - Easy to add rate limiting, caching, custom claims
- **Testing** - Mock auth service instead of Supabase in tests

## Project Structure

```
auth/
├── src/                    # Source code (restructured from src/auth/)
│   ├── __init__.py        # Package exports
│   ├── __main__.py        # FastAPI app entry point
│   ├── api.py             # API endpoints
│   ├── database.py        # Database setup & connection pooling
│   ├── models.py          # SQLAlchemy models (User, APIKey, PasswordResetToken)
│   └── security.py        # Security utilities (JWT, password hashing)
├── tests/                 # Unit tests (95% coverage target)
├── pyproject.toml         # Package configuration & dependencies
├── Dockerfile             # Container definition
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and receive JWT token
- `GET /auth/me` - Get current user profile (requires auth)

### API Keys
- `POST /auth/apikeys` - Create new API key (requires auth)
- `GET /auth/apikeys` - List all API keys (requires auth)
- `DELETE /auth/apikeys/{id}` - Revoke API key (requires auth)

### Password Reset
- `POST /auth/password-reset/request` - Request password reset token
- `POST /auth/password-reset/confirm` - Confirm and reset password

### Health
- `GET /health` - Service health check

## Database Models

### User
- `id`: Primary key
- `name`: Full name
- `email`: Unique email address
- `address`: User address
- `username`: Unique username (3-50 chars)
- `password_hash`: PBKDF2-SHA256 hashed password
- `is_active`: Account status
- `created_at`: Timestamp

### APIKey
- `id`: Primary key
- `key_hash`: SHA-256 hashed API key
- `user_id`: Foreign key to User
- `created_at`: Timestamp
- `revoked`: Revocation status

### PasswordResetToken
- `id`: Primary key
- `token`: URL-safe reset token
- `user_id`: Foreign key to User
- `expires_at`: Expiration timestamp
- `used`: Usage status
- `created_at`: Timestamp

## Configuration

Environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db  # or sqlite:///./auth.db

# JWT Settings
AUTH_JWT_SECRET=your-secret-key
AUTH_JWT_EXPIRE_MINUTES=60

# Password Reset
AUTH_RESET_EXPIRE_MINUTES=30
FRONTEND_BASE_URL=http://localhost:8000  # For reset links
```

## Supabase Integration

The service supports both Supabase pooling modes:

- **Transaction Pooler** (port 6543): Disables prepared statements for compatibility
- **Session Pooler** (port 5432): Full PostgreSQL feature support

Connection pooling is configured automatically based on the DATABASE_URL.

## Development

### Setup

```bash
# Install dependencies with uv
cd auth
uv pip install -e ".[dev]"

# Or with standard pip
pip install -e ".[dev]"
```

### Running Locally

```bash
# Run the service (uses entry point from src/__main__.py)
cd auth
python -m src

# Or with uvicorn directly
uvicorn src.__main__:app --reload --port 8003 --host 0.0.0.0
```

### Running with Docker

```bash
# Build image
docker build -t metar-auth .

# Run container
docker run -p 8001:8000 \
  -e DATABASE_URL=sqlite:///./auth.db \
  -e AUTH_JWT_SECRET=dev-secret \
  metar-auth
```

## Testing

Comprehensive test suite with 95% coverage target:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-branch --cov-report=html --cov-report=term-missing --cov-report=xml

# Run specific test file
pytest tests/test_api.py
```

### Test Categories

- **Unit Tests**: Individual function and class testing
- **API Tests**: Endpoint behavior and validation
- **Database Tests**: Model and query testing
- **Security Tests**: JWT, password hashing, API key generation
- **Integration Tests**: End-to-end workflow testing

## Security Considerations

- **Password Storage**: PBKDF2-SHA256 hashing via Passlib
- **JWT Tokens**: HS256 signing, configurable expiration
- **API Keys**: SHA-256 hashed, shown only once at creation
- **Reset Tokens**: URL-safe, time-limited, single-use
- **SQL Injection**: Protected by SQLAlchemy ORM
- **HTTPS**: Required in production (configure reverse proxy)

## Production Deployment

1. **Set strong JWT secret**: `AUTH_JWT_SECRET`
2. **Use PostgreSQL**: Not SQLite
3. **Enable SSL/TLS**: Database and API connections
4. **Configure CORS**: Restrict to known frontends
5. **Set up monitoring**: Health check endpoint
6. **Database migrations**: Use Alembic for schema changes
7. **Backup strategy**: Regular database backups

## Integration with Backend

The auth service is designed to work alongside the METAR conversion backend:

- Backend validates JWT tokens from auth service
- Users authenticate once, use token for all services
- API keys can be used for programmatic access
- Both services can share the same database or use separate ones

## License

Part of the METAR to IWXXM platform. See root LICENSE file.

## Contributing

1. Follow Python PEP 8 style guidelines
2. Add tests for new features (maintain 95% coverage)
3. Update this README for significant changes
4. Use uv for dependency management
