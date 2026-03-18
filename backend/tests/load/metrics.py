"""Prometheus metrics instrumentation for Locust runs."""

from __future__ import annotations

import os
from threading import Lock

from locust import events
from prometheus_client import Counter, Histogram, start_http_server

REQUEST_LATENCY_MS = Histogram(
    "locust_request_latency_ms",
    "Request latency in milliseconds",
    ["profile", "auth_mode", "scenario", "endpoint", "method"],
)

REQUEST_TOTAL = Counter(
    "locust_requests_total",
    "Total requests emitted by Locust",
    ["profile", "auth_mode", "scenario", "endpoint", "method", "status_class"],
)

REQUEST_FAILURES = Counter(
    "locust_request_failures_total",
    "Total failed requests emitted by Locust",
    ["profile", "auth_mode", "scenario", "endpoint", "method", "error_type"],
)

_METRICS_SERVER_STARTED = False
_METRICS_SERVER_LOCK = Lock()


def _status_class(status_code: int | None) -> str:
    if status_code is None:
        return "none"
    return f"{status_code // 100}xx"


def _should_enable_metrics_server() -> bool:
    return os.getenv("LOCUST_PROMETHEUS_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Start Prometheus scrape endpoint once per Locust process."""
    del environment, kwargs

    if not _should_enable_metrics_server():
        return

    global _METRICS_SERVER_STARTED
    with _METRICS_SERVER_LOCK:
        if _METRICS_SERVER_STARTED:
            return

        port = int(os.getenv("LOCUST_PROMETHEUS_PORT", "9646"))
        start_http_server(port)
        _METRICS_SERVER_STARTED = True


@events.request.add_listener
def on_locust_request(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    start_time,
    url,
    **kwargs,
):
    """Map Locust request events to Prometheus counters/histograms."""
    del response_length, start_time, url, kwargs

    request_context = context or {}
    profile = request_context.get("profile", "unknown")
    auth_mode = request_context.get("auth_mode", "unknown")
    scenario = request_context.get("scenario", "unknown")
    endpoint = request_context.get("endpoint", name)

    status_code = None
    if response is not None:
        status_code = getattr(response, "status_code", None)

    method = request_type.upper() if request_type else "UNKNOWN"
    status = _status_class(status_code)

    REQUEST_LATENCY_MS.labels(
        profile=profile,
        auth_mode=auth_mode,
        scenario=scenario,
        endpoint=endpoint,
        method=method,
    ).observe(response_time)

    REQUEST_TOTAL.labels(
        profile=profile,
        auth_mode=auth_mode,
        scenario=scenario,
        endpoint=endpoint,
        method=method,
        status_class=status,
    ).inc()

    if exception is not None:
        REQUEST_FAILURES.labels(
            profile=profile,
            auth_mode=auth_mode,
            scenario=scenario,
            endpoint=endpoint,
            method=method,
            error_type=type(exception).__name__,
        ).inc()
