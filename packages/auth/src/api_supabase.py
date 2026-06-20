"""Authentication API router - Supabase Proxy.

Endpoints that proxy authentication requests to Supabase:
- POST /auth/register        (create user via Supabase)
- POST /auth/login           (authenticate via Supabase)
- POST /auth/logout          (sign out via Supabase)
- GET  /auth/me              (get current user from token)
- POST /auth/refresh         (refresh access token)
- POST /auth/password-reset/request  (send reset email)
- POST /auth/password-reset/confirm  (update password)
- GET  /health               (health check)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from auth.supabase_proxy import SupabaseAuthProxy, get_supabase_proxy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])
legacy_router = APIRouter(tags=["Auth"])


# Custom email type that allows special domains for development
def validate_email_permissive(email: str) -> str:
    """Validate email with permissive rules for development domains."""
    if not email or "@" not in email:
        raise ValueError("Invalid email format")

    local_part, domain = email.rsplit("@", 1)

    if not local_part or not domain:
        raise ValueError("Invalid email format")

    # Allow special domains for development (.local, .test, .localhost, etc.)
    allowed_dev_domains = [".local", ".test", ".localhost", ".dev", ".example"]
    is_dev_domain = any(domain.endswith(dev) or domain == dev[1:] for dev in allowed_dev_domains)

    if is_dev_domain:
        logger.debug(f"Allowing development email domain: {email}")
        return email.lower()

    # For production domains, use standard validation
    from email_validator import EmailNotValidError, validate_email

    try:
        validated = validate_email(email, check_deliverability=False)
        return validated.normalized
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {str(e)}")


# Request/Response Models
class RegisterRequest(BaseModel):
    """User registration request."""

    email: str
    password: str = Field(min_length=8)
    name: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        return validate_email_permissive(v)


class LoginRequest(BaseModel):
    """User login request."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        return validate_email_permissive(v)


class UserResponse(BaseModel):
    """User information response."""

    id: str
    email: str
    metadata: Dict[str, Any] = {}


class SessionResponse(BaseModel):
    """Session token response."""

    access_token: str
    refresh_token: str
    expires_at: int


class AuthResponse(BaseModel):
    """Complete authentication response."""

    user: UserResponse
    session: Optional[SessionResponse] = None


class RefreshRequest(BaseModel):
    """Token refresh request."""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset email request."""

    email: str

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str) -> str:
        return validate_email_permissive(v)


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""

    new_password: str = Field(min_length=8)


class Message(BaseModel):
    """Generic message response."""

    message: str


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate bearer token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        Access token string

    Raises:
        HTTPException: If token is missing or invalid format
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
        )

    return parts[1]


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Register a new user via Supabase.

    Args:
        request: Registration details (email, password, metadata)
        proxy: Supabase authentication proxy

    Returns:
        User information and session tokens
    """
    logger.info(f"[API] POST /auth/register - email: {request.email}")
    metadata = {}
    if request.name:
        metadata["name"] = request.name
    if request.username:
        metadata["username"] = request.username

    result = proxy.sign_up(request.email, request.password, metadata)
    logger.info(f"[API] POST /auth/register - success for {request.email}")
    return result


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Authenticate user via Supabase.

    Args:
        request: Login credentials (email, password)
        proxy: Supabase authentication proxy

    Returns:
        User information and session tokens
    """
    logger.info("=" * 80)
    logger.info("[API] 🔐 POST /auth/login - STARTING")
    logger.info(f"  Email: {request.email}")
    logger.info(f"  Password length: {len(request.password)} chars")
    logger.info(f"  Request type: {type(request)}")
    logger.info("=" * 80)

    try:
        result = proxy.sign_in(request.email, request.password)
        logger.info("=" * 80)
        logger.info(f"[API] ✓ POST /auth/login - SUCCESS for {request.email}")
        logger.info(f"  User ID: {result.get('user', {}).get('id', 'UNKNOWN')}")
        logger.info(f"  Has session: {result.get('session') is not None}")
        logger.info("=" * 80)
        return result
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"[API] ✗ POST /auth/login - FAILED for {request.email}")
        logger.error(f"  Error type: {type(e).__name__}")
        logger.error(f"  Error message: {str(e)}")
        logger.error("=" * 80)
        raise


def _logout_with_token(
    token: str = Depends(get_token_from_header), proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)
):
    """Shared logout implementation for canonical and legacy routes."""
    result = proxy.sign_out(token)
    return result


@router.post("/logout", response_model=Message)
def logout(token: str = Depends(get_token_from_header), proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Sign out the current user.

    Args:
        token: User's access token from Authorization header
        proxy: Supabase authentication proxy

    Returns:
        Success message
    """
    logger.info("[API] POST /auth/logout")
    result = _logout_with_token(token=token, proxy=proxy)
    logger.info("[API] POST /auth/logout - success")
    return result


@legacy_router.post("/logout", response_model=Message)
def legacy_logout(token: str = Depends(get_token_from_header), proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Compatibility alias for legacy clients still posting to /logout."""
    logger.info("[API] POST /logout (compat alias)")
    result = _logout_with_token(token=token, proxy=proxy)
    logger.info("[API] POST /logout (compat alias) - success")
    return result


@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(get_token_from_header), proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)
):
    """Get current user information from access token.

    Args:
        token: User's access token from Authorization header
        proxy: Supabase authentication proxy

    Returns:
        User information
    """
    logger.info("[API] GET /auth/me")
    result = proxy.get_user(token)
    logger.info("[API] GET /auth/me - success")
    return result


@router.post("/refresh", response_model=SessionResponse)
def refresh_token(request: RefreshRequest, proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Refresh an expired access token.

    Args:
        request: Refresh token
        proxy: Supabase authentication proxy

    Returns:
        New session tokens
    """
    logger.info("[API] POST /auth/refresh")
    result = proxy.refresh_session(request.refresh_token)
    logger.info("[API] POST /auth/refresh - success")
    return result


@router.post("/password-reset/request", response_model=Message)
def request_password_reset(request: PasswordResetRequest, proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Send password reset email via Supabase.

    Args:
        request: Email address for password reset
        proxy: Supabase authentication proxy

    Returns:
        Success message
    """
    logger.info(f"[API] POST /auth/password-reset/request - email: {request.email}")
    result = proxy.reset_password_email(request.email)
    logger.info(f"[API] POST /auth/password-reset/request - success for {request.email}")
    return result


@router.post("/password-reset/confirm", response_model=Message)
def confirm_password_reset(
    request: PasswordResetConfirm,
    token: str = Depends(get_token_from_header),
    proxy: SupabaseAuthProxy = Depends(get_supabase_proxy),
):
    """Update password after reset.

    Args:
        request: New password
        token: Reset token from Authorization header
        proxy: Supabase authentication proxy

    Returns:
        Success message
    """
    logger.info("[API] POST /auth/password-reset/confirm")
    result = proxy.update_password(token, request.new_password)
    logger.info("[API] POST /auth/password-reset/confirm - success")
    return result


@router.get("/verify")
def verify_token(token: str = Depends(get_token_from_header), proxy: SupabaseAuthProxy = Depends(get_supabase_proxy)):
    """Verify if a token is valid.

    Used by backend services to validate user tokens.

    Args:
        token: Access token to verify
        proxy: Supabase authentication proxy

    Returns:
        User info if valid, 401 if invalid
    """
    logger.info("[API] GET /auth/verify")
    is_valid = proxy.verify_token(token)
    if not is_valid:
        logger.warning("[API] GET /auth/verify - invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    logger.info("[API] GET /auth/verify - success")
    return {"message": "Token is valid"}
