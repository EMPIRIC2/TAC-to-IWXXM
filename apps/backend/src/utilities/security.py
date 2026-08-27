"""JWT gate for logged-in work-sessions (F31 / ADR-033) - JWKS-only verify."""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from metar_auth.jwks import JwtVerificationError, verify_access_token

from metar_shared.supabase_env import get_supabase_url

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=True)

# Product convert/lint/validate remain public - this flag is not used to bypass JWT
# on work-sessions (Auth-kept for long-term storage).
DISABLE_AUTH = False


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """
    Verify Bearer JWT via Supabase Auth JWKS (no HS256 secret path).

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Authorization Bearer token from the request.

    Returns
    -------
    dict[str, Any]
        Decoded claims (must include ``sub``).

    Raises
    ------
    HTTPException
        401 when the token is missing/invalid; 503 when Auth URL env is missing.
    """
    supabase_url = get_supabase_url()
    jwks_url = (os.environ.get("SUPABASE_JWKS_URL") or "").strip() or None
    if not supabase_url and not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth verify unavailable - set SUPABASE_URL or SUPABASE_JWKS_URL",
        )
    try:
        claims = verify_access_token(
            credentials.credentials,
            jwks_url=jwks_url,
            supabase_url=supabase_url or None,
        )
    except JwtVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if not claims.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing sub claim",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


async def fetch_jwks() -> dict[str, Any]:
    """
    Compatibility stub - product verify uses ``verify_access_token`` (JWKS URL).

    Raises
    ------
    NotImplementedError
        Always; callers should use ``metar_auth.jwks.verify_access_token``.
    """
    raise NotImplementedError("Use metar_auth.jwks.verify_access_token (ADR-033 JWKS-only)")


__all__ = ["DISABLE_AUTH", "fetch_jwks", "security", "verify_supabase_token"]
