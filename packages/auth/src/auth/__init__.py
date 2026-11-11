"""Supabase Auth service library — JWKS verify + Auth API proxy (no HTTP routes)."""

from __future__ import annotations

from auth.jwks import (
    JwtVerificationError,
    jwks_url_from_supabase_url,
    verify_access_token,
)
from auth.models import AuthProxyError
from auth.proxy import SupabaseAuthProxy

__all__ = [
    "AuthProxyError",
    "JwtVerificationError",
    "SupabaseAuthProxy",
    "jwks_url_from_supabase_url",
    "verify_access_token",
]
