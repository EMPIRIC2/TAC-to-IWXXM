"""T1.1 - JWKS-only JWT verify (F31 / ADR-033 / D-S038-04-b1)."""

from __future__ import annotations

import json
import time
from typing import Any

import jwt
import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import Response
from metar_auth.jwks import (
    JwtVerificationError,
    clear_jwks_client_cache,
    jwks_url_from_supabase_url,
    verify_access_token,
)


@pytest.fixture
def rsa_keypair() -> tuple[Any, dict[str, Any]]:
    """Generate an RSA keypair and matching JWKS JWK."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    def _b64url_uint(value: int) -> str:
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        import base64

        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    jwk = {
        "kty": "RSA",
        "kid": "test-kid-1",
        "use": "sig",
        "alg": "RS256",
        "n": _b64url_uint(public_numbers.n),
        "e": _b64url_uint(public_numbers.e),
    }
    return private_key, jwk


def _sign(
    private_key: Any,
    *,
    sub: str = "user-123",
    exp_offset: int = 3600,
    extra: dict[str, Any] | None = None,
) -> str:
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": sub,
        "email": "op@example.com",
        "iat": now,
        "exp": now + exp_offset,
    }
    if extra:
        payload.update(extra)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return jwt.encode(
        payload,
        pem,
        algorithm="RS256",
        headers={"kid": "test-kid-1"},
    )


@pytest.fixture(autouse=True)
def _clear_jwks_cache() -> None:
    clear_jwks_client_cache()


def test_jwks_url_from_supabase_url_strips_slash() -> None:
    assert (
        jwks_url_from_supabase_url("https://proj.supabase.co/")
        == "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    )


@respx.mock
def test_verify_access_token_happy_path(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key)
    claims = verify_access_token(token, jwks_url=jwks_url)
    assert claims["sub"] == "user-123"
    assert claims["email"] == "op@example.com"


@respx.mock
def test_verify_access_token_rejects_expired(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    private_key, jwk = rsa_keypair
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(private_key, exp_offset=-10)
    with pytest.raises(JwtVerificationError):
        verify_access_token(token, jwks_url=jwks_url)


@respx.mock
def test_verify_access_token_rejects_bad_signature(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    _private_key, jwk = rsa_keypair
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks_url = "https://proj.supabase.co/auth/v1/.well-known/jwks.json"
    respx.get(jwks_url).mock(return_value=Response(200, json={"keys": [jwk]}))
    token = _sign(other_key)
    with pytest.raises(JwtVerificationError):
        verify_access_token(token, jwks_url=jwks_url)


def test_verify_access_token_rejects_empty() -> None:
    with pytest.raises(JwtVerificationError, match="Missing"):
        verify_access_token("", jwks_url="https://example.test/jwks.json")


def test_verify_requires_jwks_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SUPABASE_JWKS_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    with pytest.raises(JwtVerificationError, match="JWKS URL"):
        verify_access_token("a.b.c")


def test_jwks_document_is_json_serializable_shape(
    rsa_keypair: tuple[Any, dict[str, Any]],
) -> None:
    _, jwk = rsa_keypair
    # Sanity: JWKS payload used by mocks is JSON-roundtrippable.
    assert json.loads(json.dumps({"keys": [jwk]}))["keys"][0]["kid"] == "test-kid-1"
