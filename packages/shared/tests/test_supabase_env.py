"""Tests for metar_shared.supabase_env."""

from __future__ import annotations

import warnings

import pytest

from metar_shared.supabase_env import (
    get_supabase_publishable_key,
    get_supabase_secret_key,
    get_supabase_url,
)


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
