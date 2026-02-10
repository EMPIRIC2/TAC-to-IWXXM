# METAR to IWXXM Converter

Modern React-based web application with microservices backend to decode METAR/SPECI TAC and serialize IWXXM XML using the GIFTs submodule.

## Architecture

This project uses a **microservices architecture** with an authentication middleware proxy:

```
Frontend (Port 8000)
    ↓
Auth Service (Port 8002) ← Supabase
    ↓                        (Credentials: server-side only)
Backend (Port 8001)
```

**Benefits:**
- ✅ Supabase credentials never exposed to frontend
- ✅ Centralized auth logic and monitoring
- ✅ Easy to add rate limiting, logging, custom claims
- ✅ Flexible auth provider switching

## Features

- **Authentication**: User registration, login via Supabase through auth middleware
- **Drag & drop** multiple `.tac` / `.txt` METAR files
- **Manual METAR text input**
- **Batch conversion** to IWXXM XML (returned as text for convenience)
- **Copy / download** each result
- **ZIP batch download** endpoint for multiple conversions
- **Microservices architecture** with auth proxy, backend API, and React frontend
- **Token-based security** - Backend validates tokens via auth service

## Quick Start with Docker Compose (Recommended)

### 1. Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- Git
- Supabase account (free tier available)

### 2. Clone and Start Services

```bash
# Clone the repository with submodules
git clone --recurse-submodules <repository-url>
cd metar-to-IWXXM

# If already cloned, initialize submodules
git submodule update --init --recursive

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase credentials:
#   SUPABASE_URL=https://your-project.supabase.co
#   SUPABASE_ANON_KEY=your-anon-key

# Start all services (auth middleware, backend, frontend)
docker-compose up --build
```

### 3. Access the Application

1. Open your browser to <http://localhost:8000>
2. You'll be redirected to the login page
3. Click "Register" to create a new account
4. Fill in your details (email, password, name)
5. Click "Register" - uses Supabase via auth service
6. Login with your credentials
7. Start converting METAR reports to IWXXM XML!

### 4. Service Endpoints

- **Frontend (React UI)**: <http://localhost:8000>
- **Backend API**: <http://localhost:8001>
  - API Docs: <http://localhost:8001/docs>
  - Health: <http://localhost:8001/health>
- **Auth Service (Middleware)**: <http://localhost:8002>
  - Health: <http://localhost:8002/health>

### 5. Stop Services

```bash
# Stop services (keep volumes)
docker-compose down

# Stop and remove everything (including database volumes)
docker-compose down -v
```

## Architecture Details

See [docs/AUTH_MIDDLEWARE_ARCHITECTURE.md](docs/AUTH_MIDDLEWARE_ARCHITECTURE.md) for detailed documentation on:
- How the auth middleware works
- Token flow between frontend, backend, and Supabase
- API endpoint reference
- Migration guide from direct Supabase

## Development Setup (Local)

### Prerequisites
- Python 3.9+ (3.12 recommended)
- Node.js 18+ (for frontend)
- `uv` package manager (optional but recommended)

### 1. Clone and Initialize

```bash
git clone --recurse-submodules <repository-url>
cd metar-to-IWXXM
git submodule update --init --recursive
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src

# Run server
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
```

### 3. Auth Service Setup

```bash
cd auth

# Create virtual environment (or use shared one)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Set environment variables
cp .env.example .env
# Edit .env with Supabase credentials

# Run server
python -m uvicorn auth.src.__main__:app --reload --host 0.0.0.0 --port 8002
```

### 4. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend will be available at <http://localhost:5173> (Vite dev server)

## Configuration

### Environment Variables

**Root `.env` file** (for docker-compose):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
VITE_AUTH_SERVICE_URL=http://localhost:8002
VITE_APP_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8001
```

**Auth Service** (auth/.env):
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
FRONTEND_BASE_URL=http://localhost:8000
```

**Backend** (backend/.env, if needed):
```bash
AUTH_SERVICE_URL=http://localhost:8002
```

**Frontend** (frontend/.env):
```bash
VITE_AUTH_SERVICE_URL=http://localhost:8002
VITE_BACKEND_URL=http://localhost:8001
```

## Testing

### Backend Unit Tests

```bash
cd backend
pytest tests/ -v --cov=src --cov-fail-under=90
```

### Auth Service Tests

```bash
cd auth
python -m pytest tests/ -v --cov=src
```

### Integration Tests

```bash
# From root directory
pytest tests/ -v
```

## Project Structure

```
metar-to-IWXXM/
├── auth/                  # Authentication service (Supabase proxy)
│   ├── src/
│   │   ├── __main__.py   # FastAPI app
│   │   ├── api_supabase.py # API endpoints
│   │   └── supabase_proxy.py # Supabase client wrapper
│   └── tests/            # Auth service tests
├── backend/               # METAR conversion backend
│   ├── src/
│   │   ├── api.py        # FastAPI app
│   │   ├── utilities/    # Conversion and security
│   │   └── schemas/      # Data models
│   └── tests/            # Backend tests
├── frontend/              # React web application
│   ├── src/
│   │   ├── app/          # Main app component
│   │   ├── utils/        # Utilities (authService.ts for auth)
│   │   └── styles/       # CSS/Tailwind
│   └── tests/            # Frontend tests
├── GIFTs/                 # Git submodule for IWXXM generation
├── docs/                  # Documentation
│   └── AUTH_MIDDLEWARE_ARCHITECTURE.md
├── tests/                 # Root integration tests
├── docker-compose.yml     # Multi-container orchestration
└── README.md              # This file
```

## Key Technologies

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, Vitest
- **Backend**: FastAPI, SQLAlchemy, GIFTs submodule
- **Auth Service**: FastAPI, Supabase, CORS middleware
- **Database**: Supabase (Postgres)
- **Containerization**: Docker, Docker Compose
- **Package Management**: uv (Python), npm (Node.js)

## Troubleshooting

### Docker services won't start
1. Ensure `.env` file exists with Supabase credentials
2. Check Docker is running: `docker ps`
3. View logs: `docker-compose logs -f`

### Auth service connection errors
1. Verify SUPABASE_URL and SUPABASE_ANON_KEY in `.env`
2. Check auth service is healthy: `curl http://localhost:8002/health`
3. Ensure `VITE_AUTH_SERVICE_URL` is set correctly in frontend build

### Backend can't connect to auth service
1. In Docker, use `AUTH_SERVICE_URL=http://auth:8000` (service name, not localhost)
2. Locally, use `AUTH_SERVICE_URL=http://localhost:8002`

### Frontend CORS errors
1. Auth service has CORS enabled for all origins (development)
2. For production, restrict origins in `auth/src/__main__.py`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test: `pytest`, `npm test`
4. Submit a pull request

## Documentation

- **Frontend (GUI)**: <http://localhost:8000>
- **Backend API**: <http://localhost:8001>
- **Auth Service**: <http://localhost:8002>

### 5. Stop Services

```powershell
# Stop services
docker-compose down

# Stop and remove volumes (clears auth database)
docker-compose down -v
```

## Development Setup (Local)

### 1. Create a virtual environment (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Or use `uv` for faster package management:

```powershell
uv venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

Install each component in editable mode:

```powershell
# Install auth service
cd auth
uv pip install -e .
cd ..

# Install backend
cd backend
uv pip install -e .
cd ..

# Install frontend dependencies (Node.js/npm required)
cd frontend
npm install
cd ..
```

### 3. Run Services Manually

Terminal 1 - Auth Service:

```powershell
cd auth
python -m uvicorn auth.__main__:app --host 0.0.0.0 --port 8002
```

Terminal 2 - Backend Service:

```powershell
cd backend
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8001
```

Terminal 3 - Frontend Service:

```powershell
cd frontend
npm run dev
```

The frontend will start at <http://localhost:5173> (Vite default port).

**Note**: For proper API integration, you may need to configure the frontend to proxy requests to the backend and auth services.

### 4. Configure Environment Variables

For local development, create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./auth.db
FRONTEND_BASE_URL=http://localhost:8000
BACKEND_URL=http://localhost:8001
AUTH_URL=http://localhost:8002
```

## Architecture

The application is split into three microservices:

1. **Auth Service** (`auth/`): User authentication, JWT tokens, API keys, password reset
2. **Backend Service** (`backend/`): METAR to IWXXM conversion logic (GIFTs integration)
3. **Frontend Service** (`frontend/`): React/Vite web interface with nginx for production

### Authentication Flow

1. User registers/logs in via the React frontend
2. Auth service issues JWT token
3. Token stored in browser storage (managed by Supabase client)
4. Token sent with each API request in `Authorization` header
5. Frontend validates token client-side; backend validates on conversion requests

## API Usage

### Programmatic Use

```python
from backend.conversion import convert_metar_tac

xml = convert_metar_tac("METAR KJFK 231751Z 18012KT 10SM FEW040 SCT120 BKN250 15/07 A3005")
print(xml[:200])
```

### API Endpoints

#### Auth Service (`/auth/*`)

- `POST /auth/register` - Create new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile
- `POST /auth/apikeys` - Create API key
- `GET /auth/apikeys` - List API keys
- `DELETE /auth/apikeys/{id}` - Revoke API key

#### Backend Service (`/api/*`)

- `POST /api/convert` - Convert METAR(s) to IWXXM XML
- `POST /api/convert-zip` - Convert and download as ZIP

#### Health Checks

- `GET /health` - All services support health checks

## Troubleshooting

### Issue: "Nothing showing on webpage"

**Cause**: Authentication not configured or user not logged in.

**Solution**:

1. Ensure all three services are running (check `docker-compose up` output)
2. Navigate to <http://localhost:8000>
3. You should be redirected to login page
4. Register a new account if you don't have one
5. Login to access the converter

### Issue: "Connection refused" errors

**Cause**: Services not running or ports blocked.

**Solution**:

```powershell
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs auth

# Restart services
docker-compose restart
```

### Issue: "Invalid token" errors

**Cause**: JWT token expired or auth service restarted.

**Solution**: Logout and login again to get a fresh token.

## Roadmap

- ✅ JWT authentication with user registration
- ✅ ZIP batch download endpoint
- ✅ Microservices architecture with Docker Compose
- 🔄 Editable packaging improvements
- 🔄 Optional IWXXM schema validation with `lxml`
- 📋 API key authentication for programmatic access
- 📋 Password reset email integration

## Contributing

Please use `uv` for package management as specified in `.github/copilot-instructions.md`. Ensure all dependencies are listed in `pyproject.toml` files.

## License

MIT
