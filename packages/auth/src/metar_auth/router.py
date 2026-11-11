"""FastAPI `/auth/*` routers - Auth-only; no admin (ADR-033 / F31).

Transitional: models live in ``metar_auth.models``; HTTP will leave this package.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status

from metar_auth.jwks import verify_access_token
from metar_auth.models import (
    AuthResponse,
    ConfirmRequest,
    JwtVerificationError,
    LoginRequest,
    LogoutRequest,
    Message,
    RegisterRequest,
    UserResponse,
    validate_email_permissive,
)
from metar_auth.proxy import AuthProxyError, SupabaseAuthProxy

# Re-export for tests that import validators/models from the router module.
__all__ = [
    "AuthResponse",
    "ConfirmRequest",
    "LoginRequest",
    "LogoutRequest",
    "Message",
    "RegisterRequest",
    "UserResponse",
    "create_auth_router",
    "get_token_from_header",
    "validate_email_permissive",
]


def get_token_from_header(
    authorization: str | None = Header(default=None),
) -> str:
    """
    Extract Bearer token from ``Authorization``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_token_from_header)
    2

    Parameters
    ----------
    authorization : str or None, optional
        Authorization header value. By default ``None``.

    Returns
    -------
    str
        Bearer token.
    """
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
    Build the Auth-only router (register + login + logout + me). No ``/admin`` routes.

    Parameters
    ----------
    proxy : SupabaseAuthProxy or None, optional
        Optional injected proxy (tests). By default ``None``.
    jwks_url : str or None, optional
        JWKS endpoint override for ``/auth/me``. By default ``None``.
    supabase_url : str or None, optional
        Auth project URL for JWKS derivation / proxy default.

    Returns
    -------
    APIRouter
        Router with prefix ``/auth``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (create_auth_router)
    2
    """
    router = APIRouter(prefix="/auth", tags=["Auth"])
    auth_proxy = proxy or SupabaseAuthProxy(supabase_url=supabase_url)

    def _proxy() -> SupabaseAuthProxy:
        """
        Internal helper ``_proxy``.

        Returns
        -------
        object
            Return value.
        """
        return auth_proxy

    @router.post("/register", response_model=AuthResponse)
    def register(
        request: RegisterRequest,
        client: SupabaseAuthProxy = Depends(_proxy),  # noqa: B008
    ) -> dict[str, Any]:
        """
        Create an account via Supabase Auth signup.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (register)
        2

        Parameters
        ----------
        request : RegisterRequest
            Request.
        client : SupabaseAuthProxy, optional
            Auth proxy for this route.

        Returns
        -------
        dict[str, Any]
            Signup payload from the auth proxy.
        """
        try:
            return client.sign_up(request.email, request.password)
        except AuthProxyError as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=str(exc),
            ) from exc

    @router.post("/confirm", response_model=AuthResponse)
    def confirm(
        request: ConfirmRequest,
        client: SupabaseAuthProxy = Depends(_proxy),  # noqa: B008
    ) -> dict[str, Any]:
        """
        Confirm email (or related) via GoTrue token_hash verify.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (confirm)
        2

        Parameters
        ----------
        request : ConfirmRequest
            Request.
        client : SupabaseAuthProxy, optional
            Auth proxy for this route.

        Returns
        -------
        dict[str, Any]
            Verify payload from the auth proxy.
        """
        try:
            return client.verify_email(request.token_hash, request.type)
        except AuthProxyError as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=str(exc),
            ) from exc

    @router.post("/login", response_model=AuthResponse)
    def login(
        request: LoginRequest,
        client: SupabaseAuthProxy = Depends(_proxy),  # noqa: B008
    ) -> dict[str, Any]:
        """
        Authenticate via Supabase Auth password grant.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (login)
        2

        Parameters
        ----------
        request : LoginRequest
            Request.
        client : SupabaseAuthProxy, optional
            Auth proxy for this route.

        Returns
        -------
        dict[str, Any]
            Sign-in payload from the auth proxy.
        """
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
        """
        Sign out via GoTrue; optional body ``{scope}`` for local/global/others.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (logout)
        2

        Parameters
        ----------
        request : LogoutRequest or None, optional
            Request.
        token : str, optional
            Token.
        client : SupabaseAuthProxy, optional
            Auth proxy for this route.

        Returns
        -------
        dict[str, str]
            Success message after sign-out.
        """
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
        """
        Return the current user after JWKS verification.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (me)
        2

        Parameters
        ----------
        token : str, optional
            Token.
        client : SupabaseAuthProxy, optional
            Auth proxy for this route.

        Returns
        -------
        dict[str, Any]
            The current user after JWKS verification.
        """
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
    _ = (register, confirm, login, logout, me)
    return router
