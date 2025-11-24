# METAR to IWXXM Converter

FastAPI-based single-page GUI and utility functions to decode METAR/SPECI TAC and serialize IWXXM XML using the GIFTs submodule.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Drag & drop** multiple `.tac` / `.txt` METAR files
- **Manual METAR text input**
- **Batch conversion** to IWXXM XML (returned as text for convenience)
- **Copy / download** each result
- **ZIP batch download** endpoint for multiple conversions
- **Microservices architecture** with separate auth, backend, and frontend services

## Quick Start with Docker Compose (Recommended)

### 1. Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- Git

### 2. Clone and Start Services

```powershell
# Clone the repository
git clone <repository-url>
cd metar-to-IWXXM

# Start all services (auth, backend, frontend)
docker-compose up
```

### 3. Access the Application

1. Open your browser to <http://localhost:8000>
2. You'll be redirected to the login page
3. Click "Register" to create a new account
4. Fill in your details:
   - Full Name
   - Email
   - Address (optional)
   - Username (min 3 characters)
   - Password (min 8 characters)
5. Click "Register" then login with your credentials
6. Start converting METAR reports to IWXXM XML!

### 4. Service Endpoints

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

# Install GUI
cd gui
uv pip install -e .
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
cd gui
python -m uvicorn gui.__main__:app --host 0.0.0.0 --port 8000
```

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
3. **Frontend Service** (`gui/`): Web interface, static file serving

### Authentication Flow

1. User registers/logs in via the GUI
2. Auth service issues JWT token
3. Token stored in browser `sessionStorage`
4. Token sent with each API request in `Authorization` header
5. GUI validates token client-side and server-side validates on conversion requests

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
