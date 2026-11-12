"""Auth message validators — email / confirm / logout failure edges."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from auth.models.messages import (
    ConfirmRequest,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
    validate_email_permissive,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "email",
    [
        "ops@local",
        "ops@test",
        "ops@localhost",
        "ops@dev",
        "ops@example",
    ],
)
def test_validate_email_permissive_accepts_bare_dev_domains(email: str) -> None:
    """``domain == dev[1:]`` branch for bare development TLDs."""
    assert validate_email_permissive(email) == email.lower()


@pytest.mark.unit
def test_validate_email_permissive_rejects_whitespace_only() -> None:
    with pytest.raises(ValueError, match="Invalid email format"):
        validate_email_permissive("   ")


@pytest.mark.unit
def test_login_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError) as exc_info:
        LoginRequest(email="not-an-email", password="secret")
    assert "email" in str(exc_info.value).lower()


@pytest.mark.unit
def test_register_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(email="@nodomain", password="secret1")


@pytest.mark.unit
@pytest.mark.parametrize(
    "type_",
    ["email", "signup", "invite", "magiclink", "recovery", "email_change"],
)
def test_confirm_request_accepts_allowed_types(type_: str) -> None:
    req = ConfirmRequest(token_hash="abc123", type=type_.upper())
    assert req.type == type_


@pytest.mark.unit
def test_confirm_request_rejects_blank_type() -> None:
    with pytest.raises(ValidationError):
        ConfirmRequest(token_hash="abc123", type="")


@pytest.mark.unit
def test_confirm_request_rejects_unknown_type_message() -> None:
    with pytest.raises(ValidationError, match="Unsupported confirmation type"):
        ConfirmRequest(token_hash="abc123", type="sms")


@pytest.mark.unit
@pytest.mark.parametrize("scope", ["local", "others", "global"])
def test_logout_request_accepts_allowed_scopes(scope: str) -> None:
    assert LogoutRequest(scope=scope).scope == scope


@pytest.mark.unit
def test_logout_request_none_scope_unchanged() -> None:
    assert LogoutRequest().scope is None
    assert LogoutRequest(scope=None).scope is None


@pytest.mark.unit
def test_logout_request_rejects_unknown_scope() -> None:
    with pytest.raises(ValidationError, match="Unsupported logout scope"):
        LogoutRequest(scope="session")
