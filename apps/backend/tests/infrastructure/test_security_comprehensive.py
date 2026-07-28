"""Comprehensive tests for retired operator security helpers (F21)."""

from __future__ import annotations

import pytest

from src.utilities.security import DISABLE_AUTH, fetch_jwks, verify_supabase_token


@pytest.mark.unit
class TestSecurityRetired:
    def test_disable_auth_retired(self) -> None:
        assert DISABLE_AUTH is False

    @pytest.mark.asyncio
    async def test_verify_is_anonymous_noop(self) -> None:
        result = await verify_supabase_token(None)
        assert result["authenticated"] is False
        assert result["sub"] == "anonymous"

    @pytest.mark.asyncio
    async def test_fetch_jwks_removed(self) -> None:
        with pytest.raises(NotImplementedError):
            await fetch_jwks()
