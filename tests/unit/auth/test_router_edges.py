"""Router edge paths: email validation, login mapping, /me fallbacks (EV-047)."""

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
from metar_auth.router import (
    create_auth_router,
    get_token_from_header,
    validate_email_permissive,
)
from starlette.exceptions import HTTPException as StarletteHTTPException


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
        "kid": "route-edge-kid",
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
            "sub": "user-edge",
            "email": "edge@example.com",
            "iat": now,
            "exp": now + 3600,
        },
        pem,
        algorithm="RS256",
        headers={"kid": "route-edge-kid"},
    )
    return private_key, jwk, token


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_jwks_client_cache()


def _client(proxy: SupabaseAuthProxy, jwks_url: str) -> TestClient:
    app = FastAPI()
    app.include_router(create_auth_router(proxy=proxy, jwks_url=jwks_url))
    return TestClient(app)


@pytest.mark.parametrize(
    "email",
    [
        "User@Foo.local",
        "a@bar.test",
        "x@host.localhost",
        "y@site.dev",
        "z@corp.example",
        "plain@local",
        "plain@test",
        "plain@localhost",
        "plain@dev",
        "plain@example",
    ],
)
def test_validate_email_permissive_dev_tlds(email: str) -> None:
    assert validate_email_permissive(email) == email.lower()


def test_validate_email_permissive_real_email() -> None:
    # email-validator lowercases the domain; local-part case is preserved.
    assert validate_email_permissive("Ops@Example.COM") == "Ops@example.com"


@pytest.mark.parametrize(
    "bad",
    ["", "no-at", "@nodomain", "nolocal@", "a@b@c"],
)
def test_validate_email_permissive_rejects_format(bad: str) -> None:
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email_permissive(bad)


def test_validate_email_permissive_rejects_invalid_via_validator() -> None:
    with pytest.raises(ValueError, match="Invalid email:"):
        validate_email_permissive("not an email@bad domain")


def test_logout_maps_auth_proxy_400() -> None:
    """POST /auth/logout maps AuthProxyError to HTTP 400. [Corpus: api] #1006."""
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_out.side_effect = AuthProxyError(
        "logout failed: denied", status_code=400
    )
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-access"},
        json={"scope": "local"},
    )
    assert response.status_code == 400
    assert "logout failed" in response.json()["detail"]
    proxy.sign_out.assert_called_once_with("test-access", scope="local")


def test_logout_maps_auth_proxy_502() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_out.side_effect = AuthProxyError(
        "logout failed: upstream", status_code=502
    )
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-access"},
    )
    assert response.status_code == 502
    proxy.sign_out.assert_called_once_with("test-access", scope=None)


def test_logout_rejects_unsupported_scope() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-access"},
        json={"scope": "everywhere"},
    )
    assert response.status_code == 422
    proxy.sign_out.assert_not_called()


def test_logout_empty_scope_passes_none() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_out.return_value = {"message": "Successfully signed out"}
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test-access"},
        json={"scope": ""},
    )
    assert response.status_code == 200
    proxy.sign_out.assert_called_once_with("test-access", scope=None)


def test_logout_invalid_bearer_format() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Token abc"},
        json={"scope": "local"},
    )
    assert response.status_code == 401
    proxy.sign_out.assert_not_called()


def test_login_maps_auth_proxy_503() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.sign_in.side_effect = AuthProxyError("missing env", status_code=503)
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/login",
        json={"email": "a@example.com", "password": "x"},
    )
    assert response.status_code == 503
    assert "missing env" in response.json()["detail"]


def test_login_rejects_invalid_email_body() -> None:
    proxy = MagicMock(spec=SupabaseAuthProxy)
    client = _client(
        proxy,
        "https://proj.supabase.co/auth/v1/.well-known/jwks.json",
    )
    response = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "x"},
    )
    assert response.status_code == 422
    proxy.sign_in.assert_not_called()


@respx.mock
def test_me_jwks_failure_returns_401(
    rsa_material: tuple[Any, dict[str, Any], str],
) -> None:
    _pk, _jwk, token = rsa_material
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(500, text="fail"))
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.supabase_url = "https://proj.supabase.co"
    client = _client(proxy, jwks_url)
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    proxy.get_user.assert_not_called()


@respx.mock
def test_me_get_user_success(
    rsa_material: tuple[Any, dict[str, Any], str],
) -> None:
    _pk, jwk, token = rsa_material
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.supabase_url = "https://proj.supabase.co"
    proxy.get_user.return_value = {
        "id": "from-api",
        "email": "api@example.com",
        "metadata": {"m": True},
    }
    client = _client(proxy, jwks_url)
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "from-api",
        "email": "api@example.com",
        "metadata": {"m": True},
    }


@respx.mock
def test_me_fills_id_from_claims_when_empty(
    rsa_material: tuple[Any, dict[str, Any], str],
) -> None:
    _pk, jwk, token = rsa_material
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.supabase_url = "https://proj.supabase.co"
    proxy.get_user.return_value = {
        "id": "",
        "email": "api@example.com",
        "metadata": {},
    }
    client = _client(proxy, jwks_url)
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "user-edge"
    assert body["email"] == "api@example.com"


@respx.mock
def test_me_get_user_fail_falls_back_to_claims(
    rsa_material: tuple[Any, dict[str, Any], str],
) -> None:
    _pk, jwk, token = rsa_material
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    proxy = MagicMock(spec=SupabaseAuthProxy)
    proxy.supabase_url = "https://proj.supabase.co"
    proxy.get_user.side_effect = AuthProxyError("lookup", status_code=401)
    client = _client(proxy, jwks_url)
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "user-edge",
        "email": "edge@example.com",
        "metadata": {},
    }


def test_get_token_from_header_invalid_format() -> None:
    with pytest.raises(StarletteHTTPException) as exc_info:
        get_token_from_header("Token abc")
    assert exc_info.value.status_code == 401
    assert "Invalid authorization" in str(exc_info.value.detail)


def test_get_token_from_header_missing() -> None:
    with pytest.raises(StarletteHTTPException) as exc_info:
        get_token_from_header(None)
    assert exc_info.value.status_code == 401


def test_create_auth_router_default_proxy() -> None:
    router = create_auth_router(supabase_url="https://proj.supabase.co")
    paths = {getattr(r, "path", None) for r in router.routes}
    assert "/auth/login" in paths
    assert "/auth/logout" in paths
    assert "/auth/me" in paths
