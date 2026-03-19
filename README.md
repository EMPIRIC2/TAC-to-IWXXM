# METAR to IWXXM Converter

[![CI/CD](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/ci-cd.yml)
[![E2E](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/e2e-tests.yml)
[![codecov](https://codecov.io/gh/joseph-c-mcguire/metar-to-IWXXM/graph/badge.svg)](https://codecov.io/gh/joseph-c-mcguire/metar-to-IWXXM)

Modern React-based web application with microservices backend to decode METAR/SPECI TAC and serialize IWXXM XML using the GIFTs submodule.

## Features

- ✅ **Authentication**: User registration, login via Supabase through auth middleware
- ✅ **Drag & drop** multiple `.tac` / `.txt` METAR files
- ✅ **Manual METAR text input**
- ✅ **Batch conversion** to IWXXM XML (returned as text for convenience)
- ✅ **Copy / download** each result
- ✅ **ZIP batch download** endpoint for multiple conversions
- ✅ **Microservices architecture** with auth proxy, backend API, and React frontend
- ✅ **Token-based security** - Backend validates tokens via auth service

## 📖 For Developers

**→ Complete setup and development guide:** [DEVELOPMENT.md](DEVELOPMENT.md)

This includes:
- Quick start (5 minutes with Docker)
- Manual setup instructions
- Architecture details
- Testing & troubleshooting
- Deployment guide

## Architecture

This project uses a **microservices architecture** with an authentication middleware proxy:

```
Frontend (Port 5173 - dev, 8000 - prod)
    ↓ (HTTP/HTTPS)
Auth Service (Port 8003)
    ↓ (Server-to-Server)
Supabase Backend
    (Credentials: server-side only)
    ↓
Backend Service (Port 8001)
    ↓
GIFTs Library (IWXXM Generation)
```

**Key Benefits:**
- ✅ Supabase credentials never exposed to frontend
- ✅ Centralized auth logic and monitoring
- ✅ Easy to add rate limiting, logging, custom claims
- ✅ Flexible auth provider switching

See [docs/AUTH_MIDDLEWARE_ARCHITECTURE.md](docs/AUTH_MIDDLEWARE_ARCHITECTURE.md) for detailed documentation.

## Quick Start with Docker Compose (Recommended)

### Prerequisites
- Docker Desktop or Docker Engine with Docker Compose
- Git
- Supabase account (free tier available at https://supabase.com)

### Setup (5 minutes)

```bash
# Clone the repository with submodules
git clone --recurse-submodules <repository-url>
cd metar-to-IWXXM

# Copy environment template and add your Supabase credentials
cp .env.example .env

# Edit .env with your Supabase credentials:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_ANON_KEY=your-anon-key-here
```

### Run Services

```bash
# Start all services (will download images on first run)
docker-compose up --build

# In a separate terminal, check services are healthy
curl http://localhost:8003/health  # Auth service
curl http://localhost:8001/health  # Backend service
curl http://localhost:5173         # Frontend (should return HTML)
```

### Access the Application

1. Open your browser to http://localhost:5173 (or http://localhost:8000 if running production build)
2. You'll be redirected to the login page
3. Click "Register" to create a new account
4. Fill in your details (email, password, name, optional username)
5. Submit - uses Supabase via auth service
6. Login with your credentials
7. **Start converting METAR reports to IWXXM XML!**

### Service Endpoints

- **Frontend (React UI)**: http://localhost:8000
- **Backend API**: http://localhost:8001
  - API Docs (Swagger): http://localhost:8001/docs
  - OpenAPI JSON: http://localhost:8001/openapi.json
- **Auth Service (Middleware)**: http://localhost:8002
  - Health: http://localhost:8002/health

### Stop Services

```bash
# Stop services (keep data volumes)
docker-compose down

# Stop and remove everything (clears all data)
docker-compose down -v
```

## Development Setup (Local)

### Prerequisites
- Python 3.8+ (3.10+ recommended)
- Node.js 18+ (for frontend)
- Git with submodules support
- uv package manager (optional but recommended)

### Clone and Initialize

```bash
git clone --recurse-submodules <repository-url>
cd metar-to-IWXXM
git submodule update --init --recursive
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate.ps1  # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Or with uv
uv venv
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src --cov-fail-under=90

# Run server (with auto-reload)
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
```

### Auth Service Setup

```bash
cd auth

# Create virtual environment (or use shared one)
python -m venv .venv
source .venv/bin/activate
# or with uv
uv venv

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with Supabase credentials

# Run tests
pytest tests/ -v --cov=src

# Run server
python -m uvicorn src.__main__:app --reload --host 0.0.0.0 --port 8002
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional for local dev)
cp .env.example .env.local

# Run dev server
npm run dev  # Opens at http://localhost:5173
```

## Configuration

### Environment Variables

**Root `.env` file** (for Docker Compose):
```env
# Supabase credentials (server-side, never exposed to frontend)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Frontend configuration
VITE_AUTH_SERVICE_URL=http://localhost:8002
VITE_APP_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8001
```

**Auth Service** (`auth/.env`):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
FRONTEND_BASE_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```env
# For Docker: use auth service name instead of localhost
AUTH_SERVICE_URL=http://auth:8002
# For local development:
# AUTH_SERVICE_URL=http://localhost:8002
```

**Frontend** (`frontend/.env` for local development):
```env
VITE_AUTH_SERVICE_URL=http://localhost:8002
VITE_BACKEND_URL=http://localhost:8001
```

### Supabase Configuration

1. Create a Supabase account at https://supabase.com
2. Create a new project
3. As soon as the project is created, note down:
   - **Project URL**: Found in Settings → API under "API URL"
   - **Anon Key**: Found in Settings → API under "Project API keys"
4. Add these to your `.env` file

## Testing

### Backend Tests

```bash
cd backend

# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run based on marker
pytest tests/ -v -m "not integration"
```

### Auth Service Tests

```bash
cd auth

# Run all tests
python -m pytest tests/ -v --cov=src

# Current status: 14 passed, 7 skipped
# (Skipped tests require Supabase backend configuration)
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Integration Tests

```bash
# From root directory (requires all three services running locally)
pytest tests/ -v

# Run specific integration tests
pytest tests/test_backend_auth_service_integration.py -v
```

## Project Structure

```
metar-to-IWXXM/
├── .github/
│   └── copilot-instructions.md    # Development guidelines
├── auth/                           # Authentication service
│   ├── src/
│   │   ├── __main__.py            # FastAPI app, CORS config
│   │   ├── api_supabase.py        # API endpoints (register, login, etc.)
│   │   ├── supabase_proxy.py      # Supabase client wrapper
│   │   └── __init__.py
│   ├── tests/
│   │   ├── conftest.py            # Test configuration
│   │   └── test_auth_middleware.py # API endpoint tests
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── README.md
├── backend/                        # METAR conversion backend
│   ├── src/
│   │   ├── api.py                 # FastAPI app, route definitions
│   │   ├── conversion.py          # METAR to IWXXM logic
│   │   ├── utilities/
│   │   │   ├── security.py        # Token verification via auth service
│   │   │   └── __init__.py
│   │   ├── schemas/               # Pydantic models
│   │   └── __init__.py
│   ├── tests/                     # Unit and integration tests
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── README.md
├── frontend/                       # React web application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/auth/   # Login, Register, etc.
│   │   │   └── App.tsx            # Main component
│   │   ├── utils/
│   │   │   └── authService.ts     # Auth client library
│   │   └── styles/                # CSS/Tailwind styles
│   ├── tests/                     # Vitest unit tests
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   ├── nginx.conf                 # Production server config
│   └── README.md
├── GIFTs/                         # Git submodule
│   └── gifts/                      # KHTML to IWXXM conversion
├── docs/
│   ├── AUTH_MIDDLEWARE_ARCHITECTURE.md  # Detailed auth architecture
│   ├── SUPABASE_INTEGRATION.md          # Supabase setup guide
│   └── API.md                           # API documentation
├── tests/                         # Root integration tests
│   ├── test_backend_auth_service_integration.py
│   └── ... (other integration tests)
├── scripts/                       # Utility scripts
│   ├── launch_api.sh              # Launch script
│   └── ... (other scripts)
├── notebooks/                     # Jupyter notebooks for testing
│   └── testing.ipynb
├── docker-compose.yml             # Multi-container orchestration
├── .env.example                   # Environment template
├── README.md                      # This file
├── LICENSE
└── Makefile (optional)
```

## Key Technologies

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, Vitest
- **Backend API**: FastAPI, SQLAlchemy 2.0, Python 3.8+
- **Auth Service**: FastAPI, Supabase Python SDK, CORS middleware
- **Database**: Supabase Postgres (managed)
- **Conversion**: GIFTs submodule (KHTML to IWXXM)
- **Containerization**: Docker, Docker Compose
- **Package Management**: uv (Python), npm (Node.js)
- **Testing**: pytest, pytest-cov, pytest-asyncio, Vitest

## Troubleshooting

### CI/CD Troubleshooting

#### GIFTs submodule checkout fails in GitHub Actions

If a workflow fails with errors like `did not contain <sha>` or `not our ref`, run:

```bash
git submodule sync --recursive
git submodule update --init GIFTs
git -C GIFTs fetch --tags --force origin
git submodule update --init GIFTs
git submodule status GIFTs
```

Use a non-shallow fetch for `GIFTs` in CI. The main workflow at `.github/workflows/ci-cd.yml` now retries GIFTs initialization with an explicit remote fetch.

#### Coverage checks fail in PRs

Coverage is gated per service through Codecov (not combined-only):

- `backend` ≥ 75%
- `auth` ≥ 75%
- `frontend` ≥ 75%
- `gifts` ≥ 75%

Policy source of truth is `.codecov.yml`, and uploads happen in `.github/workflows/ci-cd.yml`.

### Docker Troubleshooting

#### Services won't start
```bash
# Check if .env exists with credentials
ls -la .env

# Check Docker is running
docker ps

# View detailed logs
docker-compose logs -f

# Rebuild images
docker-compose down && docker-compose up --build
```

#### Port conflicts
```bash
# Check what's using ports 8000, 8001, 8002
lsof -i :8000      # Frontend
lsof -i :8001      # Backend
lsof -i :8002      # Auth service

# On Windows:
netstat -ano | findstr :8000
```

### Authentication Troubleshooting

#### "Invalid API key" during startup
- ✅ Check SUPABASE_URL format: `https://...supabase.co`
- ✅ Check SUPABASE_ANON_KEY is not empty
- ✅ Keys must be from same Supabase project
- ✅ Regenerate keys in Supabase dashboard if needed

#### Auth service connection errors
```bash
# Check auth service is healthy
curl http://localhost:8002/health

# Check auth service can reach Supabase
docker-compose logs auth | grep -i "supabase\|error\|connection"

# Verify SUPABASE_* credentials in auth service
docker-compose exec auth env | grep SUPABASE
```

#### Backend can't connect to auth service
- In Docker: Use `AUTH_SERVICE_URL=http://auth:8002` (service name from docker-compose.yml)
- Locally: Use `AUTH_SERVICE_URL=http://localhost:8002`
- Check network: `docker-compose logs backend | grep -i "auth\|error"`

#### Frontend CORS errors
```
Access to XMLHttpRequest blocked by CORS policy
```
- ✅ Auth service has CORS enabled for all origins (development mode)
- ✅ For production, restrict origins in `auth/src/__main__.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Production domains
    ...
)
```

#### "Redirect loop" in frontend
- Check VITE_AUTH_SERVICE_URL is set correctly
- Ensure auth service is running and healthy
- Clear browser cookies/localStorage if tokens are corrupted

### Development Troubleshooting

#### "Module not found" in backend
```bash
cd backend
# Reinstall in editable mode
pip install -e .
```

#### "Cannot find package" in frontend
```bash
cd frontend
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Tests failing
```bash
# Clear pytest cache
pytest --cache-clear tests/

# Run with verbose output
pytest tests/ -vv

# Run single test
pytest tests/test_file.py::test_function -vv
```

## Contributing

Please use `uv` for package management for Python. Ensure:
1. All Python dependencies are listed in `pyproject.toml`
2. Run tests before submitting PR: `pytest tests/ -v`
3. For frontend: Run `npm test` and `npm run lint`
4. Use descriptive commit messages

For detailed guidelines, see `.github/copilot-instructions.md`.

## API Usage

### Convert METAR to IWXXM

**Via Frontend UI**: Upload `.tac`/`.txt` files or paste METAR text

**Via Backend API**:
```bash
curl -X POST "http://localhost:8001/api/convert" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"metar": "METAR KJFK 231751Z 18012KT 10SM FEW040 SCT120 BKN250 15/07 A3005"}'
```

**Batch Download**:
```bash
curl -X POST "http://localhost:8001/api/convert-zip" \
  -H "Authorization: Bearer <your-token>" \
  -F "files=@file1.tac" \
  -F "files=@file2.tac" \
  --output results.zip
```

### API Documentation

Live API docs available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json

## Deployment

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run in production mode
docker-compose -f docker-compose.yml up -d

# Monitor
docker-compose logs -f
docker-compose stats
```

### Environment Variables for Production

```env
# Use production Supabase project
SUPABASE_URL=https://prod.supabase.co
SUPABASE_ANON_KEY=prod-anon-key

# Use production URLs
VITE_AUTH_SERVICE_URL=https://auth.yourdomain.com
VITE_BACKEND_URL=https://api.yourdomain.com
VITE_APP_URL=https://yourdomain.com

# Restrict CORS origins (in auth/src/__main__.py)
CORS_ORIGINS=["https://yourdomain.com"]
```

## Roadmap

- ✅ JWT authentication with Supabase
- ✅ Auth middleware proxy pattern
- ✅ Microservices architecture
- ✅ ZIP batch download
- 🔄 Enhanced error messages
- 📋 API key authentication for programmatic access
- 📋 Email-based password reset
- 📋 Rate limiting per user
- 📋 Admin dashboard for user management

## License

MIT - See LICENSE file for details

## Support

For issues and questions:
1. Check [troubleshooting](#troubleshooting) section
2. Review [docs/AUTH_MIDDLEWARE_ARCHITECTURE.md](docs/AUTH_MIDDLEWARE_ARCHITECTURE.md)
3. Check existing [GitHub Issues](https://github.com/your-repo/issues)
4. Create new issue with detailed description

## Additional Resources

- [Supabase Docs](https://supabase.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [GIFTs Documentation](https://github.com/wmo-im/GIFTs)
- [IWXXM Standard](https://github.com/wmo-im/IWXXM)
