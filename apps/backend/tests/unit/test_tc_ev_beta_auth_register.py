"""TC-EV-beta-007 — POST /auth/register via GoTrue proxy."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy
from metar_auth.router import create_auth_router


class _StubProxy(SupabaseAuthProxy):
    def __init__(self) -> None:
        super().__init__(
            supabase_url="https://example.supabase.co",
            publishable_key="test-anon",
        )
        self.signups: list[tuple[str, str]] = []

    def sign_up(self, email: str, password: str) -> dict[str, Any]:
        self.signups.append((email, password))
        if email.startswith("dup@"):
            raise AuthProxyError("registration failed: already registered", status_code=400)
        return {
            "user": {"id": "new-user", "email": email, "metadata": {}},
            "session": {
                "access_token": "at",
                "refresh_token": "rt",
                "expires_at": 1,
            },
        }


@pytest.mark.unit
def test_auth_register_success() -> None:
    proxy = _StubProxy()
    app = FastAPI()
    app.include_router(create_auth_router(proxy=proxy))
    client = TestClient(app)
    res = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "secret12"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["user"]["email"] == "new@example.com"
    assert body["session"]["access_token"] == "at"
    assert proxy.signups == [("new@example.com", "secret12")]


@pytest.mark.unit
def test_auth_register_maps_proxy_error() -> None:
    app = FastAPI()
    app.include_router(create_auth_router(proxy=_StubProxy()))
    client = TestClient(app)
    res = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "secret12"},
    )
    assert res.status_code == 400
