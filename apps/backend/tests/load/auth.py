"""Authentication helpers for Locust users."""

from __future__ import annotations

import os
import threading
from abc import ABC, abstractmethod

import requests
from tests.load.config import LoadProfile


class AuthProvider(ABC):
    """Provides headers for protected API calls."""

    @abstractmethod
    def headers(self) -> dict[str, str]:
        """Return request headers for authenticated requests."""


class BypassAuthProvider(AuthProvider):
    """No-op auth provider for DISABLE_AUTH mode."""

    def headers(self) -> dict[str, str]:
        return {}


class BearerAuthProvider(AuthProvider):
    """Bearer token via Supabase GoTrue password grant (F31 FE-direct)."""

    def __init__(self, profile: LoadProfile):
        self._profile = profile
        self._access_token = ""
        self._lock = threading.Lock()

    def headers(self) -> dict[str, str]:
        token = self._get_token()
        return {"Authorization": f"Bearer {token}"}

    def _get_token(self) -> str:
        with self._lock:
            if self._access_token:
                return self._access_token
            self._access_token = self._login()
            return self._access_token

    def _login(self) -> str:
        email = _required_env("LOCUST_AUTH_EMAIL")
        password = _required_env("LOCUST_AUTH_PASSWORD")
        timeout = float(_required_env("LOCUST_AUTH_TIMEOUT", default="20"))
        supabase_url = (
            os.getenv("SUPABASE_URL") or os.getenv("LOCUST_SUPABASE_URL") or self._profile.auth_base_url
        ).rstrip("/")
        publishable = (
            os.getenv("SUPABASE_PUBLISHABLE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or os.getenv("LOCUST_SUPABASE_ANON_KEY")
            or ""
        ).strip()
        if not supabase_url or not publishable:
            raise RuntimeError(
                "Bearer load auth requires SUPABASE_URL + SUPABASE_PUBLISHABLE_KEY "
                "(or LOCUST_SUPABASE_* / LOCUST_AUTH_BASE_URL)"
            )

        response = requests.post(
            f"{supabase_url}/auth/v1/token?grant_type=password",
            json={"email": email, "password": password},
            headers={
                "Content-Type": "application/json",
                "apikey": publishable,
                "Authorization": f"Bearer {publishable}",
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()

        token = payload.get("access_token", "")
        if not token:
            raise RuntimeError("Auth login succeeded but no access token returned")
        return token


def build_auth_provider(profile: LoadProfile) -> AuthProvider:
    """Build provider based on selected auth mode."""
    if profile.auth_mode == "bypass":
        return BypassAuthProvider()
    if profile.auth_mode == "bearer":
        return BearerAuthProvider(profile=profile)
    raise ValueError("LOCUST_AUTH_MODE must be either 'bypass' or 'bearer'")


def _required_env(name: str, default: str | None = None) -> str:
    value = default if default is not None else ""
    value = str(value) if default is not None else value
    raw = _safe_env(name, value)
    if not raw:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return raw


def _safe_env(name: str, default: str) -> str:
    return os.getenv(name, default).strip()
