# METAR to IWXXM Converter

Modern React-based web application with microservices backend to decode METAR/SPECI TAC and serialize IWXXM XML using the GIFTs submodule.

## Features

- **Authentication**: Supabase-powered user authentication with JWT tokens
  - Password-based login
  - Magic link (passwordless) authentication
  - Password reset flow
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
- A Supabase account (free tier is sufficient) - [Sign up here](https://supabase.com)

### 2. Set Up Supabase

Follow the detailed guide in [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md) to:
1. Create a Supabase project
2. Get your API keys
3. Configure authentication settings

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:
```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY=your-anon-key-here
```

### 4. Clone and Start Services

```bash
# Clone the repository with submodules
git clone --recurse-submodules https://github.com/joseph-c-mcguire/metar-to-IWXXM.git
cd metar-to-IWXXM

# If already cloned, initialize submodules
git submodule update --init --recursive

# Start all services (auth, backend, frontend)
docker-compose up --build
```

### 5. Access the Application

1. Open your browser to <http://localhost:8000>
2. You'll be redirected to the login page
3. Click "Register" to create a new account
4. Fill in your details:
   - Full Name
   - Email
   - Password (min 8 characters)
5. Check your email for the confirmation link
6. After confirming, login with your credentials
7. Start converting METAR reports to IWXXM XML!


### 6. Service Endpoints

- **Frontend (GUI)**: <http://localhost:8000>
- **Backend API**: <http://localhost:8001>
- **Auth Service**: <http://localhost:8002>

### 7. Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes (clears auth database)
docker-compose down -v
```

## Development Setup (Local)

### 1. Prerequisites

- Python 3.11+
- Node.js 20+
- npm or yarn
- Git
- Supabase account (for authentication)

### 2. Set Up Supabase

Follow the guide in [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md).

### 3. Create a virtual environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

Or use `uv` for faster package management:
```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\Activate.ps1  # Windows
```

### 4. Install dependencies

Install each component in editable mode:

```bash
# Install auth service
cd auth
uv pip install -e .
cd ..

# Install backend
cd backend
uv pip install -e .
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 5. Configure Environment Variables

**For Python services (root directory `.env`):**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials and other settings
```

**For frontend (create `frontend/.env.local`):**
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your Supabase credentials
```

### 6. Run Services Manually

**Terminal 1 - Auth Service:**
```bash
cd auth
python -m uvicorn auth.__main__:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 2 - Backend Service:**
```bash
cd backend
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 3 - Frontend Service:**
```bash
cd frontend
npm run dev
```

The frontend will start at <http://localhost:5173> (Vite default port).

## Architecture

The application is split into three microservices:

1. **Auth Service** (`auth/`): User authentication via Supabase, JWT token validation
2. **Backend Service** (`backend/`): METAR to IWXXM conversion logic (GIFTs integration)
3. **Frontend Service** (`frontend/`): React/Vite web interface with nginx for production

### Authentication Flow

1. User registers/logs in via the React frontend using Supabase Auth
2. Supabase issues JWT access token with PKCE flow
3. Token stored in browser via Supabase client library
4. Token sent with each API request in `Authorization: Bearer <token>` header
5. Backend validates token by verifying JWT signature against Supabase JWKS endpoint
6. Frontend handles session management and automatic token refresh

### Technology Stack

**Frontend:**
- React 19 with TypeScript
- Vite for build tooling
- Supabase JS Client (@supabase/supabase-js)
- React Router for navigation
- React Dropzone for file uploads
- Axios for HTTP requests
- Nginx for production serving and reverse proxy

**Backend:**
- FastAPI (Python) for REST API
- GIFTs library for METAR to IWXXM conversion
- Jose for JWT verification
- HTTPX for async HTTP requests (JWKS fetching)

**Auth Service:**
- FastAPI (Python)
- Supabase for authentication
- PostgreSQL database (via Supabase)

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
