"""Unit tests for retired operator auth helpers (F21 / ADR-031)."""

from __future__ import annotations

import pytest

from src.utilities import security as sec


@pytest.mark.unit
def test_disable_auth_constant_is_false() -> None:
    """DISABLE_AUTH dual path is retired — constant must stay False."""
    assert sec.DISABLE_AUTH is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_supabase_token_is_public_noop() -> None:
    result = await sec.verify_supabase_token(None)
    assert result["authenticated"] is False
    assert result["sub"] == "anonymous"
    assert result["user_id"] == "anonymous"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_jwks_removed() -> None:
    with pytest.raises(NotImplementedError, match="F21"):
        await sec.fetch_jwks()
