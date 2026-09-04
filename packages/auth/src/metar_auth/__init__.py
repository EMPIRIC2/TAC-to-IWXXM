"""Supabase Auth-only library - JWKS JWT verify + `/auth/*` routers (ADR-033)."""

from __future__ import annotations

from metar_auth.jwks import (
    JwtVerificationError,
    jwks_url_from_supabase_url,
    verify_access_token,
)
from metar_auth.router import create_auth_router

__all__ = [
    "JwtVerificationError",
    "create_auth_router",
    "jwks_url_from_supabase_url",
    "verify_access_token",
]
