"""Operator JWT gate retired (F21 / ADR-031 / T5.2).

Public convert / validate / lint / decode / dissemination no longer depend on this
module. ``verify_supabase_token`` remains as a transitional no-op for any leftover
call sites that still declare the dependency.

The ``DISABLE_AUTH`` dual path is removed — there is no JWT enforcement path left
for the operator API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# Retired — kept as a constant so leftover tests/config greps fail closed.
DISABLE_AUTH = False


async def verify_supabase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Transitional no-op auth dependency (F21).

    Ignores credentials and returns an anonymous principal. Callers that still
    inject this dependency must not treat the result as a verified end-user.

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials or None
        Optional Bearer credentials (ignored).

    Returns
    -------
    dict[str, Any]
        Anonymous principal marker.
    """
    _ = credentials
    return {
        "sub": "anonymous",
        "user_id": "anonymous",
        "email": None,
        "authenticated": False,
        "environment": "public",
    }


async def fetch_jwks() -> Dict[str, Any]:
    """Removed with operator Auth (F21) — JWKS is no longer used by the API."""
    raise NotImplementedError("JWKS fetching removed with operator Auth (F21 / ADR-031)")


__all__ = ["verify_supabase_token", "fetch_jwks", "DISABLE_AUTH"]
