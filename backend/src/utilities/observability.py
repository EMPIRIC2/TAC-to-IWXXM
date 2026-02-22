"""Observability helpers for metrics and structured logging."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
import requests


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "endpoint"],
)

METAR_CONVERSIONS_TOTAL = Counter(
    "metar_conversions_total",
    "Total METAR conversions by status",
    ["status", "iwxxm_version", "icao_region"],
)

METAR_CONVERSION_DURATION_SECONDS = Histogram(
    "metar_conversion_duration_seconds",
    "METAR conversion duration in seconds",
    ["status", "iwxxm_version", "icao_region"],
)


class JsonLogFormatter(logging.Formatter):
    """Formats log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
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

    def emit(self, record: logging.LogRecord) -> None:
        if not self.push_url:
            return

        try:
            line = self.format(record)
            ts_ns = str(int(time.time() * 1_000_000_000))
            payload = {
                "streams": [
                    {
                        "stream": {
                            "service": self.service_name,
                            "level": record.levelname.lower(),
                            "environment": self.environment,
                        },
                        "values": [[ts_ns, line]],
                    }
                ]
            }
            auth: Optional[tuple[str, str]] = None
            if self.username and self.password:
                auth = (self.username, self.password)

            requests.post(
                self.push_url,
                json=payload,
                timeout=self.timeout,
                auth=auth,
            )
        except Exception:
            return


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
        response = await call_next(request)
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
