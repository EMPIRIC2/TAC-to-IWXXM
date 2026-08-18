"""TC-EV060-1006 / D-S070-logout=1a — restore POST /auth/logout.

Spec: [Corpus: api] POST /auth/logout; [Corpus: product §F31]; #1006.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy
from metar_auth.router import create_auth_router


class _StubProxy(SupabaseAuthProxy):
    """In-memory Auth proxy for logout unit tests."""

    def __init__(self) -> None:
        super().__init__(
            supabase_url="https://example.supabase.co",
            publishable_key="test-anon",
        )
        self.calls: list[tuple[str, str | None]] = []

    def sign_out(self, access_token: str, *, scope: str | None = None) -> dict[str, str]:
        self.calls.append((access_token, scope))
        if access_token == "bad-token":
            raise AuthProxyError("logout failed", status_code=400)
        return {"message": "Successfully signed out"}


@pytest.mark.unit
def test_auth_logout_requires_bearer() -> None:
    """POST /auth/logout without Authorization → 401."""
    app = FastAPI()
    app.include_router(create_auth_router(proxy=_StubProxy()))
    client = TestClient(app)

    response = client.post("/auth/logout", json={"scope": "local"})
    assert response.status_code == 401


@pytest.mark.unit
def test_auth_logout_passes_scope_to_proxy() -> None:
    """POST /auth/logout with Bearer + scope → 200 and proxy.sign_out."""
    proxy = _StubProxy()
    app = FastAPI()
    app.include_router(create_auth_router(proxy=proxy))
    client = TestClient(app)

    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-access"},
        json={"scope": "local"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully signed out"}
    assert proxy.calls == [("test-access", "local")]


@pytest.mark.unit
def test_auth_logout_accepts_empty_body() -> None:
    """authService.logout() POSTs Bearer with no JSON body."""
    proxy = _StubProxy()
    app = FastAPI()
    app.include_router(create_auth_router(proxy=proxy))
    client = TestClient(app)

    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-access"},
    )
    assert response.status_code == 200
    assert proxy.calls == [("test-access", None)]


@pytest.mark.unit
def test_proxy_sign_out_posts_gotrue_logout(monkeypatch: pytest.MonkeyPatch) -> None:
    """SupabaseAuthProxy.sign_out hits /auth/v1/logout?scope=… with user Bearer."""
    captured: dict[str, Any] = {}

    class _Resp:
        status_code = 204
        text = ""

    class _Http:
        def post(self, url: str, *, headers: dict[str, str], params: Any = None):
            captured["url"] = url
            captured["headers"] = headers
            captured["params"] = params
            return _Resp()

    proxy = SupabaseAuthProxy(
        supabase_url="https://example.supabase.co",
        publishable_key="anon-key",
        client=_Http(),  # type: ignore[arg-type]
    )
    out = proxy.sign_out("user-jwt", scope="local")
    assert out == {"message": "Successfully signed out"}
    assert captured["url"] == "https://example.supabase.co/auth/v1/logout"
    assert captured["params"] == {"scope": "local"}
    assert captured["headers"]["Authorization"] == "Bearer user-jwt"
    assert captured["headers"]["apikey"] == "anon-key"
