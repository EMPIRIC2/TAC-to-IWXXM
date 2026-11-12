"""Unit tests for auth pydantic message/error models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from auth.models import (
    AuthProxyError,
    ConfirmRequest,
    JwtVerificationError,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
    validate_email_permissive,
)


@pytest.mark.unit
def test_validate_email_permissive_dev_tld() -> None:
    assert validate_email_permissive("a@b.local") == "a@b.local"


@pytest.mark.unit
def test_validate_email_permissive_rejects_empty() -> None:
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email_permissive("not-an-email")


@pytest.mark.unit
def test_validate_email_permissive_rejects_empty_local_or_domain() -> None:
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email_permissive("@example.com")
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email_permissive("user@")


@pytest.mark.unit
def test_validate_email_permissive_rejects_invalid_public_email() -> None:
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email_permissive("not a valid@bad domain")


@pytest.mark.unit
def test_login_request_normalizes_dev_email() -> None:
    req = LoginRequest(email="User@Test.local", password="secret")
    assert req.email == "user@test.local"


@pytest.mark.unit
def test_register_request_min_password() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password="123")


@pytest.mark.unit
def test_confirm_request_type_validation() -> None:
    with pytest.raises(ValidationError):
        ConfirmRequest(token_hash="abc", type="nope")
    assert ConfirmRequest(token_hash="abc", type="Signup").type == "signup"


@pytest.mark.unit
def test_logout_scope_validation() -> None:
    assert LogoutRequest(scope="").scope is None
    assert LogoutRequest(scope="global").scope == "global"
    with pytest.raises(ValidationError):
        LogoutRequest(scope="everywhere")


@pytest.mark.unit
def test_typed_errors_carry_status() -> None:
    err = AuthProxyError("boom", status_code=503)
    assert err.status_code == 503
    assert str(JwtVerificationError("bad")) == "bad"


@pytest.mark.unit
def test_login_request_rejects_blank_email() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="", password="secret")


@pytest.mark.unit
def test_register_request_normalizes_email_domain() -> None:
    req = RegisterRequest(email="Ops@Example.COM", password="secret1")
    assert req.email.endswith("@example.com")
    assert "@" in req.email


@pytest.mark.unit
def test_confirm_request_requires_token_hash() -> None:
    with pytest.raises(ValidationError):
        ConfirmRequest(token_hash="", type="email")


@pytest.mark.unit
def test_auth_proxy_error_default_status() -> None:
    err = AuthProxyError("proxy down")
    assert err.status_code == 400
    assert str(err) == "proxy down"
