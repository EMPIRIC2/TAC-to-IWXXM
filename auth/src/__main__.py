"""Entry point for running the auth service via `python -m auth`."""
import logging
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

from auth.api_supabase import router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Auth service __main__ module loaded")
logger.debug(f"SUPABASE_URL from env: {os.getenv('SUPABASE_URL', 'NOT SET')}")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AUTH SERVICE STARTING UP")
    logger.info("=" * 80)
    logger.info("Service Configuration:")
    logger.info(f"  Port: 8003")
    logger.info(f"  Host: 0.0.0.0 (all interfaces)")
    logger.info("")
    logger.info("Environment Variables:")
    logger.info(f"  SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT SET')}")
    logger.info(f"  SUPABASE_ANON_KEY: {'SET (' + os.getenv('SUPABASE_ANON_KEY')[:20] + '...)' if os.getenv('SUPABASE_ANON_KEY') else 'NOT SET'}")
    logger.info(f"  FRONTEND_BASE_URL: {os.getenv('FRONTEND_BASE_URL', 'NOT SET')}")
    logger.info("")
    logger.info("CORS Configuration:")
    logger.info("  Allowed Origins:")
    for origin in ["http://localhost:8000", "http://localhost:3000", "http://localhost:8001", "http://localhost:8002"]:
        logger.info(f"    - {origin}")
    logger.info("  Allow Credentials: True")
    logger.info("  Allow Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD")
    logger.info("  Allow Headers: *")
    logger.info("")
    logger.info("Available Endpoints:")
    logger.info("  POST   /auth/register")
    logger.info("  POST   /auth/login")
    logger.info("  POST   /auth/logout")
    logger.info("  GET    /auth/me")
    logger.info("  POST   /auth/refresh")
    logger.info("  POST   /auth/password-reset/request")
    logger.info("  POST   /auth/password-reset/confirm")
    logger.info("  GET    /health")
    logger.info("=" * 80)
    logger.info("✓ AUTH SERVICE READY - Listening for requests...")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("🛑 AUTH SERVICE SHUTTING DOWN")


app = FastAPI(
    title="METAR Auth Proxy Service",
    version="0.1.0",
    description="Authentication middleware proxy to Supabase",
    lifespan=lifespan
)

logger.info("Initializing Auth Service with CORS middleware...")

# CORS debugging and request logging middleware - FIRST to catch all requests
@app.middleware("http")
async def log_requests_and_cors(request: Request, call_next):
    start_time = time.time()
    
    # Detailed logging for CORS preflight requests
    origin = request.headers.get("origin", "NO-ORIGIN")
    method = request.method
    
    if method == "OPTIONS":
        logger.warning("=" * 80)
        logger.warning(f"🔍 CORS PREFLIGHT REQUEST DETECTED")
        logger.warning(f"  Origin: {origin}")
        logger.warning(f"  Method: {method}")
        logger.warning(f"  Path: {request.url.path}")
        logger.warning(f"  All Headers:")
        for key, value in request.headers.items():
            logger.warning(f"    {key}: {value}")
        logger.warning("=" * 80)
    else:
        # Log normal requests
        logger.info(f"→ [{request.method}] {request.url.path} from {request.client.host}")
        logger.debug(f"  Origin: {origin}")
        logger.debug(f"  Headers: {dict(request.headers)}")
    
    # Process request
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        if method == "OPTIONS":
            logger.warning("=" * 80)
            logger.warning(f"✓ CORS PREFLIGHT RESPONSE")
            logger.warning(f"  Status: {response.status_code}")
            logger.warning(f"  Response Headers:")
            for key, value in response.headers.items():
                if key.lower().startswith("access-control"):
                    logger.warning(f"    {key}: {value}")
            logger.warning("=" * 80)
        else:
            logger.info(f"← [{request.method}] {request.url.path} - {response.status_code} ({duration:.2f}ms)")
        
        return response
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"✗ [{request.method}] {request.url.path} - ERROR: {type(e).__name__}: {str(e)} ({duration:.2f}ms)", exc_info=True)
        raise

# Add CORS middleware AFTER logging (before other middleware)
# CRITICAL: Cannot use "*" with allow_credentials=True
# Must specify exact origins when credentials are enabled
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server (default)
        "http://localhost:8000",      # Frontend production port
        "http://localhost:3000",      # Alternative frontend port
        "http://localhost:8001",      # Backend API
        "http://localhost:8003",      # Auth service (self)
        "http://127.0.0.1:5173",      # Explicit IP versions
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8003",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

logger.info("✓ CORS middleware configured with origins:")
for origin in ["http://localhost:5173", "http://localhost:8000", "http://localhost:3000", "http://localhost:8001", "http://localhost:8003"]:
    logger.info(f"  - {origin}")

app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint for Docker."""
    logger.info("Health check requested")
    return HealthResponse(status="healthy", service="auth", version="0.1.0")


__all__ = ["app"]
