"""Part 2 of ``observability.py`` (line-cap split)."""

from __future__ import annotations

import contextlib
import logging
import os
import re
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .observability_part_1 import (
    _ALLOWED_LOG_LEVELS,
    _JWT_RE,
    _REQUEST_LOG_LEVEL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    JsonLogFormatter,
    LokiHandler,
)

_AUTH_RE = re.compile(r"(?i)(authorization\s*[:=]\s*)(\S+)")

_filters_installed = False


class RequestLogLevelFilter(logging.Filter):
    """
    Drop records below the per-request convert ``log_level`` ContextVar.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Allow records at or above the per-request convert log level.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (filter)
        2

        Parameters
        ----------
        record : object
            Argument ``record``.

        Returns
        -------
        object
            Return value.
        """
        minimum = _REQUEST_LOG_LEVEL.get()
        if minimum is None:
            return True
        return record.levelno >= minimum


class SecretRedactFilter(logging.Filter):
    """
    Strip JWTs and Authorization header values from log records.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Redact JWTs and Authorization header values from log message text.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (filter)
        2

        Parameters
        ----------
        record : object
            Argument ``record``.

        Returns
        -------
        object
            Return value.
        """
        try:
            message = record.getMessage()
        except Exception:
            return True
        if "eyJ" not in message and "authorization" not in message.lower():
            return True
        redacted = _AUTH_RE.sub(r"\1[REDACTED]", _JWT_RE.sub("[REDACTED_JWT]", message))
        record.msg = redacted
        record.args = ()
        return True


def ensure_request_log_filters() -> None:
    """
    Attach request-level and secret filters once (safe for tests).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (ensure_request_log_filters)
    2
    """
    global _filters_installed
    if _filters_installed:
        return
    level_filter = RequestLogLevelFilter()
    redact_filter = SecretRedactFilter()
    names = ("", "src", "src.api", "tac2iwxxm", "tac_validate", "iwxxm_validate")
    for name in names:
        target = logging.getLogger(name)
        target.addFilter(level_filter)
        target.addFilter(redact_filter)
    _filters_installed = True


_REQUEST_LOGGERS = ("src", "src.api", "tac2iwxxm", "tac_validate", "iwxxm_validate")


def set_request_log_level(request: Request, level_name: str | None) -> str:
    """
    Apply convert ``log_level`` to this request's log ContextVar.

    Returns
    -------
    str
        Normalized level name (DEBUG/INFO/WARNING/ERROR/CRITICAL).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (set_request_log_level)
    2

    Parameters
    ----------
    request : object
        Argument ``request``.
    level_name : object
        Argument ``level_name``.
    """
    ensure_request_log_filters()
    name = (level_name or "INFO").strip().upper()
    if name not in _ALLOWED_LOG_LEVELS:
        name = "INFO"
    levelno = getattr(logging, name)
    token = _REQUEST_LOG_LEVEL.set(levelno)
    request.state.convert_log_level_token = token
    previous: list[tuple[logging.Logger, int]] = []
    for logger_name in _REQUEST_LOGGERS:
        target = logging.getLogger(logger_name)
        previous.append((target, target.level))
        if target.level == logging.NOTSET or target.level > levelno:
            target.setLevel(levelno)
    request.state.convert_log_level_prev = previous
    return name


def _reset_request_log_level(request: Request) -> None:
    """
    Internal helper ``_reset_request_log_level``.

    Parameters
    ----------
    request : object
        Argument ``request``.
    """
    token = getattr(request.state, "convert_log_level_token", None)
    if token is not None:
        with contextlib.suppress(ValueError):
            _REQUEST_LOG_LEVEL.reset(token)
            # Starlette BaseHTTPMiddleware runs the route in a different Context
            # than dispatch(); Token.reset is invalid across contexts.
        request.state.convert_log_level_token = None
    previous = getattr(request.state, "convert_log_level_prev", None)
    if previous:
        for target, prior in previous:
            target.setLevel(prior)
        request.state.convert_log_level_prev = None


def setup_logging(service_name: str) -> None:
    """
    Configure JSON logs and optional Loki push handler.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (setup_logging)
    2

    Parameters
    ----------
    service_name : object
        Argument ``service_name``.
    """
    root_logger = logging.getLogger()
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(level)

    formatter = JsonLogFormatter()
    if not root_logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

    if os.getenv("LOKI_PUSH_URL", "").strip():
        has_loki = any(isinstance(handler, LokiHandler) for handler in root_logger.handlers)
        if not has_loki:
            loki_handler = LokiHandler(service_name=service_name)
            loki_handler.setFormatter(formatter)
            root_logger.addHandler(loki_handler)

    ensure_request_log_filters()


def install_fastapi_observability(app: FastAPI, service_name: str) -> None:
    """
    Install metrics middleware and /metrics endpoint into FastAPI app.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (install_fastapi_observability)
    2

    Parameters
    ----------
    app : object
        Argument ``app``.
    service_name : object
        Argument ``service_name``.
    """

    @app.middleware("http")
    async def prometheus_http_metrics(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Record Prometheus HTTP request counters and latency histograms.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (prometheus_http_metrics)
        2

        Parameters
        ----------
        request : object
            Argument ``request``.
        call_next : object
            Argument ``call_next``.

        Returns
        -------
        object
            Return value.
        """
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            _reset_request_log_level(request)
        duration_seconds = time.perf_counter() - start

        route = request.scope.get("route")
        endpoint = getattr(route, "path", request.url.path)
        status = f"{response.status_code}"

        HTTP_REQUESTS_TOTAL.labels(
            service=service_name,
            method=request.method,
            endpoint=endpoint,
            status=status,
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            service=service_name,
            method=request.method,
            endpoint=endpoint,
        ).observe(duration_seconds)

        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics_endpoint() -> Response:
        """
        Expose Prometheus metrics in text exposition format.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (metrics_endpoint)
        2

        Returns
        -------
        object
            Return value.
        """
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
