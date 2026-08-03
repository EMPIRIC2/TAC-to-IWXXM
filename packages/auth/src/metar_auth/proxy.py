"""Thin Supabase Auth HTTP proxy for login/logout/refresh (no product DB)."""

from __future__ import annotations

import os
from typing import Any

import httpx


class AuthProxyError(Exception):
    """Supabase Auth HTTP call failed."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class SupabaseAuthProxy:
    """Password-grant Auth API client (publishable key only)."""

    def __init__(
        self,
        *,
        supabase_url: str | None = None,
        publishable_key: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.supabase_url = (supabase_url or os.getenv("SUPABASE_URL") or "").rstrip(
            "/"
        )
        self.publishable_key = (
            publishable_key
            or os.getenv("SUPABASE_PUBLISHABLE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        )
        self._client = client
        self._owns_client = client is None

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=30.0)
        return self._client

    def close(self) -> None:
        """Close the owned HTTP client."""
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def _headers(self) -> dict[str, str]:
        if not self.supabase_url or not self.publishable_key:
            raise AuthProxyError(
                "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY required for Auth",
                status_code=503,
            )
        return {
            "apikey": self.publishable_key,
            "Authorization": f"Bearer {self.publishable_key}",
            "Content-Type": "application/json",
        }

    def sign_in(self, email: str, password: str) -> dict[str, Any]:
        """
        Authenticate via Supabase password grant.

        Parameters
        ----------
        email : str
            User email.
        password : str
            User password.

        Returns
        -------
        dict[str, Any]
            Normalized ``user`` + ``session`` payload.
        """
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        response = self._http().post(
            url,
            headers=self._headers(),
            json={"email": email, "password": password},
        )
        if response.status_code >= 400:
            detail = response.text
            raise AuthProxyError(
                f"login failed: {detail}",
                status_code=401 if response.status_code in {400, 401} else 502,
            )
        data = response.json()
        return _normalize_session_payload(data)

    def get_user(self, access_token: str) -> dict[str, Any]:
        """
        Fetch the Auth user for ``access_token``.

        Parameters
        ----------
        access_token : str
            Bearer access token (already JWKS-verified by the router).

        Returns
        -------
        dict[str, Any]
            User dict with ``id`` / ``email`` / ``metadata``.
        """
        url = f"{self.supabase_url}/auth/v1/user"
        headers = self._headers()
        headers["Authorization"] = f"Bearer {access_token}"
        response = self._http().get(url, headers=headers)
        if response.status_code >= 400:
            raise AuthProxyError("user lookup failed", status_code=401)
        data = response.json()
        return {
            "id": data.get("id") or "",
            "email": data.get("email") or "",
            "metadata": data.get("user_metadata") or {},
        }


def _normalize_session_payload(data: dict[str, Any]) -> dict[str, Any]:
    user_raw = data.get("user") or {}
    return {
        "user": {
            "id": user_raw.get("id") or "",
            "email": user_raw.get("email") or "",
            "metadata": user_raw.get("user_metadata") or {},
        },
        "session": {
            "access_token": data.get("access_token") or "",
            "refresh_token": data.get("refresh_token") or "",
            "expires_at": int(data.get("expires_at") or 0),
        },
    }
