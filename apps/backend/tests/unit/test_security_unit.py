"""Unit tests for security auth helpers."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.utilities import security as sec


class _FakeProxy:
    def __init__(
        self,
        *,
        verify: bool = True,
        user: dict | None = None,
        init_error: Exception | None = None,
        verify_error: Exception | None = None,
        get_user_error: Exception | None = None,
    ) -> None:
        self._verify = verify
        self._user = user or {
            "id": "user-1",
            "email": "user@example.com",
            "metadata": {},
        }
        self._init_error = init_error
        self._verify_error = verify_error
        self._get_user_error = get_user_error

    def verify_token(self, _token: str) -> bool:
        if self._verify_error:
            raise self._verify_error
        return self._verify

    def get_user(self, _token: str) -> dict:
        if self._get_user_error:
            raise self._get_user_error
        return self._user


def _creds(token: str = "valid-token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _patch_proxy(monkeypatch: pytest.MonkeyPatch, proxy: _FakeProxy) -> None:
    monkeypatch.setattr(sec, "get_supabase_proxy", lambda: proxy)


@pytest.mark.asyncio
async def test_verify_supabase_token_dev_mode_constant_bypass(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", True)
    monkeypatch.delenv("DISABLE_AUTH", raising=False)
    monkeypatch.setenv("ADMIN_USER_ID", "admin-123")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")

    result = await sec.verify_supabase_token(None)

    assert result["sub"] == "admin-123"
    assert result["email"] == "admin@example.com"
    assert result["environment"] == "development"


@pytest.mark.asyncio
async def test_verify_supabase_token_dev_mode_runtime_bypass(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "true")

    result = await sec.verify_supabase_token(None)

    assert result["authenticated"] is False
    assert result["environment"] == "development"


@pytest.mark.asyncio
async def test_verify_supabase_token_missing_credentials(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(None)

    assert exc.value.status_code == 401
    assert "Missing authorization credentials" in exc.value.detail


@pytest.mark.asyncio
async def test_verify_supabase_token_success(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    _patch_proxy(
        monkeypatch,
        _FakeProxy(
            user={
                "id": "user-1",
                "email": "user@example.com",
                "metadata": {"role": "tester"},
            }
        ),
    )

    result = await sec.verify_supabase_token(_creds())

    assert result["sub"] == "user-1"
    assert result["email"] == "user@example.com"
    assert result["authenticated"] is True


@pytest.mark.asyncio
async def test_verify_supabase_token_invalid_token(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    _patch_proxy(monkeypatch, _FakeProxy(verify=False))

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_supabase_token_auth_not_configured(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    monkeypatch.setattr(
        sec,
        "get_supabase_proxy",
        lambda: (_ for _ in ()).throw(ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")),
    )

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 503
    assert "not configured" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_supabase_token_get_user_http_exception(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    _patch_proxy(
        monkeypatch,
        _FakeProxy(
            get_user_error=HTTPException(
                status_code=401,
                detail="Failed to get user: session expired",
            )
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_supabase_token_unexpected_error(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    _patch_proxy(monkeypatch, _FakeProxy(get_user_error=RuntimeError("boom")))

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 500
    assert "Token verification failed" in exc.value.detail


@pytest.mark.asyncio
async def test_fetch_jwks_not_implemented():
    with pytest.raises(NotImplementedError):
        await sec.fetch_jwks()


def test_security_module_reload_without_env_file(monkeypatch):
    original_exists = Path.exists

    def fake_exists(path: Path) -> bool:
        if str(path).endswith("/.env"):
            return False
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", fake_exists)
    importlib.reload(sec)

    assert sec.env_file.name == ".env"
