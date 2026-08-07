"""
F21 / ADR-031 abuse controls — rate limits (slowapi) + max request body.

Env knobs (env-contract):
- ``RATE_LIMIT_PUBLIC_PER_MIN`` (default 60)
- ``RATE_LIMIT_DISSEMINATION_PER_MIN`` (default 10)
- ``RATE_LIMIT_MASS_INGEST_PER_MIN`` (default 10) — F33 / EV-042
- ``MAX_REQUEST_BODY_BYTES`` (default 2097152)
- ``MASS_INGEST_MAX_FILES`` / ``MASS_INGEST_MAX_FILE_BYTES`` / ``MASS_INGEST_MAX_TOTAL_BYTES``
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, cast

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, ExceptionHandler, Receive, Scope, Send

DEFAULT_PUBLIC_PER_MIN = 60
DEFAULT_DISSEMINATION_PER_MIN = 10
DEFAULT_MASS_INGEST_PER_MIN = 10
DEFAULT_MAX_BODY_BYTES = 2_097_152
DEFAULT_MASS_INGEST_MAX_FILES = 200
DEFAULT_MASS_INGEST_MAX_FILE_BYTES = 5_242_880
DEFAULT_MASS_INGEST_MAX_TOTAL_BYTES = 52_428_800
MASS_INGEST_PATH_PREFIX = "/api/v1/ingest/mass"


def _positive_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def get_rate_limit_public_per_min() -> int:
    """Return public convert/lint/decode rate limit (requests/minute/IP)."""
    return _positive_int("RATE_LIMIT_PUBLIC_PER_MIN", DEFAULT_PUBLIC_PER_MIN)


def get_rate_limit_dissemination_per_min() -> int:
    """Return dissemination preflight/send rate limit (requests/minute/IP)."""
    return _positive_int("RATE_LIMIT_DISSEMINATION_PER_MIN", DEFAULT_DISSEMINATION_PER_MIN)


def get_rate_limit_mass_ingest_per_min() -> int:
    """Return mass-ingest rate limit (requests/minute/IP)."""
    return _positive_int("RATE_LIMIT_MASS_INGEST_PER_MIN", DEFAULT_MASS_INGEST_PER_MIN)


def get_max_request_body_bytes() -> int:
    """Return max request Content-Length / body size in bytes."""
    return _positive_int("MAX_REQUEST_BODY_BYTES", DEFAULT_MAX_BODY_BYTES)


def get_mass_ingest_max_files() -> int:
    """Return max files per mass-ingest request."""
    return _positive_int("MASS_INGEST_MAX_FILES", DEFAULT_MASS_INGEST_MAX_FILES)


def get_mass_ingest_max_file_bytes() -> int:
    """Return max bytes per file in mass-ingest."""
    return _positive_int("MASS_INGEST_MAX_FILE_BYTES", DEFAULT_MASS_INGEST_MAX_FILE_BYTES)


def get_mass_ingest_max_total_bytes() -> int:
    """Return max total uncompressed bytes for mass-ingest (also mass-route body cap)."""
    return _positive_int("MASS_INGEST_MAX_TOTAL_BYTES", DEFAULT_MASS_INGEST_MAX_TOTAL_BYTES)


def public_limit_string() -> str:
    """slowapi limit string for public API routes."""
    return f"{get_rate_limit_public_per_min()}/minute"


def dissemination_limit_string() -> str:
    """slowapi limit string for dissemination routes."""
    return f"{get_rate_limit_dissemination_per_min()}/minute"


def mass_ingest_limit_string() -> str:
    """slowapi limit string for mass-ingest routes."""
    return f"{get_rate_limit_mass_ingest_per_min()}/minute"


_limiter: Limiter | None = None


def get_limiter() -> Limiter:
    """Return the process-wide Limiter (created once)."""
    global _limiter
    if _limiter is None:
        _limiter = create_limiter()
    return _limiter


def create_limiter() -> Limiter:
    """
    Create an in-memory slowapi Limiter (single Render instance baseline).

    Returns
    -------
    Limiter
        Shared limiter; attach to ``app.state.limiter``.
    """
    return Limiter(
        key_func=get_remote_address,
        default_limits=[public_limit_string()],
        headers_enabled=False,
    )


class MaxBodySizeMiddleware:
    """Reject oversized bodies; mass-ingest path uses ``MASS_INGEST_MAX_TOTAL_BYTES`` (D-S050-C1)."""

    def __init__(
        self,
        app: ASGIApp,
        max_bytes: int | None = None,
        path_prefix: str = "/api/v1",
    ) -> None:
        self.app = app
        self.max_bytes = max_bytes if max_bytes is not None else get_max_request_body_bytes()
        self.path_prefix = path_prefix

    def _limit_for_path(self, path: str) -> int:
        if str(path).startswith(MASS_INGEST_PATH_PREFIX):
            return get_mass_ingest_max_total_bytes()
        return self.max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not str(path).startswith(self.path_prefix):
            await self.app(scope, receive, send)
            return

        max_bytes = self._limit_for_path(str(path))
        headers = {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in scope.get("headers", [])}
        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                length = -1
            if length > max_bytes:
                response = JSONResponse(
                    status_code=413,
                    content={"detail": (f"Request body exceeds maximum of {max_bytes} bytes")},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


def install_abuse_controls(app: FastAPI, limiter: Limiter | None = None) -> Limiter:
    """
    Attach slowapi default limits + body-size middleware to ``app``.

    Parameters
    ----------
    app : FastAPI
        Application instance.
    limiter : Limiter | None
        Optional pre-built limiter (tests); otherwise the process singleton.

    Returns
    -------
    Limiter
        The limiter stored on ``app.state.limiter``.
    """
    global _limiter
    lim = limiter or get_limiter()
    _limiter = lim
    app.state.limiter = lim
    app.add_exception_handler(
        RateLimitExceeded,
        cast(ExceptionHandler, _rate_limit_exceeded_handler),
    )
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(MaxBodySizeMiddleware)
    return lim


def dissemination_limit(limiter: Limiter) -> Callable[..., Any]:
    """Decorator factory for stricter dissemination rate limits."""
    return limiter.limit(dissemination_limit_string())


def mass_ingest_limit(limiter: Limiter) -> Callable[..., Any]:
    """Decorator factory for mass-ingest rate limits."""
    return limiter.limit(mass_ingest_limit_string())


__all__ = [
    "MASS_INGEST_PATH_PREFIX",
    "MaxBodySizeMiddleware",
    "create_limiter",
    "dissemination_limit",
    "dissemination_limit_string",
    "get_limiter",
    "get_mass_ingest_max_file_bytes",
    "get_mass_ingest_max_files",
    "get_mass_ingest_max_total_bytes",
    "get_max_request_body_bytes",
    "get_rate_limit_dissemination_per_min",
    "get_rate_limit_mass_ingest_per_min",
    "get_rate_limit_public_per_min",
    "install_abuse_controls",
    "mass_ingest_limit",
    "mass_ingest_limit_string",
    "public_limit_string",
]
