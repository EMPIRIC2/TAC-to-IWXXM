"""FastAPI `/auth/*` routers - Auth-only; no admin (ADR-033 / F31)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from metar_auth.jwks import JwtVerificationError, verify_access_token
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy


def validate_email_permissive(email: str) -> str:
    """Validate email; allow common development TLDs."""
    if not email or "@" not in email:
        raise ValueError("Invalid email format")
    local_part, domain = email.rsplit("@", 1)
    if not local_part or not domain:
        raise ValueError("Invalid email format")
    allowed_dev = (".local", ".test", ".localhost", ".dev", ".example")
    if any(domain.endswith(dev) or domain == dev[1:] for dev in allowed_dev):
        return email.lower()
    from email_validator import EmailNotValidError, validate_email

    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        raise ValueError(f"Invalid email: {exc}") from exc


class LoginRequest(BaseModel):
    """Login credentials."""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        return validate_email_permissive(value)


class UserResponse(BaseModel):
    """Auth user projection."""

    id: str
    email: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """Session tokens."""

    access_token: str
    refresh_token: str
    expires_at: int


class AuthResponse(BaseModel):
    """Login response."""

    user: UserResponse
    session: SessionResponse | None = None


class LogoutRequest(BaseModel):
    """Optional scoped logout body (FileConverter / AdminDashboard)."""

    scope: str | None = Field(
        default=None,
        description="GoTrue logout scope: global, local, or others",
    )

    @field_validator("scope")
    @classmethod
    def _scope(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        allowed = {"global", "local", "others"}
        if value not in allowed:
            raise ValueError(f"Unsupported logout scope {value!r}")
        return value


class Message(BaseModel):
    """Simple success message."""

    message: str


def get_token_from_header(
    authorization: str | None = Header(default=None),
) -> str:
    """Extract Bearer token from ``Authorization``."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
        )
    return parts[1]


def create_auth_router(
    *,
    proxy: SupabaseAuthProxy | None = None,
    jwks_url: str | None = None,
    supabase_url: str | None = None,
) -> APIRouter:
    """
    Build the Auth-only router (login + logout + me). No ``/admin`` routes.

    Parameters
    ----------
    proxy : SupabaseAuthProxy or None
        Optional injected proxy (tests).
    jwks_url : str or None
        JWKS endpoint override for ``/auth/me``.
    supabase_url : str or None
        Auth project URL for JWKS derivation / proxy default.

    Returns
    -------
    APIRouter
        Router with prefix ``/auth``.
    """
    router = APIRouter(prefix="/auth", tags=["Auth"])
    auth_proxy = proxy or SupabaseAuthProxy(supabase_url=supabase_url)

    def _proxy() -> SupabaseAuthProxy:
        return auth_proxy

    @router.post("/login", response_model=AuthResponse)
    def login(
        request: LoginRequest,
        client: SupabaseAuthProxy = Depends(_proxy),  # noqa: B008
    ) -> dict[str, Any]:
        """Authenticate via Supabase Auth password grant."""
        try:
            return client.sign_in(request.email, request.password)
        except AuthProxyError as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=str(exc),
            ) from exc

    @router.post("/logout", response_model=Message)
    def logout(
        request: LogoutRequest | None = Body(default=None),  # noqa: B008
        token: str = Depends(get_token_from_header),
        client: SupabaseAuthProxy = Depends(_proxy),  # noqa: B008
    ) -> dict[str, str]:
        """Sign out via GoTrue; optional body ``{scope}`` for local/global/others."""
        body = request or LogoutRequest()
        try:
            return client.sign_out(token, scope=body.scope)
        except AuthProxyError as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=str(exc),
            ) from exc

    @router.get("/me", response_model=UserResponse)
    def me(
        token: str = Depends(get_token_from_header),
        client: SupabaseAuthProxy = Depends(_proxy),  # noqa: B008
    ) -> dict[str, Any]:
        """Return the current user after JWKS verification."""
        try:
            claims = verify_access_token(
                token,
                jwks_url=jwks_url,
                supabase_url=supabase_url or auth_proxy.supabase_url,
            )
        except JwtVerificationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        try:
            user = client.get_user(token)
        except AuthProxyError:
            return {
                "id": str(claims.get("sub") or ""),
                "email": str(claims.get("email") or ""),
                "metadata": {},
            }
        if not user.get("id"):
            user["id"] = str(claims.get("sub") or "")
        return user

    # Keep nested handlers referenced for typecheckers that miss FastAPI decorators.
    _ = (login, logout, me)
    return router
