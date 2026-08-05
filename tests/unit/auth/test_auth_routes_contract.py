"""T1.1 — `/auth/login` + `/auth/me` contract; no admin (F31 / ADR-033)."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import jwt
import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from metar_auth.jwks import clear_jwks_client_cache
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy
from metar_auth.router import create_auth_router


@pytest.fixture
def rsa_material() -> tuple[Any, dict[str, Any], str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    def _b64url_uint(value: int) -> str:
        import base64

        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    jwk = {
        "kty": "RSA",
        "kid": "route-kid",
        "use": "sig",
        "alg": "RS256",
        "n": _b64url_uint(public_numbers.n),
        "e": _b64url_uint(public_numbers.e),
    }
    now = int(time.time())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    token = jwt.encode(
        {
            "sub": "user-abc",
            "email": "op@example.com",
            "iat": now,
            "exp": now + 3600,
        },
        pem,
        algorithm="RS256",
        headers={"kid": "route-kid"},
    )
    return private_key, jwk, token


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_jwks_client_cache()


def _app_with_auth(
    *,
    proxy: SupabaseAuthProxy,
    jwks_url: str,
) -> TestClient:
    app = FastAPI()
    app.include_router(
        create_auth_router(proxy=proxy, jwks_url=jwks_url),
    )
    return TestClient(app)


def test_login_returns_user_and_session() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_in.return_value = {
        "user": {"id": "u1", "email": "a@example.com", "metadata": {}},
        "session": {
            "access_token": "tok",
            "refresh_token": "ref",
            "expires_at": 1,
        },
    }
    client = _app_with_auth(
        proxy=proxy,
        jwks_url="https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/login",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["id"] == "u1"
    assert body["session"]["access_token"] == "tok"
    proxy.sign_in.assert_called_once_with("a@example.com", "password123")


def test_login_maps_proxy_failure_to_401() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_in.side_effect = AuthProxyError("bad creds", status_code=401)
    client = _app_with_auth(
        proxy=proxy,
        jwks_url="https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/login",
        json={"email": "a@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@respx.mock
def test_me_requires_valid_jwks_token(
    rsa_material: tuple[Any, dict[str, Any], str],
) -> None:
    _, jwk, token = rsa_material
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.supabase_url = "https://proj.supabase.co"
    proxy.get_user.side_effect = AuthProxyError("skip", status_code=401)
    client = _app_with_auth(proxy=proxy, jwks_url=jwks_url)
    ok = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
    assert ok.json()["id"] == "user-abc"
    bad = client.get("/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert bad.status_code == 401
    missing = client.get("/auth/me")
    assert missing.status_code == 401


def test_admin_routes_not_mounted() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    client = _app_with_auth(
        proxy=proxy,
        jwks_url="https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    for path in ("/admin", "/auth/admin", "/admin/users"):
        response = client.get(path)
        assert response.status_code == 404, path
