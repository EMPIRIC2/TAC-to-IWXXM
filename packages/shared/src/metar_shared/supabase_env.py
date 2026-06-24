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


def _is_production_env() -> bool:
    return os.getenv("METAR_CONFIG_ENV", "local").strip().lower() == "prod"


def _is_legacy_jwt_api_key(value: str) -> bool:
    """True for legacy Supabase anon/service_role JWT keys (disabled when legacy keys off)."""
    return value.startswith("eyJ")


def _resolve_with_fallback(canonical: str, deprecated: str) -> str:
    value = os.getenv(canonical, "").strip()
    if value:
        return value
    legacy = os.getenv(deprecated, "").strip()
    if legacy:
        if (
            deprecated == _DEPRECATED_PUBLISHABLE
            and _is_production_env()
            and _is_legacy_jwt_api_key(legacy)
        ):
            logger.error(
                "%s is a legacy JWT key and is disabled in production; set %s",
                deprecated,
                _CANONICAL_PUBLISHABLE,
            )
            return ""
        warnings.warn(
            f"{deprecated} is deprecated; set {canonical} instead",
            DeprecationWarning,
            stacklevel=3,
        )
        logger.warning("%s is deprecated; migrate to %s", deprecated, canonical)
        return legacy
    return ""


def assert_modern_supabase_publishable_key(key: str) -> None:
    """Raise with an actionable message when publishable key is missing or legacy JWT."""
    if not key:
        raise ValueError(
            "SUPABASE_PUBLISHABLE_KEY is not set. "
            "Add your sb_publishable_* key to Render (see docs/env-contract.md)."
        )
    if _is_legacy_jwt_api_key(key):
        raise ValueError(
            "Legacy Supabase JWT anon key detected; Supabase has disabled legacy API keys. "
            "Set SUPABASE_PUBLISHABLE_KEY to your sb_publishable_* key in Render."
        )


def get_supabase_publishable_key() -> str:
    """Return publishable (anon) key from env with legacy fallback."""
    value = _resolve_with_fallback(_CANONICAL_PUBLISHABLE, _DEPRECATED_PUBLISHABLE)
    if value and _is_legacy_jwt_api_key(value) and _is_production_env():
        logger.error(
            "Refusing legacy JWT publishable key in production; set %s",
            _CANONICAL_PUBLISHABLE,
        )
        return ""
    return value


def get_supabase_secret_key() -> str:
    """Return secret key from env with legacy service-role fallback."""
    return _resolve_with_fallback(_CANONICAL_SECRET, _DEPRECATED_SECRET)


def get_supabase_url() -> str:
    """Return Supabase project URL from env or committed config."""
    url = os.getenv("SUPABASE_URL", "").strip()
    if url:
        return url
    return get_supabase_url_from_config()
