"""Supabase Auth service library — JWKS verify + Auth API proxy (no HTTP routes)."""

from __future__ import annotations

from metar_auth.jwks import (
    JwtVerificationError,
    jwks_url_from_supabase_url,
    verify_access_token,
)
from metar_auth.models import AuthProxyError
from metar_auth.proxy import SupabaseAuthProxy

__all__ = [
    "AuthProxyError",
    "JwtVerificationError",
    "SupabaseAuthProxy",
    "jwks_url_from_supabase_url",
    "verify_access_token",
]
