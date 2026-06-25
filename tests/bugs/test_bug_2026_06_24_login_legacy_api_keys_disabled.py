"""Regression: production login fails when only legacy Supabase JWT keys are configured."""

from __future__ import annotations

import pytest

from metar_shared.supabase_env import get_supabase_publishable_key

_LEGACY_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlc3QifQ."
    "signature"
)


def test_prod_does_not_use_legacy_jwt_anon_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When legacy keys are disabled in Supabase, JWT anon fallback must not be used in prod."""
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", _LEGACY_JWT)

    assert get_supabase_publishable_key() == ""


def test_local_still_allows_legacy_jwt_anon_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Local dev may still use legacy anon key until operators finish migration."""
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", "legacy-anon-dev")

    with pytest.warns(DeprecationWarning, match="SUPABASE_ANON_KEY"):
        assert get_supabase_publishable_key() == "legacy-anon-dev"


def test_supabase_proxy_rejects_legacy_jwt_in_prod(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Auth proxy should surface an actionable error instead of opaque Supabase 401."""
    from supabase_proxy import SupabaseAuthProxy

    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", _LEGACY_JWT)

    with pytest.raises(ValueError, match="Legacy Supabase"):
        SupabaseAuthProxy()
