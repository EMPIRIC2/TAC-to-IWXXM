"""API key middleware for public routes (NFR-007 / D-029)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

try:
    from ..services.api_key_store import (
        api_key_required_enabled,
        verify_plaintext_key,
    )
except ImportError:  # pragma: no cover - script load
    from services.api_key_store import (  # type: ignore[no-redef]
        api_key_required_enabled,
        verify_plaintext_key,
    )

API_KEY_HEADER = "x-api-key"
REQUEST_STATE_ATTR = "api_key_identity"

_EXEMPT_EXACT = {
    "/health",
    "/metrics",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/favicon.ico",
}
_EXEMPT_PREFIXES = (
    "/docs/",
    "/redoc/",
)


def path_is_api_key_exempt(method: str, path: str) -> bool:
    """
    Return True when the route does not require ``X-API-Key``.

    Parameters
    ----------
    method : str
        HTTP method.
    path : str
        Request path.

    Returns
    -------
    bool
        Exemption flag.
    """
    upper = method.upper()
    if upper == "OPTIONS":
        return True
    if path in _EXEMPT_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in _EXEMPT_PREFIXES):
        return True
    return (upper, path) in {("POST", "/api/v1/api-keys")}


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Require ``X-API-Key`` on protected routes when enforcement is enabled.

    Attributes
    ----------
    (inherited)
        Starlette ``BaseHTTPMiddleware`` app handle.
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Parameters
        ----------
        app : ASGIApp
            Downstream app.
        """
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Validate API key before protected handlers.

        Parameters
        ----------
        request : Request
            Incoming request.
        call_next : callable
            Downstream.

        Returns
        -------
        Response
            Downstream or 401.
        """
        if not api_key_required_enabled():
            return await call_next(request)
        if path_is_api_key_exempt(request.method, request.url.path):
            return await call_next(request)
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        raw = request.headers.get(API_KEY_HEADER)
        if raw is None or not str(raw).strip():
            return JSONResponse(
                status_code=401,
                content={"detail": "API key required"},
            )
        verified = verify_plaintext_key(str(raw))
        if verified is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API key"},
            )
        setattr(request.state, REQUEST_STATE_ATTR, verified)
        return await call_next(request)


def install_api_key_auth(app: object) -> None:
    """
    Attach ``ApiKeyAuthMiddleware`` to a FastAPI app.

    Parameters
    ----------
    app : object
        FastAPI application.
    """
    add_middleware = getattr(app, "add_middleware", None)
    if callable(add_middleware):
        add_middleware(ApiKeyAuthMiddleware)
