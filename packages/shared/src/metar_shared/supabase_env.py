"""Canonical Supabase environment variable resolution with deprecation shims."""

from __future__ import annotations

import logging
import os
import warnings

from metar_shared.config_loader import get_supabase_url_from_config

logger = logging.getLogger(__name__)

_CANONICAL_PUBLISHABLE = "SUPABASE_PUBLISHABLE_KEY"
_DEPRECATED_PUBLISHABLE = "SUPABASE_ANON_KEY"
_CANONICAL_SECRET = "SUPABASE_SECRET_KEY"
_DEPRECATED_SECRET = "SUPABASE_SERVICE_ROLE_KEY"


def _resolve_with_fallback(canonical: str, deprecated: str) -> str:
    value = os.getenv(canonical, "").strip()
    if value:
        return value
    legacy = os.getenv(deprecated, "").strip()
    if legacy:
        warnings.warn(
            f"{deprecated} is deprecated; set {canonical} instead",
            DeprecationWarning,
            stacklevel=3,
        )
        logger.warning("%s is deprecated; migrate to %s", deprecated, canonical)
        return legacy
    return ""


def get_supabase_publishable_key() -> str:
    """Return publishable (anon) key from env with legacy fallback."""
    return _resolve_with_fallback(_CANONICAL_PUBLISHABLE, _DEPRECATED_PUBLISHABLE)


def get_supabase_secret_key() -> str:
    """Return secret key from env with legacy service-role fallback."""
    return _resolve_with_fallback(_CANONICAL_SECRET, _DEPRECATED_SECRET)


def get_supabase_url() -> str:
    """Return Supabase project URL from env or committed config."""
    url = os.getenv("SUPABASE_URL", "").strip()
    if url:
        return url
    return get_supabase_url_from_config()
