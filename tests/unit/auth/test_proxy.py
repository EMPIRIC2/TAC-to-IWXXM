"""Unit tests for SupabaseAuthProxy (EV-047 / D-S056-cov95-scope=2)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from metar_auth.proxy import (
    AuthProxyError,
    SupabaseAuthProxy,
    _normalize_session_payload,
)


def test_auth_proxy_error_stores_status_code() -> None:
    err = AuthProxyError("boom", status_code=503)
    assert str(err) == "boom"
    assert err.status_code == 503


def test_auth_proxy_error_default_status() -> None:
    assert AuthProxyError("x").status_code == 400


def test_init_reads_env_and_anon_key_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://proj.supabase.co/")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon-key")
    proxy = SupabaseAuthProxy()
    assert proxy.supabase_url == "https://proj.supabase.co"
    assert proxy.publishable_key == "anon-key"
    assert proxy._owns_client is True


def test_init_prefers_explicit_and_injected_client() -> None:
    client = MagicMock(spec=httpx.Client)
    proxy = SupabaseAuthProxy(
        supabase_url="https://a.example/",
        publishable_key="pk",
        client=client,
    )
    assert proxy.supabase_url == "https://a.example"
    assert proxy.publishable_key == "pk"
    assert proxy._owns_client is False
    assert proxy._http() is client


def test_http_lazily_creates_owned_client() -> None:
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
    )
    assert proxy._client is None
    http = proxy._http()
    assert isinstance(http, httpx.Client)
    assert proxy._http() is http
    proxy.close()
    assert proxy._client is None


def test_close_noop_when_client_injected() -> None:
    client = MagicMock(spec=httpx.Client)
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    proxy.close()
    client.close.assert_not_called()
    assert proxy._client is client


def test_close_noop_when_never_opened() -> None:
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
    )
    proxy.close()  # no-op
    assert proxy._client is None


def test_headers_missing_env_raises_503() -> None:
    proxy = SupabaseAuthProxy(supabase_url="", publishable_key="")
    with pytest.raises(AuthProxyError, match="SUPABASE_URL") as exc_info:
        proxy._headers()
    assert exc_info.value.status_code == 503


def test_headers_missing_key_only_raises_503() -> None:
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="",
    )
    with pytest.raises(AuthProxyError) as exc_info:
        proxy._headers()
    assert exc_info.value.status_code == 503


def test_sign_in_success_normalizes_payload() -> None:
    client = MagicMock(spec=httpx.Client)
    client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "access_token": "at",
            "refresh_token": "rt",
            "expires_at": 99,
            "user": {
                "id": "u1",
                "email": "a@example.com",
                "user_metadata": {"role": "op"},
            },
        },
    )
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    out = proxy.sign_in("a@example.com", "secret")
    assert out["user"]["id"] == "u1"
    assert out["user"]["metadata"] == {"role": "op"}
    assert out["session"]["access_token"] == "at"
    assert out["session"]["expires_at"] == 99
    client.post.assert_called_once()
    call_kwargs = client.post.call_args
    assert "grant_type=password" in call_kwargs.args[0]
    assert call_kwargs.kwargs["json"] == {
        "email": "a@example.com",
        "password": "secret",
    }


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (400, 401),
        (401, 401),
        (500, 502),
        (503, 502),
    ],
)
def test_sign_in_maps_http_errors(status_code: int, expected: int) -> None:
    client = MagicMock(spec=httpx.Client)
    client.post.return_value = MagicMock(
        status_code=status_code,
        text="denied",
    )
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    with pytest.raises(AuthProxyError, match="login failed") as exc_info:
        proxy.sign_in("a@example.com", "bad")
    assert exc_info.value.status_code == expected


def test_sign_in_missing_config_propagates_503() -> None:
    client = MagicMock(spec=httpx.Client)
    proxy = SupabaseAuthProxy(
        supabase_url="",
        publishable_key="",
        client=client,
    )
    with pytest.raises(AuthProxyError) as exc_info:
        proxy.sign_in("a@example.com", "x")
    assert exc_info.value.status_code == 503
    client.post.assert_not_called()


def test_get_user_success() -> None:
    client = MagicMock(spec=httpx.Client)
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "id": "u9",
            "email": "b@example.com",
            "user_metadata": {"k": 1},
        },
    )
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    user = proxy.get_user("access-tok")
    assert user == {
        "id": "u9",
        "email": "b@example.com",
        "metadata": {"k": 1},
    }
    headers = client.get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer access-tok"
    assert headers["apikey"] == "pk"


def test_get_user_error_raises_401() -> None:
    client = MagicMock(spec=httpx.Client)
    client.get.return_value = MagicMock(status_code=401, text="nope")
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    with pytest.raises(AuthProxyError, match="user lookup") as exc_info:
        proxy.get_user("tok")
    assert exc_info.value.status_code == 401


def test_get_user_defaults_missing_fields() -> None:
    client = MagicMock(spec=httpx.Client)
    client.get.return_value = MagicMock(status_code=200, json=lambda: {})
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    assert proxy.get_user("tok") == {"id": "", "email": "", "metadata": {}}


def test_normalize_session_payload_defaults() -> None:
    out = _normalize_session_payload({})
    assert out == {
        "user": {"id": "", "email": "", "metadata": {}},
        "session": {
            "access_token": "",
            "refresh_token": "",
            "expires_at": 0,
        },
    }


def test_normalize_session_payload_partial_user() -> None:
    data: dict[str, Any] = {
        "access_token": "a",
        "user": {"email": "x@y.z"},
    }
    out = _normalize_session_payload(data)
    assert out["user"]["email"] == "x@y.z"
    assert out["user"]["id"] == ""
    assert out["session"]["access_token"] == "a"
    assert out["session"]["expires_at"] == 0
