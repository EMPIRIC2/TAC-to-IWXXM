"""Observability helpers for metrics and structured logging."""

from __future__ import annotations

import contextvars
import json
import logging
import os
import queue
import re
import threading
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

if TYPE_CHECKING:
    from .profile_wire import WireProfileSelection

# Module-level registry avoids relying on prometheus_client's private internals
# while still preventing duplicate-registration errors on module reload.
_METRICS: dict[str, Any] = {}


def _get_or_create_counter(name: str, documentation: str, labelnames: list[str]) -> Counter:
    if name not in _METRICS:
        try:
            _METRICS[name] = Counter(name, documentation, labelnames)
        except ValueError:
            # Metric already registered globally; retrieve from default REGISTRY
            from prometheus_client import REGISTRY

            _METRICS[name] = REGISTRY._names_to_collectors.get(name)
    return _METRICS[name]  # type: ignore[return-value]


def _get_or_create_histogram(name: str, documentation: str, labelnames: list[str]) -> Histogram:
    if name not in _METRICS:
        try:
            _METRICS[name] = Histogram(name, documentation, labelnames)
        except ValueError:
            # Metric already registered globally; retrieve from default REGISTRY
            from prometheus_client import REGISTRY

            _METRICS[name] = REGISTRY._names_to_collectors.get(name)
    return _METRICS[name]  # type: ignore[return-value]


HTTP_REQUESTS_TOTAL = _get_or_create_counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = _get_or_create_histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "endpoint"],
)

METAR_CONVERSIONS_TOTAL = _get_or_create_counter(
    "metar_conversions_total",
    "Total METAR conversions by status",
    ["status", "iwxxm_version", "icao_region"],
)

METAR_CONVERSION_DURATION_SECONDS = _get_or_create_histogram(
    "metar_conversion_duration_seconds",
    "METAR conversion duration in seconds",
    ["status", "iwxxm_version", "icao_region"],
)

TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL = _get_or_create_counter(
    "tac_semantic_profile_requests_total",
    "Profile wire requests by canonical semantic profile id (F35 / EV-063)",
    ["route", "semantic_profile"],
)

TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL = _get_or_create_counter(
    "tac_exchange_profile_requests_total",
    "Profile wire requests with an explicit exchange profile id (F35 / EV-063)",
    ["route", "exchange_profile"],
)

TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL = _get_or_create_counter(
    "tac_semantic_profile_alias_requests_total",
    "Profile wire requests that used a deprecated semantic profile alias (F35 / EV-063)",
    ["route", "semantic_profile"],
)


class JsonLogFormatter(logging.Formatter):
    """Formats log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": getattr(record, "service", os.getenv("SERVICE_NAME", "backend")),
            "environment": os.getenv("OBSERVABILITY_ENV", "unknown"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class LokiHandler(logging.Handler):
    """Pushes logs to Loki using HTTP API."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name
        self.push_url = os.getenv("LOKI_PUSH_URL", "").strip()
        self.username = os.getenv("LOKI_USERNAME", "").strip()
        self.password = os.getenv("LOKI_PASSWORD", "").strip()
        self.environment = os.getenv("OBSERVABILITY_ENV", "unknown")
        self.timeout = float(os.getenv("LOKI_TIMEOUT_SECONDS", "2.5"))
        self.batch_size = max(int(os.getenv("LOKI_BATCH_SIZE", "50")), 1)
        self.flush_interval = max(float(os.getenv("LOKI_FLUSH_INTERVAL_SECONDS", "1.0")), 0.1)
        self.queue_maxsize = max(int(os.getenv("LOKI_QUEUE_MAXSIZE", "1000")), 1)

        min_level_name = os.getenv("LOKI_MIN_LEVEL", "").upper().strip()
        self.min_level = getattr(logging, min_level_name, logging.NOTSET) if min_level_name else logging.NOTSET

        self._requests = None
        self._session = None
        if self.push_url:
            try:
                import requests as _requests  # type: ignore[import-untyped]

                self._requests = _requests
                self._session = _requests.Session()
            except Exception:
                self.push_url = ""

        self._queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=self.queue_maxsize)
        self._stop_event = threading.Event()
        self._worker = threading.Thread(
            target=self._worker_loop,
            name=f"LokiHandlerWorker-{service_name}",
            daemon=True,
        )
        self._worker.start()

    def emit(self, record: logging.LogRecord) -> None:
        if not self.push_url or self._session is None:
            return
        if self.min_level and record.levelno < self.min_level:
            return

        try:
            entry = self._build_loki_entry(record)
            self._queue.put_nowait(entry)
        except queue.Full:
            return
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        try:
            self._stop_event.set()
            if self._worker.is_alive():
                self._worker.join(timeout=self.timeout + self.flush_interval)
            if self._session is not None:
                self._session.close()
        finally:
            super().close()

    def _worker_loop(self) -> None:
        if not self.push_url or self._session is None:
            return

        batch: list[dict[str, Any]] = []
        last_flush = time.monotonic()

        while not self._stop_event.is_set():
            remaining = max(self.flush_interval - (time.monotonic() - last_flush), 0.0)
            try:
                item = self._queue.get(timeout=remaining)
                batch.append(item)
                self._queue.task_done()
            except queue.Empty:
                pass

            now = time.monotonic()
            should_flush = bool(
                batch
                and (
                    len(batch) >= self.batch_size
                    or (now - last_flush) >= self.flush_interval
                    or self._stop_event.is_set()
                )
            )
            if should_flush:
                try:
                    self._send_batch(batch)
                except Exception:
                    pass
                finally:
                    batch.clear()
                    last_flush = now

        while not self._queue.empty():
            try:
                batch.append(self._queue.get_nowait())
                self._queue.task_done()
            except queue.Empty:
                break

            if len(batch) >= self.batch_size:
                try:
                    self._send_batch(batch)
                except Exception:
                    pass
                finally:
                    batch.clear()

        if batch:
            try:
                self._send_batch(batch)
            except Exception:
                pass

    def _build_loki_entry(self, record: logging.LogRecord) -> dict[str, Any]:
        ts_ns = str(int(record.created * 1_000_000_000))
        line = self.format(record)
        labels = {
            "service": getattr(record, "service", self.service_name),
            "environment": self.environment,
            "level": record.levelname.lower(),
            "logger": record.name,
        }
        return {"timestamp": ts_ns, "line": line, "labels": labels}

    def _send_batch(self, batch: list[dict[str, Any]]) -> None:
        if not batch or self._session is None:
            return

        streams_map: dict[tuple[tuple[str, str], ...], list[list[str]]] = defaultdict(list)
        for entry in batch:
            labels = entry["labels"]
            key = tuple(sorted(labels.items()))
            streams_map[key].append([entry["timestamp"], entry["line"]])

        streams = [
            {
                "stream": dict(label_items),
                "values": values,
            }
            for label_items, values in streams_map.items()
        ]
        payload = {"streams": streams}

        auth = (self.username, self.password) if self.username and self.password else None
        response = self._session.post(
            self.push_url,
            json=payload,
            timeout=self.timeout,
            auth=auth,
        )
        response.raise_for_status()


def setup_logging(service_name: str) -> None:
    """Configure JSON logs and optional Loki push handler."""
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


def _metric_profile_id(profile_id: str) -> str:
    """Normalize a profile id for Prometheus labels (uppercase, no PII)."""
    return (profile_id or "unknown").strip().upper().replace("-", "_") or "unknown"


def record_profile_wire_metrics(route: str, wire: WireProfileSelection) -> None:
    """
    Record semantic/exchange profile id counters for a resolved wire selection.

    Parameters
    ----------
    route :
        FastAPI route path (e.g. ``/api/v1/convert``).
    wire :
        ``WireProfileSelection`` from ``profile_wire.resolve_route_profiles``.
    """
    safe_route = (route or "unknown").strip() or "unknown"
    semantic_id = _metric_profile_id(getattr(wire, "semantic_canonical", ""))

    TAC_SEMANTIC_PROFILE_REQUESTS_TOTAL.labels(
        route=safe_route,
        semantic_profile=semantic_id,
    ).inc()

    if getattr(wire, "deprecated_alias_used", False):
        TAC_SEMANTIC_PROFILE_ALIAS_REQUESTS_TOTAL.labels(
            route=safe_route,
            semantic_profile=semantic_id,
        ).inc()

    exchange = getattr(wire, "exchange_profile", None)
    if exchange:
        TAC_EXCHANGE_PROFILE_REQUESTS_TOTAL.labels(
            route=safe_route,
            exchange_profile=_metric_profile_id(exchange),
        ).inc()


def record_translation_metric(
    status: str,
    iwxxm_version: str,
    icao_region: str,
    duration_ms: int,
) -> None:
    """Record translation status and latency metrics."""
    safe_status = status or "unknown"
    safe_version = iwxxm_version or "unknown"
    safe_region = icao_region or "unknown"

    METAR_CONVERSIONS_TOTAL.labels(
        status=safe_status,
        iwxxm_version=safe_version,
        icao_region=safe_region,
    ).inc()

    METAR_CONVERSION_DURATION_SECONDS.labels(
        status=safe_status,
        iwxxm_version=safe_version,
        icao_region=safe_region,
    ).observe(max(duration_ms, 0) / 1000.0)


def install_fastapi_observability(app: FastAPI, service_name: str) -> None:
    """Install metrics middleware and /metrics endpoint into FastAPI app."""

    @app.middleware("http")
    async def prometheus_http_metrics(request: Request, call_next):
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
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)


_REQUEST_LOG_LEVEL: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "convert_request_log_level",
    default=None,
)
_ALLOWED_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
_AUTH_RE = re.compile(r"(?i)(authorization\s*[:=]\s*)(\S+)")
_FILTERS_INSTALLED = False


class RequestLogLevelFilter(logging.Filter):
    """Drop records below the per-request convert ``log_level`` ContextVar."""

    def filter(self, record: logging.LogRecord) -> bool:
        minimum = _REQUEST_LOG_LEVEL.get()
        if minimum is None:
            return True
        return record.levelno >= minimum


class SecretRedactFilter(logging.Filter):
    """Strip JWTs and Authorization header values from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
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
    """Attach request-level and secret filters once (safe for tests)."""
    global _FILTERS_INSTALLED
    if _FILTERS_INSTALLED:
        return
    level_filter = RequestLogLevelFilter()
    redact_filter = SecretRedactFilter()
    names = ("", "src", "src.api", "tac2iwxxm", "tac_validate", "iwxxm_validate")
    for name in names:
        target = logging.getLogger(name)
        target.addFilter(level_filter)
        target.addFilter(redact_filter)
    _FILTERS_INSTALLED = True


_REQUEST_LOGGERS = ("src", "src.api", "tac2iwxxm", "tac_validate", "iwxxm_validate")


def set_request_log_level(request: Request, level_name: str | None) -> str:
    """Apply convert ``log_level`` to this request's log ContextVar.

    Returns
    -------
    str
        Normalized level name (DEBUG/INFO/WARNING/ERROR/CRITICAL).
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
    token = getattr(request.state, "convert_log_level_token", None)
    if token is not None:
        try:
            _REQUEST_LOG_LEVEL.reset(token)
        except ValueError:
            # Starlette BaseHTTPMiddleware runs the route in a different Context
            # than dispatch(); Token.reset is invalid across contexts.
            pass
        request.state.convert_log_level_token = None
    previous = getattr(request.state, "convert_log_level_prev", None)
    if previous:
        for target, prior in previous:
            target.setLevel(prior)
        request.state.convert_log_level_prev = None
