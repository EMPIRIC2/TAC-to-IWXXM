"""BUG-2026-09-17 — email confirm must verify token_hash via /auth/confirm.

Repro: registration leaves users unconfirmed because the app never calls GoTrue
verify with the email template ``token_hash``. Login then fails with
``email_not_confirmed``.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy
from metar_auth.router import create_auth_router


def _route_paths(router: object) -> set[str]:
    paths: set[str] = set()
    for route in getattr(router, "routes", []):
        if isinstance(route, APIRoute):
            paths.add(route.path)
    return paths


@pytest.mark.unit
def test_bug_2026_09_17_auth_confirm_route_mounted() -> None:
    """Operator Auth must expose POST /auth/confirm for email token_hash verify."""
    router = create_auth_router(proxy=MagicMock())
    assert "/auth/confirm" in _route_paths(router)


@pytest.mark.unit
def test_bug_2026_09_17_auth_confirm_exchanges_token_hash() -> None:
    """POST /auth/confirm must call GoTrue verify and return a session."""
    proxy = MagicMock()
    proxy.verify_email.return_value = {
        "user": {"id": "u1", "email": "op@example.com", "metadata": {}},
        "session": {
            "access_token": "at",
            "refresh_token": "rt",
            "expires_at": 99,
        },
    }
    app = FastAPI()
    app.include_router(create_auth_router(proxy=proxy))
    client = TestClient(app)
    response = client.post(
        "/auth/confirm",
        json={"token_hash": "abc123hash", "type": "email"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["session"]["access_token"] == "at"
    assert body["user"]["email"] == "op@example.com"
    proxy.verify_email.assert_called_once_with("abc123hash", "email")


@pytest.mark.unit
def test_bug_2026_09_17_sign_in_maps_email_not_confirmed() -> None:
    """Password grant email_not_confirmed → operator-facing confirm message."""
    client = MagicMock(spec=httpx.Client)
    client.post.return_value = MagicMock(
        status_code=400,
        text='{"code":400,"error_code":"email_not_confirmed","msg":"Email not confirmed"}',
    )
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    with pytest.raises(AuthProxyError) as exc_info:
        proxy.sign_in("op@example.com", "password123")
    assert exc_info.value.status_code == 401
    assert "confirm your email" in str(exc_info.value).lower()
    assert "email_not_confirmed" not in str(exc_info.value)
