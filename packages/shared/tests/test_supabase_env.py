"""Tests for metar_shared.supabase_env."""

from __future__ import annotations

import warnings

import pytest

from metar_shared.supabase_env import (
    _is_legacy_jwt_api_key,
    _is_production_env,
    assert_modern_supabase_publishable_key,
    get_supabase_publishable_key,
    get_supabase_secret_key,
    get_supabase_url,
)

_LEGACY_JWT = "eyJhbGciOiJIUzI1NiJ9.eyJyZWYiOiJ0ZXN0In0.sig"


def test_publishable_key_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    assert get_supabase_publishable_key() == "sb_publishable_test"


def test_publishable_key_legacy_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", "legacy-anon")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert get_supabase_publishable_key() == "legacy-anon"
    assert any("SUPABASE_ANON_KEY" in str(w.message) for w in caught)


def test_secret_key_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_test")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    assert get_supabase_secret_key() == "sb_secret_test"


def test_secret_key_legacy_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "legacy-service")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert get_supabase_secret_key() == "legacy-service"
    assert any("SUPABASE_SERVICE_ROLE_KEY" in str(w.message) for w in caught)


def test_supabase_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://env.supabase.co")
    assert get_supabase_url() == "https://env.supabase.co"


def test_publishable_key_empty_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    assert get_supabase_publishable_key() == ""


def test_secret_key_empty_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    assert get_supabase_secret_key() == ""

    monkeypatch.delenv("SUPABASE_URL", raising=False)
    url = get_supabase_url()
    assert url.startswith("https://")
    assert "supabase.co" in url


def test_is_production_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    assert _is_production_env() is True
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    assert _is_production_env() is False
    monkeypatch.delenv("METAR_CONFIG_ENV", raising=False)
    assert _is_production_env() is False


def test_is_legacy_jwt_api_key() -> None:
    assert _is_legacy_jwt_api_key(_LEGACY_JWT) is True
    assert _is_legacy_jwt_api_key("sb_publishable_abc") is False
    assert _is_legacy_jwt_api_key("") is False


def test_publishable_legacy_jwt_refused_in_prod(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", _LEGACY_JWT)
    assert get_supabase_publishable_key() == ""


def test_publishable_legacy_jwt_canonical_refused_in_prod(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", _LEGACY_JWT)
    assert get_supabase_publishable_key() == ""


def test_publishable_legacy_jwt_allowed_in_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_ANON_KEY", _LEGACY_JWT)
    with pytest.warns(DeprecationWarning, match="SUPABASE_ANON_KEY"):
        assert get_supabase_publishable_key() == _LEGACY_JWT


def test_assert_modern_publishable_key_accepts_modern() -> None:
    assert_modern_supabase_publishable_key("sb_publishable_abc")


def test_assert_modern_publishable_key_rejects_empty() -> None:
    with pytest.raises(ValueError, match="not set"):
        assert_modern_supabase_publishable_key("")


def test_assert_modern_publishable_key_rejects_legacy_jwt() -> None:
    with pytest.raises(ValueError, match="Legacy Supabase"):
        assert_modern_supabase_publishable_key(_LEGACY_JWT)
