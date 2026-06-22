"""Resolve canonical LIVE_* env vars with deprecated STAGING_* / E2E_* fallbacks."""

from __future__ import annotations

import os
import warnings


def _first_non_empty(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def live_api_url() -> str:
    """Return live API base URL without trailing slash."""
    return _first_non_empty(
        "LIVE_API_URL", "STAGING_API_URL", "E2E_API_URL", "E2E_BACKEND_URL"
    ).rstrip("/")


def live_frontend_url() -> str:
    """Return live frontend origin/URL without trailing slash."""
    return _first_non_empty(
        "LIVE_FRONTEND_URL",
        "STAGING_FRONTEND_ORIGIN",
        "STAGING_FRONTEND_URL",
        "E2E_FRONTEND_URL",
    ).rstrip("/")


def warn_deprecated_env() -> None:
    """Emit deprecation warnings when legacy env vars are used without LIVE_*."""
    if not os.environ.get("LIVE_API_URL", "").strip() and _first_non_empty(
        "STAGING_API_URL", "E2E_API_URL", "E2E_BACKEND_URL"
    ):
        warnings.warn(
            "STAGING_API_URL / E2E_* are deprecated; set LIVE_API_URL",
            DeprecationWarning,
            stacklevel=2,
        )
    if not os.environ.get("LIVE_FRONTEND_URL", "").strip() and _first_non_empty(
        "STAGING_FRONTEND_ORIGIN", "STAGING_FRONTEND_URL", "E2E_FRONTEND_URL"
    ):
        warnings.warn(
            "STAGING_FRONTEND_* / E2E_FRONTEND_URL are deprecated; set LIVE_FRONTEND_URL",
            DeprecationWarning,
            stacklevel=2,
        )
