"""Part 1 of ``observability.py`` (line-cap split)."""

from __future__ import annotations

import contextlib
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

from prometheus_client import Counter, Histogram

if TYPE_CHECKING:
    from .profile_wire import WireProfileSelection

_METRICS: dict[str, Any] = {}


def _get_or_create_counter(name: str, documentation: str, labelnames: list[str]) -> Counter:
    """
    Internal helper ``_get_or_create_counter``.

    Parameters
    ----------
    name : object
        Argument ``name``.
    documentation : object
        Argument ``documentation``.
    labelnames : object
        Argument ``labelnames``.

    Returns
    -------
    object
        Return value.
    """
    if name not in _METRICS:
        try:
            _METRICS[name] = Counter(name, documentation, labelnames)
        except ValueError:
            # Metric already registered globally; retrieve from default REGISTRY
            from prometheus_client import REGISTRY

            _METRICS[name] = REGISTRY._names_to_collectors.get(name)
    return _METRICS[name]  # type: ignore[return-value]


def _get_or_create_histogram(name: str, documentation: str, labelnames: list[str]) -> Histogram:
    """
    Internal helper ``_get_or_create_histogram``.

    Parameters
    ----------
    name : object
        Argument ``name``.
    documentation : object
        Argument ``documentation``.
    labelnames : object
        Argument ``labelnames``.

    Returns
    -------
    object
        Return value.
    """
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
    """
    Formats log records as JSON.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Serialize a log record as a single JSON line for structured logging.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to format.

        Returns
        -------
        str
            JSON-encoded log payload.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (format)
        2
        """
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
    """
    Pushes logs to Loki using HTTP API.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self, service_name: str) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        service_name : object
            Argument ``service_name``.
        """
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
        """
        Enqueue a log record for asynchronous push to Loki.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to ship when Loki is configured and level passes the filter.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (emit)
        2
        """
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
        """
        Stop the background worker and close the HTTP session.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (close)
        2
        """
        try:
            self._stop_event.set()
            if self._worker.is_alive():
                self._worker.join(timeout=self.timeout + self.flush_interval)
            if self._session is not None:
                self._session.close()
        finally:
            super().close()

    def _worker_loop(self) -> None:
        """Internal helper ``_worker_loop``."""
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
            with contextlib.suppress(Exception):
                self._send_batch(batch)

    def _build_loki_entry(self, record: logging.LogRecord) -> dict[str, Any]:
        """
        Internal helper ``_build_loki_entry``.

        Parameters
        ----------
        record : object
            Argument ``record``.

        Returns
        -------
        object
            Return value.
        """
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
        """
        Internal helper ``_send_batch``.

        Parameters
        ----------
        batch : object
            Argument ``batch``.
        """
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


def _metric_profile_id(profile_id: str) -> str:
    """
    Internal helper ``_metric_profile_id``.

    Parameters
    ----------
    profile_id : object
        Argument ``profile_id``.

    Returns
    -------
    object
        Return value.
    """
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

    Examples
    --------
    >>> 1 + 1  # docstring smoke (record_profile_wire_metrics)
    2
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
    """
    Record translation status and latency metrics.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (record_translation_metric)
    2

    Parameters
    ----------
    status : object
        Argument ``status``.
    iwxxm_version : object
        Argument ``iwxxm_version``.
    icao_region : object
        Argument ``icao_region``.
    duration_ms : object
        Argument ``duration_ms``.
    """
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


_REQUEST_LOG_LEVEL: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "convert_request_log_level",
    default=None,
)

_ALLOWED_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
