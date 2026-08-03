"""Unit tests for JWT gate helpers (F31 / ADR-033 JWKS-only)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from metar_auth.jwks import JwtVerificationError

from src.utilities import security as sec


@pytest.mark.unit
def test_disable_auth_constant_is_false() -> None:
    """DISABLE_AUTH must stay False — work-sessions always require JWT."""
    assert sec.DISABLE_AUTH is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_supabase_token_requires_auth_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_JWKS_URL", raising=False)
    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok"))
    assert exc.value.status_code == 503


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_supabase_token_rejects_bad_jwt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    with patch.object(
        sec,
        "verify_access_token",
        side_effect=JwtVerificationError("bad"),
    ):
        with pytest.raises(HTTPException) as exc:
            await sec.verify_supabase_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok"))
    assert exc.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_supabase_token_requires_sub(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_JWKS_URL", "https://example.supabase.co/jwks")
    with patch.object(sec, "verify_access_token", return_value={"aud": "x"}):
        with pytest.raises(HTTPException) as exc:
            await sec.verify_supabase_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok"))
    assert exc.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_supabase_token_happy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    with patch.object(sec, "verify_access_token", return_value={"sub": "u1"}):
        claims = await sec.verify_supabase_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok"))
    assert claims["sub"] == "u1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_jwks_removed() -> None:
    with pytest.raises(NotImplementedError, match="metar_auth"):
        await sec.fetch_jwks()
