"""Configuration helpers for Locust load tests."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class LoadProfile:
    """Defines scenario settings for a load-test profile."""

    name: str
    host: str
    auth_mode: str
    auth_base_url: str
    target_iwxxm_version: str
    validation_layers: str
    evaluation_enabled: bool


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _build_profile(name: str) -> LoadProfile:
    defaults = {
        "local_bypass": {
            "host": "http://localhost:8001",
            "auth_mode": "bypass",
            "auth_base_url": "http://localhost:8002",
        },
        "local_auth": {
            "host": "http://localhost:8001",
            "auth_mode": "bearer",
            "auth_base_url": "http://localhost:8002",
        },
        "staging_bypass": {
            "host": "https://metar-to-iwxxm.onrender.com",
            "auth_mode": "bypass",
            "auth_base_url": "https://metar-to-iwxxm-auth.onrender.com",
        },
        "staging_auth": {
            "host": "https://metar-to-iwxxm.onrender.com",
            "auth_mode": "bearer",
            "auth_base_url": "https://metar-to-iwxxm-auth.onrender.com",
        },
    }

    if name not in defaults:
        supported = ", ".join(sorted(defaults.keys()))
        raise ValueError(f"Unsupported LOCUST_PROFILE '{name}'. Supported: {supported}")

    selected = defaults[name]
    host = os.getenv("LOCUST_HOST", selected["host"])
    auth_mode = os.getenv("LOCUST_AUTH_MODE", selected["auth_mode"]).lower().strip()
    auth_base_url = os.getenv("LOCUST_AUTH_BASE_URL", selected["auth_base_url"])

    return LoadProfile(
        name=name,
        host=host,
        auth_mode=auth_mode,
        auth_base_url=auth_base_url,
        target_iwxxm_version=os.getenv("LOCUST_IWXXM_VERSION", "2025-2"),
        validation_layers=os.getenv("LOCUST_VALIDATION_LAYERS", "airport_icao,tac_syntax"),
        evaluation_enabled=_env_bool("LOCUST_ENABLE_EVALUATION", default=False),
    )


def load_profile() -> LoadProfile:
    """Load active profile from environment variables."""
    profile_name = os.getenv("LOCUST_PROFILE", "local_bypass").strip().lower()
    return _build_profile(profile_name)
