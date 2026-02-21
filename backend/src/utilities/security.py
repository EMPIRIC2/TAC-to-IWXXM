"""JWT security and authentication utilities via Auth Service proxy."""
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Load .env file if it exists (for development)
env_file = Path(__file__).parent.parent.parent.parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value

# Configuration - Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8003")
# Development mode - bypass auth verification
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "").lower() in ("true", "1", "yes")

logger.info(f"Security module loaded: DISABLE_AUTH={DISABLE_AUTH}, env value='{os.getenv('DISABLE_AUTH', '')}'")

security = HTTPBearer(auto_error=False)


async def verify_supabase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Verify JWT token via Auth Service proxy.
    
    The auth service validates the token with Supabase and returns user info.
    In development mode (DISABLE_AUTH=true), this is bypassed for testing.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        Decoded user information from auth service (or mock development data)

    Raises:
        HTTPException: If token is invalid, expired, or missing (unless in dev mode)
    """
    # Check for auth bypass at runtime (in case env var changed after module load)
    disable_auth_runtime = os.getenv("DISABLE_AUTH", "").lower() in ("true", "1", "yes")
    
    logger.info(
        "[AUTH] verify_supabase_token disable_auth=%s runtime_disable_auth=%s has_credentials=%s",
        DISABLE_AUTH,
        disable_auth_runtime,
        credentials is not None,
    )
    
    # Development mode bypass
    if DISABLE_AUTH or disable_auth_runtime:
        logger.info("Auth bypassed (development mode)")
        # Use actual admin user from environment, or fallback to dev user
        admin_user_id = os.getenv("ADMIN_USER_ID", "dev-user-12345")
        admin_email = os.getenv("ADMIN_EMAIL", "dev@example.com")
        return {
            "sub": admin_user_id,  # Standard JWT claim
            "user_id": admin_user_id,  # Also include for compatibility
            "email": admin_email,
            "authenticated": False,
            "environment": "development"
        }
    
    if not credentials:
        logger.warning("[AUTH] Missing authorization credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials"
        )
        
    token = credentials.credentials
    logger.info(
        "[AUTH] Token received scheme=%s token_length=%s",
        credentials.scheme,
        len(token),
    )

    try:
        # Call auth service to verify token
        logger.info("[AUTH] Verifying token via auth service url=%s", AUTH_SERVICE_URL)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            logger.info("[AUTH] Auth service verify response status=%s", response.status_code)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.warning("[AUTH] Auth service rejected token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            else:
                logger.error("[AUTH] Auth service unexpected status=%s", response.status_code)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Auth service error"
                )
                
    except httpx.TimeoutException:
        logger.error("[AUTH] Auth service timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service timeout"
        )
    except httpx.ConnectError:
        logger.error("[AUTH] Auth service connection failure")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to auth service"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[AUTH] Unexpected token verification failure: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification failed: {str(e)}"
        )


# Legacy functions kept for backwards compatibility but now proxy through auth service
async def fetch_jwks() -> Dict[str, Any]:
    """Legacy function - now handled by auth service."""
    raise NotImplementedError("JWKS fetching now handled by auth service proxy")


__all__ = ["verify_supabase_token", "fetch_jwks"]
