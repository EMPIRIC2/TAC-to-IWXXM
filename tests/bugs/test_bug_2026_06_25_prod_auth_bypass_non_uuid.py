"""BUG-2026-06-25 — F5 work-session persist 502 caused by prod auth bypass.

Production ran with ``DISABLE_AUTH=true`` and ``ADMIN_USER_ID=dev-user-12345``.
``verify_supabase_token`` bypassed auth and returned the non-UUID dev user id,
which PostgREST rejected on insert::

    invalid input syntax for type uuid: "dev-user-12345"  (code 22P02)

mapped to an opaque 502 ``Work session database error``.

Root cause: a development-only auth bypass was honoured in a production
environment. Hardening: ``verify_supabase_token`` must never bypass auth when
``METAR_CONFIG_ENV`` indicates production, regardless of ``DISABLE_AUTH``.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[2] / "apps" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.utilities import security as sec  # noqa: E402


def _creds(token: str = "valid-token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


class _FakeProxy:
    """Minimal proxy stand-in that verifies and returns a real UUID user."""

    def verify_token(self, _token: str) -> bool:
        return True

    def get_user(self, _token: str) -> dict:
        return {
            "id": "27f7a37c-5575-4e19-a6d6-338755caec1d",
            "email": "admin@metar.local",
            "metadata": {},
        }


@pytest.mark.asyncio
async def test_prod_does_not_bypass_auth_when_disable_auth_true_no_credentials(
    monkeypatch,
):
    """In prod, DISABLE_AUTH must be ignored: missing credentials -> 401, not dev bypass."""
    monkeypatch.setattr(sec, "DISABLE_AUTH", True)
    monkeypatch.setenv("DISABLE_AUTH", "true")
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    # Even if a stray dev user id is present, prod must never emit it.
    monkeypatch.setenv("ADMIN_USER_ID", "dev-user-12345")

    with pytest.raises(HTTPException) as exc:
        await sec.verify_supabase_token(None)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_prod_verifies_real_token_and_returns_uuid_subject(monkeypatch):
    """In prod with DISABLE_AUTH=true, a valid token still resolves to the real UUID."""
    monkeypatch.setattr(sec, "DISABLE_AUTH", True)
    monkeypatch.setenv("DISABLE_AUTH", "true")
    monkeypatch.setenv("METAR_CONFIG_ENV", "prod")
    monkeypatch.setattr(sec, "get_supabase_proxy", lambda: _FakeProxy())

    result = await sec.verify_supabase_token(_creds())

    assert result["authenticated"] is True
    assert result["sub"] == "27f7a37c-5575-4e19-a6d6-338755caec1d"
    # Never the non-UUID dev fallback that broke PostgREST inserts.
    assert result["sub"] != "dev-user-12345"


@pytest.mark.asyncio
async def test_non_prod_bypass_still_allowed(monkeypatch):
    """Local/dev bypass behaviour is preserved (guard is prod-only)."""
    monkeypatch.setattr(sec, "DISABLE_AUTH", True)
    monkeypatch.setenv("DISABLE_AUTH", "true")
    monkeypatch.setenv("METAR_CONFIG_ENV", "local")

    result = await sec.verify_supabase_token(None)

    assert result["authenticated"] is False
    assert result["environment"] == "development"
