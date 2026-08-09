"""JWKS edge paths: cache, fetch failures, aud/iss, kid (EV-047)."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import patch

import jwt
import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import Response
from metar_auth.jwks import (
    JwtVerificationError,
    clear_jwks_client_cache,
    resolve_jwks_url,
    verify_access_token,
)


@pytest.fixture
def rsa_keypair() -> tuple[Any, dict[str, Any]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    def _b64url_uint(value: int) -> str:
        import base64

        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    jwk = {
        "kty": "RSA",
        "kid": "edge-kid",
        "use": "sig",
        "alg": "RS256",
        "n": _b64url_uint(public_numbers.n),
        "e": _b64url_uint(public_numbers.e),
    }
    return private_key, jwk


def _sign(
    private_key: Any,
    *,
    kid: str | None = "edge-kid",
    extra: dict[str, Any] | None = None,
    include_kid: bool = True,
) -> str:
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": "user-edge",
        "email": "edge@example.com",
        "iat": now,
        "exp": now + 3600,
    }
    if extra:
        payload.update(extra)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    headers: dict[str, Any] = {}
    if include_kid and kid is not None:
        headers["kid"] = kid
    return jwt.encode(payload, pem, algorithm="RS256", headers=headers or None)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    clear_jwks_client_cache()


def test_resolve_jwks_url_explicit_arg() -> None:
    assert (
        resolve_jwks_url(jwks_url=" https://jwks.example/keys ")
        == "https://jwks.example/keys"
    )


def test_resolve_jwks_url_from_env_jwks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_JWKS_URL", "https://env.example/jwks.json")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert resolve_jwks_url() == "https://env.example/jwks.json"


def test_resolve_jwks_url_from_supabase_url_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SUPABASE_JWKS_URL", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co/")
    assert (
        resolve_jwks_url() == "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    )


def test_resolve_jwks_url_from_supabase_url_arg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SUPABASE_JWKS_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert (
        resolve_jwks_url(supabase_url="https://arg.supabase.co")
        == "https://arg.supabase.co/auth/v1/.well-known/jwks.json"
    )


@respx.mock
def test_jwks_cache_hit_skips_second_fetch(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    route = respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key)
    assert verify_access_token(token, jwks_url=jwks_url)["sub"] == "user-edge"
    assert verify_access_token(token, jwks_url=jwks_url)["sub"] == "user-edge"
    assert route.call_count == 1


@respx.mock
def test_jwks_fetch_http_error_raises(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, _jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(503, text="down"))
    with pytest.raises(JwtVerificationError, match="JWKS fetch failed"):
        verify_access_token(_sign(private_key), jwks_url=jwks_url)


@respx.mock
def test_jwks_fetch_network_error_raises(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, _jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(side_effect=OSError("dns boom"))
    with pytest.raises(JwtVerificationError, match="JWKS fetch failed"):
        verify_access_token(_sign(private_key), jwks_url=jwks_url)


@respx.mock
def test_jwks_document_missing_keys(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, _jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"foo": []}))
    with pytest.raises(JwtVerificationError, match="missing keys"):
        verify_access_token(_sign(private_key), jwks_url=jwks_url)


@respx.mock
def test_jwks_document_non_dict(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, _jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json=[1, 2, 3]))
    with pytest.raises(JwtVerificationError, match="missing keys"):
        verify_access_token(_sign(private_key), jwks_url=jwks_url)


@respx.mock
def test_verify_rejects_missing_kid(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key, include_kid=False)
    with pytest.raises(JwtVerificationError, match="missing kid"):
        verify_access_token(token, jwks_url=jwks_url)


@respx.mock
def test_verify_rejects_unknown_kid(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key, kid="other-kid")
    with pytest.raises(JwtVerificationError):
        verify_access_token(token, jwks_url=jwks_url)


@respx.mock
def test_verify_enforces_audience(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key, extra={"aud": "authenticated"})
    claims = verify_access_token(
        token,
        jwks_url=jwks_url,
        audience="authenticated",
    )
    assert claims["aud"] == "authenticated"
    with pytest.raises(JwtVerificationError):
        verify_access_token(token, jwks_url=jwks_url, audience="wrong-aud")


@respx.mock
def test_verify_enforces_issuer(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    iss = "https://proj.supabase.co/auth/v1"
    token = _sign(private_key, extra={"iss": iss})
    claims = verify_access_token(token, jwks_url=jwks_url, issuer=iss)
    assert claims["iss"] == iss
    with pytest.raises(JwtVerificationError):
        verify_access_token(
            token,
            jwks_url=jwks_url,
            issuer="https://other.example/auth/v1",
        )


def test_verify_rejects_whitespace_token() -> None:
    with pytest.raises(JwtVerificationError, match="Missing"):
        verify_access_token("   ", jwks_url="https://example.test/jwks.json")


@respx.mock
def test_verify_generic_exception_wrapped(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key)
    with (
        patch(
            "metar_auth.jwks.PyJWKSet.from_dict",
            side_effect=RuntimeError("boom"),
        ),
        pytest.raises(JwtVerificationError, match="boom"),
    ):
        verify_access_token(token, jwks_url=jwks_url)
