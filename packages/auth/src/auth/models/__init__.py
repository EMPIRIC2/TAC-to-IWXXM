"""Pydantic message and error models for the auth service library."""

from __future__ import annotations

from auth.models.errors import AuthProxyError, JwtVerificationError
from auth.models.messages import (
    AuthResponse,
    ConfirmRequest,
    LoginRequest,
    LogoutRequest,
    Message,
    RegisterRequest,
    SessionResponse,
    UserResponse,
    validate_email_permissive,
)

__all__ = [
    "AuthProxyError",
    "AuthResponse",
    "ConfirmRequest",
    "JwtVerificationError",
    "LoginRequest",
    "LogoutRequest",
    "Message",
    "RegisterRequest",
    "SessionResponse",
    "UserResponse",
    "validate_email_permissive",
]
