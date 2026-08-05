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


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


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


def doks_provisional() -> bool:
    """True when targeting provisional DOKS (Host-header / no real DNS)."""
    return _truthy("PLAYWRIGHT_DOKS_PROVISIONAL") or _truthy("DOKS_PROVISIONAL")


def doks_lb_ip() -> str:
    return _first_non_empty("DOKS_LB_IP") or "168.144.12.70"


def doks_api_host() -> str:
    return _first_non_empty("DOKS_API_HOST") or "api.doks.placeholder.metar-iwxxm.local"


def doks_fe_host() -> str:
    return _first_non_empty("DOKS_FE_HOST") or "app.doks.placeholder.metar-iwxxm.local"


def live_api_host_headers() -> dict[str, str]:
    """Host header for API requests when Ingress routes by hostname."""
    if doks_provisional():
        return {"Host": doks_api_host()}
    return {}


def live_frontend_host_headers() -> dict[str, str]:
    """Host header for FE asset fetches when Ingress routes by hostname."""
    if doks_provisional():
        return {"Host": doks_fe_host()}
    return {}


def live_frontend_fetch_base() -> str:
    """Base URL used to fetch FE assets (LB IP under provisional DOKS)."""
    if doks_provisional():
        return f"http://{doks_lb_ip()}"
    return live_frontend_url()


def expected_api_base_url() -> str:
    """Expected FE config.json api.baseUrl (placeholder host under provisional DOKS)."""
    return (_first_non_empty("VITE_API_BASE_URL") or live_api_url()).rstrip("/")


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
