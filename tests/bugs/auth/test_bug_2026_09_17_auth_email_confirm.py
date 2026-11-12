"""BUG-2026-09-17 — email confirm must verify token_hash (FE-direct / proxy).

Repro: registration leaves users unconfirmed because the app never calls GoTrue
verify with the email template ``token_hash``. Login then fails with
``email_not_confirmed``.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from auth.proxy import AuthProxyError, SupabaseAuthProxy


@pytest.mark.unit
def test_bug_2026_09_17_auth_confirm_exchanges_token_hash() -> None:
    """Proxy verify_email must call GoTrue verify and return a session payload."""
    client = MagicMock(spec=httpx.Client)
    client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "user": {"id": "u1", "email": "op@example.com", "user_metadata": {}},
            "access_token": "at",
            "refresh_token": "rt",
            "expires_at": 99,
        },
    )
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    body = proxy.verify_email("abc123hash", "email")
    assert body["session"]["access_token"] == "at"
    assert body["user"]["email"] == "op@example.com"
    client.post.assert_called_once()
    args, kwargs = client.post.call_args
    assert args[0].endswith("/auth/v1/verify")
    assert kwargs["json"] == {"token_hash": "abc123hash", "type": "email"}


@pytest.mark.unit
def test_bug_2026_09_17_sign_in_maps_email_not_confirmed() -> None:
    """Password grant email_not_confirmed → operator-facing confirm message."""
    client = MagicMock(spec=httpx.Client)
    client.post.return_value = MagicMock(
        status_code=400,
        text='{"code":400,"error_code":"email_not_confirmed","msg":"Email not confirmed"}',
    )
    proxy = SupabaseAuthProxy(
        supabase_url="https://proj.supabase.co",
        publishable_key="pk",
        client=client,
    )
    with pytest.raises(AuthProxyError) as exc_info:
        proxy.sign_in("op@example.com", "password123")
    assert exc_info.value.status_code == 401
    assert "confirm your email" in str(exc_info.value).lower()
    assert "email_not_confirmed" not in str(exc_info.value)
