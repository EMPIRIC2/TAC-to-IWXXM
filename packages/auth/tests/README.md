# Authentication Service Tests

This directory contains comprehensive tests for the authentication service, including Supabase PostgreSQL integration tests.

## Test Files

### `test_login_email_validation.py`
Primary active auth/proxy suite covering:
- Email and login validation behavior
- Supabase proxy integration surfaces (sync path)
- API/auth flow edge-case handling

### `test_api_supabase_database_extra.py`
Focused unit tests for active Supabase-proxy routes and database helpers:
- Register/login/logout/refresh/verify route delegation
- Password reset request/confirm route behavior
- Header token parsing and permissive email validation
- Database initialization helper behavior

### `test_supabase_integration.py`
Supabase-specific integration tests covering:
- Database connection validation
- Table operations (CRUD)
- Transaction handling
- Model relationships
- Error handling
- Performance testing
- IPv4 connection pooling validation

## Running Tests

### Prerequisites

1. **Install test dependencies:**
   ```bash
   cd auth
   pip install -e ".[dev]"
   ```

2. **For Supabase integration tests, set the DATABASE_URL:**
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL="postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres"
   
   # Linux/Mac
   export DATABASE_URL="postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres"
   ```

### Run All Tests

```bash
# From the auth directory
pytest tests/ -v

# Or from project root
pytest auth/tests/ -v
```

### Run Specific Test Files

```bash
# Run active auth/proxy unit tests
pytest auth/tests/test_login_email_validation.py -v

# Run only Supabase integration tests (requires DATABASE_URL)
pytest auth/tests/test_supabase_integration.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest auth/tests/test_supabase_integration.py::TestSupabaseConnection -v

# Run a specific test function
pytest auth/tests/test_api_supabase_database_extra.py::test_verify_token_returns_success_and_raises_on_invalid -v

# Run tests matching a pattern
pytest auth/tests/ -k "password" -v
```

### Skip Tests Without Supabase

The Supabase integration tests are automatically skipped if `DATABASE_URL` is not set or doesn't contain "postgresql". To explicitly skip them:

```bash
pytest auth/tests/ -v -m "not requires_supabase"
```

### Run with Coverage

```bash
# Install coverage
pip install pytest-cov

# Run with coverage report
pytest auth/tests/ --cov=auth --cov-report=html

# Open coverage report
# Windows: start htmlcov/index.html
# Mac: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

### Run Tests in Docker

The tests can also be run inside the Docker container:

```bash
# Build the auth service
docker compose build auth

# Run tests
docker compose run --rm auth pytest tests/ -v
```

## Test Categories

### Database Connectivity Tests
- `test_database_url_from_environment()` - Validates DATABASE_URL configuration
- `test_sqlite_connection()` - Tests basic SQLite connectivity
- `test_supabase_connection()` - Tests Supabase PostgreSQL connection
- `test_database_pool_configuration()` - Validates connection pooling

### Model Tests
- `test_user_model_creation()` - User model CRUD operations
- `test_apikey_model_creation()` - API key model operations
- `test_password_reset_token_model()` - Password reset token operations

### Security Tests
- `test_password_hashing()` - Password hashing and verification
- `test_jwt_token_creation_and_decoding()` - JWT token lifecycle
- `test_api_key_hashing()` - API key hashing validation

### API/Proxy Endpoint Tests
- Sync route delegation for register/login/logout/me/refresh
- Password reset request/confirm
- Verify token success and invalid-token handling

### Supabase Integration Tests
- Connection validation and DNS resolution
- URL encoding verification for special characters
- Transaction handling
- Performance benchmarking
- Error recovery

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | For Supabase tests | None |
| `AUTH_DB_URL` | Override for test database | No | `sqlite:///./test_auth.db` |
| `AUTH_JWT_SECRET` | JWT secret key | No | `dev-insecure-secret-change` |
| `AUTH_JWT_EXPIRE_MINUTES` | JWT expiration time | No | `60` |
| `AUTH_RESET_EXPIRE_MINUTES` | Password reset token expiration | No | `30` |

## Troubleshooting

### Supabase Connection Issues

If Supabase tests fail with DNS resolution errors:

1. **Verify URL encoding of special characters in password:**
   ```
   ^ = %5E
   ! = %21
   @ = %40
   # = %23
   $ = %24
   % = %25
   & = %26
   ```

2. **Use IPv4 pooler connection instead of direct connection:**
   ```
   # Correct (pooler, port 6543)
   postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
   
   # Avoid (direct, may be IPv6 only)
   postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres
   ```

3. **Check network connectivity:**
   ```bash
   # Test DNS resolution
   nslookup aws-0-us-east-1.pooler.supabase.com
   
   # Test connection
   psql "postgresql://postgres.PROJECT:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres"
   ```

### Test Database Cleanup

Test databases are automatically cleaned up. If you need to manually clean:

```bash
# Remove SQLite test database
rm test_auth.db test_connectivity.db

# Clean up pytest cache
rm -rf .pytest_cache __pycache__
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Auth Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd auth
        pip install -e ".[dev]"
    
    - name: Run tests without Supabase
      run: DATABASE_URL=sqlite:///./auth.db pytest auth/tests/ -v
    
    - name: Run Supabase tests
      if: ${{ secrets.DATABASE_URL }}
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
      run: pytest auth/tests/test_supabase_integration.py -v
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/core/engines.html#testing-with-sqlite)
- [Supabase Documentation](https://supabase.com/docs)
