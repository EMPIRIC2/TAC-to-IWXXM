"""JWT security and authentication utilities for Supabase integration."""
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, exceptions
from jose.backends.rsa_backend import RSAKey


# Configuration
SUPABASE_PROJECT_URL = os.getenv(
    "SUPABASE_PROJECT_URL", "https://ktvxijislbtgqapllmuk.supabase.co"
)
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

# In-memory JWKS cache with TTL (1 hour)
_jwks_cache: Dict[str, Any] = {
    "keys": {},
    "last_fetch": 0,
    "ttl": 3600,  # 1 hour in seconds
}

security = HTTPBearer()


async def fetch_jwks() -> Dict[str, Any]:
    """Fetch JWKS from Supabase endpoint with caching."""
    current_time = time.time()
    cache_age = current_time - _jwks_cache["last_fetch"]

    # Check if cache is still valid
    if _jwks_cache["keys"] and cache_age < _jwks_cache["ttl"]:
        return _jwks_cache["keys"]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL, timeout=10.0)
            response.raise_for_status()
            jwks = response.json()

            # Extract keys by kid for quick lookup
            keys_by_kid = {}
            for key_data in jwks.get("keys", []):
                kid = key_data.get("kid")
                if kid:
                    keys_by_kid[kid] = key_data

            # Update cache
            _jwks_cache["keys"] = keys_by_kid
            _jwks_cache["last_fetch"] = current_time

            return keys_by_kid
    except Exception as e:
        # If fetch fails but we have cached keys, use them
        if _jwks_cache["keys"]:
            return _jwks_cache["keys"]
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch JWKS from Supabase",
        ) from e


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Verify Supabase JWT token using RS256 and cached JWKS.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        Decoded JWT payload

    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    token = credentials.credentials

    try:
        # Get unverified header to extract kid (key ID)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID",
            )

        # Fetch JWKS and get the specific key
        jwks = await fetch_jwks()

        if kid not in jwks:
            # Key might have rotated, try fetching fresh JWKS
            _jwks_cache["keys"] = {}  # Clear cache to force refresh
            _jwks_cache["last_fetch"] = 0
            jwks = await fetch_jwks()

            if kid not in jwks:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: unknown key ID",
                )

        # Get the public key
        key_data = jwks[kid]

        # Verify token signature using RS256
        try:
            payload = jwt.decode(
                token,
                key_data,
                algorithms=["RS256"],
                audience="authenticated",
            )
            return payload
        except exceptions.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except exceptions.JWTClaimsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token claims: {str(e)}",
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        ) from e


__all__ = ["verify_supabase_token", "security", "fetch_jwks"]
