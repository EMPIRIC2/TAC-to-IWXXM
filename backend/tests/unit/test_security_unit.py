"""Unit tests for security auth helpers."""

from __future__ import annotations

import importlib
from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.utilities import security as sec


class _FakeResponse:
    def __init__(self, status_code: int, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *_args, **_kwargs):
        if self.error:
            raise self.error
        return self.response


def _creds(token: str = "valid-token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


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
    payload = {"sub": "user-1", "email": "user@example.com", "authenticated": True}
    monkeypatch.setattr(
        sec.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(response=_FakeResponse(200, payload)),
    )

    result = await sec.verify_supabase_token(_creds())

    assert result == payload


@pytest.mark.asyncio
async def test_verify_supabase_token_invalid_token(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    monkeypatch.setattr(
        sec.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(response=_FakeResponse(401)),
    )

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_supabase_token_auth_service_error(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    monkeypatch.setattr(
        sec.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(response=_FakeResponse(500)),
    )

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_verify_supabase_token_timeout(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    monkeypatch.setattr(
        sec.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(error=httpx.TimeoutException("timeout")),
    )

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 503
    assert "timeout" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_supabase_token_connect_error(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    req = httpx.Request("GET", "http://auth.test/auth/verify")
    monkeypatch.setattr(
        sec.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(error=httpx.ConnectError("connect failed", request=req)),
    )

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(_creds())

    assert exc.value.status_code == 503
    assert "cannot connect" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_supabase_token_unexpected_error(monkeypatch):
    monkeypatch.setattr(sec, "DISABLE_AUTH", False)
    monkeypatch.setenv("DISABLE_AUTH", "false")
    monkeypatch.setattr(
        sec.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(error=RuntimeError("boom")),
    )

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
    assert sec.security.auto_error is False

    monkeypatch.undo()
    importlib.reload(sec)
