"""Additional coverage tests for api_supabase and database modules."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from unittest.mock import Mock
from unittest.mock import patch

from auth.api_supabase import get_token_from_header, validate_email_permissive
from auth.api_supabase import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    register,
    login,
    logout,
    legacy_logout,
    get_current_user,
    refresh_token,
    request_password_reset,
    confirm_password_reset,
    verify_token,
)


def test_get_token_from_header_with_valid_bearer_token() -> None:
    token = get_token_from_header("Bearer abc.def.ghi")
    assert token == "abc.def.ghi"


@pytest.mark.parametrize(
    "header_value",
    [
        None,
        "",
        "Bearer",
        "Token abc",
        "Bearer a b",
    ],
)
def test_get_token_from_header_rejects_invalid_formats(header_value: str | None) -> None:
    with pytest.raises(HTTPException) as exc:
        get_token_from_header(header_value)
    assert exc.value.status_code == 401


def test_validate_email_permissive_accepts_dev_domain() -> None:
    email = validate_email_permissive("Admin@Test.Dev")
    assert email == "Admin@test.dev"


def test_validate_email_permissive_rejects_missing_local_or_domain() -> None:
    with pytest.raises(ValueError):
        validate_email_permissive("@example.com")
    with pytest.raises(ValueError):
        validate_email_permissive("user@")


def test_validate_email_permissive_wraps_non_dev_validation_errors() -> None:
    with pytest.raises(ValueError) as exc:
        validate_email_permissive("user@bad_domain")
    assert "Invalid email:" in str(exc.value)


def test_database_module_exposes_database_url_and_engine() -> None:
    import auth.database as database

    assert database.DATABASE_URL
    assert database.engine is not None
    assert str(database.engine.url)


def test_database_init_db_calls_model_import_and_create_all() -> None:
    import auth.database as database

    with patch.object(database, "_ensure_models_imported") as ensure_models, patch.object(
        database.Base.metadata,
        "create_all",
    ) as create_all:
        database.init_db()

    ensure_models.assert_called_once()
    create_all.assert_called_once_with(bind=database.engine)


def test_database_ensure_models_imported_ignores_import_error() -> None:
    import builtins
    import auth.database as database

    original_import = builtins.__import__

    def raising_import(name: str, *args, **kwargs):
        if name == "auth":
            raise ImportError("forced test import failure")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=raising_import):
        database._ensure_models_imported()


def test_register_builds_metadata_and_returns_proxy_response() -> None:
    proxy = Mock()
    proxy.sign_up.return_value = {"user": {"id": "1", "email": "u@example.com"}, "session": None}
    request = RegisterRequest(
        email="u@example.com",
        password="password123",
        name="Unit User",
        username="unituser",
    )

    response = register(request=request, proxy=proxy)

    assert response["user"]["id"] == "1"
    proxy.sign_up.assert_called_once_with(
        "u@example.com",
        "password123",
        {"name": "Unit User", "username": "unituser"},
    )


def test_register_omits_empty_optional_metadata() -> None:
    proxy = Mock()
    proxy.sign_up.return_value = {"user": {"id": "2", "email": "u2@example.com"}, "session": None}
    request = RegisterRequest(email="u2@example.com", password="password123")

    register(request=request, proxy=proxy)

    proxy.sign_up.assert_called_once_with("u2@example.com", "password123", {})


def test_login_success_and_failure_branches() -> None:
    request = LoginRequest(email="user@example.com", password="password123")

    success_proxy = Mock()
    success_proxy.sign_in.return_value = {
        "user": {"id": "abc", "email": "user@example.com"},
        "session": {"access_token": "token", "refresh_token": "refresh", "expires_at": 123},
    }
    success_result = login(request=request, proxy=success_proxy)
    assert success_result["user"]["id"] == "abc"

    failure_proxy = Mock()
    failure_proxy.sign_in.side_effect = RuntimeError("auth failed")
    with pytest.raises(RuntimeError, match="auth failed"):
        login(request=request, proxy=failure_proxy)


def test_logout_and_legacy_logout_delegate_to_sign_out() -> None:
    proxy = Mock()
    proxy.sign_out.return_value = {"message": "signed out"}

    standard = logout(token="token-1", proxy=proxy)
    legacy = legacy_logout(token="token-2", proxy=proxy)

    assert standard["message"] == "signed out"
    assert legacy["message"] == "signed out"
    assert proxy.sign_out.call_count == 2


def test_me_refresh_and_password_reset_paths_delegate_to_proxy() -> None:
    proxy = Mock()
    proxy.get_user.return_value = {"id": "u1", "email": "user@example.com", "metadata": {}}
    proxy.refresh_session.return_value = {
        "access_token": "new-token",
        "refresh_token": "new-refresh",
        "expires_at": 456,
    }
    proxy.reset_password_email.return_value = {"message": "email sent"}
    proxy.update_password.return_value = {"message": "password updated"}

    me_result = get_current_user(token="token", proxy=proxy)
    refresh_result = refresh_token(request=RefreshRequest(refresh_token="refresh"), proxy=proxy)
    reset_request_result = request_password_reset(
        request=PasswordResetRequest(email="user@example.com"),
        proxy=proxy,
    )
    reset_confirm_result = confirm_password_reset(
        request=PasswordResetConfirm(new_password="password456"),
        token="reset-token",
        proxy=proxy,
    )

    assert me_result["id"] == "u1"
    assert refresh_result["access_token"] == "new-token"
    assert reset_request_result["message"] == "email sent"
    assert reset_confirm_result["message"] == "password updated"


def test_verify_token_returns_success_and_raises_on_invalid() -> None:
    valid_proxy = Mock()
    valid_proxy.verify_token.return_value = True
    assert verify_token(token="token", proxy=valid_proxy) == {"message": "Token is valid"}

    invalid_proxy = Mock()
    invalid_proxy.verify_token.return_value = False
    with pytest.raises(HTTPException) as exc:
        verify_token(token="token", proxy=invalid_proxy)
    assert exc.value.status_code == 401
