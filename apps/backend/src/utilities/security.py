"""JWT security and authentication utilities via inlined auth package."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from auth.supabase_proxy import get_supabase_proxy
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# Load .env file if it exists (for development)
env_file = Path(__file__).parent.parent.parent.parent / ".env"
if env_file.exists():  # pragma: no cover
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value

# Development mode - bypass auth verification
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "").lower() in ("true", "1", "yes")

logger.info(f"Security module loaded: DISABLE_AUTH={DISABLE_AUTH}, env value='{os.getenv('DISABLE_AUTH', '')}'")


def _is_production() -> bool:
    """True when running in a production deployment (``METAR_CONFIG_ENV=prod``)."""
    return os.getenv("METAR_CONFIG_ENV", "local").strip().lower() in ("prod", "production")


security = HTTPBearer(auto_error=False)


async def verify_supabase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Verify JWT token via the inlined auth package (Supabase proxy).

    In development mode (DISABLE_AUTH=true), this is bypassed for testing.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        Decoded user information from Supabase (or mock development data)

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

    # Development mode bypass — never honoured in production. A stray
    # DISABLE_AUTH=true in a prod deployment must not silently disable auth or
    # substitute the non-UUID dev user id (BUG-2026-06-25).
    bypass_requested = DISABLE_AUTH or disable_auth_runtime
    if bypass_requested and _is_production():
        logger.warning(
            "[AUTH] DISABLE_AUTH is set in a production environment "
            "(METAR_CONFIG_ENV=prod) — ignoring bypass and enforcing real auth"
        )
        bypass_requested = False

    if bypass_requested:
        logger.info("Auth bypassed (development mode)")
        # Use actual admin user from environment, or fallback to dev user
        admin_user_id = os.getenv("ADMIN_USER_ID", "dev-user-12345")
        admin_email = os.getenv("ADMIN_EMAIL", "dev@example.com")
        return {
            "sub": admin_user_id,  # Standard JWT claim
            "user_id": admin_user_id,  # Also include for compatibility
            "email": admin_email,
            "authenticated": False,
            "environment": "development",
        }

    if not credentials:
        logger.warning("[AUTH] Missing authorization credentials")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization credentials")

    token = credentials.credentials
    logger.info(
        "[AUTH] Token received scheme=%s token_length=%s",
        credentials.scheme,
        len(token),
    )

    try:
        proxy = get_supabase_proxy()
    except ValueError as exc:
        logger.error("[AUTH] Auth package not configured: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication not configured",
        ) from exc

    try:
        logger.info("[AUTH] Verifying token via inlined auth package")
        if not proxy.verify_token(token):
            logger.warning("[AUTH] Invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user_info = proxy.get_user(token)
        return {
            "sub": user_info["id"],
            "user_id": user_info["id"],
            "email": user_info["email"],
            "authenticated": True,
            "metadata": user_info.get("metadata", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[AUTH] Unexpected token verification failure: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Token verification failed: {str(e)}"
        )


# Legacy functions kept for backwards compatibility but now handled inline
async def fetch_jwks() -> Dict[str, Any]:
    """Legacy function - JWKS validation is handled by the auth package."""
    raise NotImplementedError("JWKS fetching now handled by auth package")


__all__ = ["verify_supabase_token", "fetch_jwks"]
