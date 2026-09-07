"""Coverage for scripts/utilities/create_admin_user.py."""

from __future__ import annotations

from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from tests.scripts.conftest import load_script


def _load_admin_module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "service-key")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret-pass")
    with (
        patch(
            "metar_shared.supabase_env.get_supabase_url",
            return_value="https://example.supabase.co",
        ),
        patch(
            "metar_shared.supabase_env.get_supabase_secret_key",
            return_value="service-key",
        ),
        patch("dotenv.load_dotenv"),
    ):
        return load_script(
            "utilities/create_admin_user.py", "create_admin_user_testmod"
        )


@pytest.mark.unit
def test_create_admin_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_admin_module(monkeypatch)
    user_resp = MagicMock(status_code=201)
    user_resp.json.return_value = {"id": "user-123"}
    profile_resp = MagicMock(status_code=201)
    with patch.object(mod.requests, "post", side_effect=[user_resp, profile_resp]):
        assert mod.create_admin() == 0


@pytest.mark.unit
def test_create_admin_user_create_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_admin_module(monkeypatch)
    user_resp = MagicMock(status_code=400, text="bad request")
    with patch.object(mod.requests, "post", return_value=user_resp):
        assert mod.create_admin() == 1


@pytest.mark.unit
def test_create_admin_profile_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_admin_module(monkeypatch)
    user_resp = MagicMock(status_code=200)
    user_resp.json.return_value = {"id": "user-123"}
    profile_resp = MagicMock(status_code=500, text="profile fail")
    with patch.object(mod.requests, "post", side_effect=[user_resp, profile_resp]):
        assert mod.create_admin() == 0


@pytest.mark.unit
def test_create_admin_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_admin_module(monkeypatch)
    with patch.object(mod.requests, "post", side_effect=RuntimeError("boom")):
        assert mod.create_admin() == 1


@pytest.mark.unit
def test_module_exits_when_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    with (
        patch("metar_shared.supabase_env.get_supabase_url", return_value=""),
        patch("metar_shared.supabase_env.get_supabase_secret_key", return_value=""),
        patch("dotenv.load_dotenv"),
        pytest.raises(SystemExit) as exc,
    ):
        load_script("utilities/create_admin_user.py", "create_admin_missing_env")
    assert exc.value.code == 1
