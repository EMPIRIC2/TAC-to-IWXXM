"""Unit tests for observability and webhook services with mocked dependencies."""

from __future__ import annotations

import logging
import sys
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.services import webhooks as webhooks_module
from src.services.webhooks import WebhookService
from src.utilities import observability as observability_module
from src.utilities.observability import JsonLogFormatter, LokiHandler


class _FakeCounter:
    def __init__(self):
        self.inc_calls = 0

    def inc(self):
        self.inc_calls += 1


class _FakeHistogram:
    def __init__(self):
        self.observations = []

    def observe(self, value):
        self.observations.append(value)


class _FakeMetric:
    def __init__(self, child):
        self.child = child
        self.labels_calls = []

    def labels(self, **kwargs):
        self.labels_calls.append(kwargs)
        return self.child


def test_json_log_formatter_includes_exception_text():
    formatter = JsonLogFormatter()
    logger = logging.getLogger("test-json")

    try:
        raise ValueError("boom")
    except ValueError:
        record = logger.makeRecord(
            name="test-json",
            level=logging.ERROR,
            fn="test_file.py",
            lno=10,
            msg="failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    output = formatter.format(record)
    assert '"level": "ERROR"' in output
    assert '"message": "failed"' in output
    assert '"exception"' in output


def test_loki_emit_skips_when_push_url_missing(monkeypatch):
    monkeypatch.delenv("LOKI_PUSH_URL", raising=False)
    handler = LokiHandler(service_name="backend")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    assert handler._queue.qsize() == 0
    handler.close()


def test_loki_send_batch_groups_and_posts(monkeypatch):
    handler = LokiHandler(service_name="backend")
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    handler._session = mock_session
    handler.push_url = "https://loki.example/push"
    handler.username = "user"
    handler.password = "pass"

    batch = [
        {
            "timestamp": "1",
            "line": "a",
            "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
        },
        {
            "timestamp": "2",
            "line": "b",
            "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
        },
    ]

    handler._send_batch(batch)

    assert mock_session.post.call_count == 1
    kwargs = mock_session.post.call_args.kwargs
    assert kwargs["auth"] == ("user", "pass")
    assert "streams" in kwargs["json"]
    handler.close()


def test_record_translation_metric_uses_safe_defaults(monkeypatch):
    fake_counter_child = _FakeCounter()
    fake_hist_child = _FakeHistogram()
    fake_counter = _FakeMetric(fake_counter_child)
    fake_hist = _FakeMetric(fake_hist_child)

    monkeypatch.setattr(observability_module, "METAR_CONVERSIONS_TOTAL", fake_counter)
    monkeypatch.setattr(observability_module, "METAR_CONVERSION_DURATION_SECONDS", fake_hist)

    observability_module.record_translation_metric("", "", "", -50)

    assert fake_counter.labels_calls[0]["status"] == "unknown"
    assert fake_hist.labels_calls[0]["iwxxm_version"] == "unknown"
    assert fake_hist_child.observations[0] == 0.0


@pytest.mark.asyncio
async def test_send_webhook_disabled_returns_true(monkeypatch):
    service = WebhookService()
    service.enabled = False

    result = await service.send_webhook("translation.success", {"k": "v"})
    assert result is True


@pytest.mark.asyncio
async def test_webhook_service_context_manager_creates_and_closes_client(monkeypatch):
    service = WebhookService()
    service.enabled = True
    fake_client = AsyncMock()
    monkeypatch.setattr(webhooks_module.httpx, "AsyncClient", lambda timeout=10.0: fake_client)

    async with service as active:
        assert active.client is fake_client

    fake_client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_webhook_service_context_manager_disabled_leaves_client_none():
    service = WebhookService()
    service.enabled = False

    async with service as active:
        assert active.client is None

    assert service.client is None


@pytest.mark.asyncio
async def test_send_webhook_no_urls_returns_false(monkeypatch):
    service = WebhookService()
    service.enabled = True
    monkeypatch.setattr(webhooks_module, "WEBHOOK_EVENTS", ["translation.success"])
    monkeypatch.setattr(webhooks_module, "WEBHOOK_URLS", [])

    result = await service.send_webhook("translation.success", {"k": "v"})
    assert result is False


@pytest.mark.asyncio
async def test_send_webhook_event_not_enabled_returns_true(monkeypatch):
    service = WebhookService()
    service.enabled = True
    monkeypatch.setattr(webhooks_module, "WEBHOOK_EVENTS", ["translation.completed"])

    result = await service.send_webhook("translation.success", {"k": "v"})
    assert result is True


@pytest.mark.asyncio
async def test_send_webhook_aggregate_result_false_when_one_fails(monkeypatch):
    service = WebhookService()
    service.enabled = True

    monkeypatch.setattr(webhooks_module, "WEBHOOK_EVENTS", ["translation.success"])
    monkeypatch.setattr(webhooks_module, "WEBHOOK_URLS", ["https://a", "https://b"])

    send_mock = AsyncMock(side_effect=[True, False])
    monkeypatch.setattr(service, "_send_single_webhook", send_mock)

    result = await service.send_webhook("translation.success", {"translation_id": "123"})
    assert result is False
    assert send_mock.await_count == 2


@pytest.mark.asyncio
async def test_send_single_webhook_handles_timeout(monkeypatch):
    service = WebhookService()
    service.client = AsyncMock()
    service.client.post.side_effect = httpx.TimeoutException("timeout")

    ok = await service._send_single_webhook(
        "https://example.test",
        "{}",
        {"Content-Type": "application/json"},
    )
    assert ok is False


@pytest.mark.asyncio
async def test_send_single_webhook_success_status(monkeypatch):
    service = WebhookService()
    response = MagicMock(status_code=202)
    service.client = AsyncMock()
    service.client.post.return_value = response

    ok = await service._send_single_webhook(
        "https://example.test",
        "{}",
        {"Content-Type": "application/json"},
    )
    assert ok is True


@pytest.mark.asyncio
async def test_notify_translation_success_calls_send_webhook(monkeypatch):
    service = WebhookService()
    send_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(service, "send_webhook", send_mock)

    await service.notify_translation_success(
        translation_id="tid",
        airport_code="KJFK",
        icao_region="NAM",
        iwxxm_version="2025-2",
        duration_ms=12,
    )

    assert send_mock.await_count == 1
    assert send_mock.await_args.kwargs["event"] == "translation.success"


def test_loki_emit_respects_min_level(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._session = MagicMock()
    handler.min_level = logging.WARNING

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="ignore me",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    assert handler._queue.qsize() == 0
    handler.close()


def test_loki_emit_queue_full_is_non_fatal(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._session = MagicMock()
    handler._queue = observability_module.queue.Queue(maxsize=1)
    handler._queue.put_nowait({"x": 1})

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="full queue",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    assert handler._queue.qsize() == 1
    handler.close()


def test_loki_build_entry_uses_handler_defaults_when_service_missing():
    handler = LokiHandler(service_name="backend")
    handler.environment = "test"
    record = logging.LogRecord(
        name="test.logger",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="entry",
        args=(),
        exc_info=None,
    )

    entry = handler._build_loki_entry(record)
    assert entry["labels"]["service"] == "backend"
    assert entry["labels"]["environment"] == "test"
    assert entry["labels"]["level"] == "error"
    handler.close()


def test_loki_send_batch_without_auth_groups_streams():
    handler = LokiHandler(service_name="backend")
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    handler._session = mock_session
    handler.push_url = "https://loki.example/push"
    handler.username = ""
    handler.password = ""

    batch = [
        {
            "timestamp": "1",
            "line": "a",
            "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
        },
        {
            "timestamp": "2",
            "line": "b",
            "labels": {"service": "backend", "environment": "test", "level": "error", "logger": "x"},
        },
    ]
    handler._send_batch(batch)

    kwargs = mock_session.post.call_args.kwargs
    assert kwargs["auth"] is None
    assert len(kwargs["json"]["streams"]) == 2
    handler.close()


def test_setup_logging_adds_stream_handler_when_none(monkeypatch):
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    root.handlers = []

    monkeypatch.delenv("LOKI_PUSH_URL", raising=False)
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    try:
        observability_module.setup_logging("backend")
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonLogFormatter)
    finally:
        for handler in list(root.handlers):
            handler.close()
        root.handlers = original_handlers
        root.setLevel(original_level)


def test_setup_logging_reformats_existing_handlers(monkeypatch):
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    existing = logging.StreamHandler()
    root.handlers = [existing]

    monkeypatch.delenv("LOKI_PUSH_URL", raising=False)

    try:
        observability_module.setup_logging("backend")
        assert isinstance(existing.formatter, JsonLogFormatter)
    finally:
        for handler in list(root.handlers):
            handler.close()
        root.handlers = original_handlers
        root.setLevel(original_level)


def test_setup_logging_adds_loki_only_once(monkeypatch):
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    root.handlers = []

    class _FakeLoki(logging.Handler):
        def __init__(self, service_name: str):
            super().__init__()
            self.service_name = service_name

    monkeypatch.setenv("LOKI_PUSH_URL", "https://loki.example/push")
    monkeypatch.setattr(observability_module, "LokiHandler", _FakeLoki)

    try:
        observability_module.setup_logging("backend")
        observability_module.setup_logging("backend")
        loki_handlers = [h for h in root.handlers if isinstance(h, _FakeLoki)]
        assert len(loki_handlers) == 1
    finally:
        for handler in list(root.handlers):
            handler.close()
        root.handlers = original_handlers
        root.setLevel(original_level)


def test_install_fastapi_observability_records_http_metrics(monkeypatch):
    fake_counter = _FakeMetric(_FakeCounter())
    fake_hist_child = _FakeHistogram()
    fake_hist = _FakeMetric(fake_hist_child)

    monkeypatch.setattr(observability_module, "HTTP_REQUESTS_TOTAL", fake_counter)
    monkeypatch.setattr(observability_module, "HTTP_REQUEST_DURATION_SECONDS", fake_hist)

    app = FastAPI()

    @app.get("/ping")
    async def _ping():
        return {"ok": True}

    observability_module.install_fastapi_observability(app, "backend")
    client = TestClient(app)

    response = client.get("/ping")
    assert response.status_code == 200
    assert fake_counter.labels_calls
    assert fake_counter.labels_calls[0]["service"] == "backend"
    assert fake_hist.labels_calls
    assert fake_hist_child.observations[0] >= 0


def test_install_fastapi_observability_exposes_metrics_endpoint():
    app = FastAPI()
    observability_module.install_fastapi_observability(app, "backend")
    client = TestClient(app)

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")


def test_loki_emit_skips_when_session_missing():
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._session = None

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    assert handler._queue.qsize() == 0
    handler.close()


def test_loki_handler_close_closes_session():
    handler = LokiHandler(service_name="backend")
    mock_session = MagicMock()
    handler._session = mock_session
    handler.push_url = "https://loki.example/push"

    handler.close()

    assert mock_session.close.call_count == 1


def test_loki_worker_loop_flushes_queue_on_stop_event():
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)

    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response
    handler._session = mock_session

    handler._queue.put_nowait(
        {
            "timestamp": "1",
            "line": "message",
            "labels": {
                "service": "backend",
                "environment": "test",
                "level": "info",
                "logger": "x",
            },
        }
    )
    handler._stop_event.set()
    handler._worker_loop()

    assert mock_session.post.call_count >= 1
    handler.close()


def test_generate_signature_empty_when_secret_missing(monkeypatch):
    service = WebhookService()
    monkeypatch.setattr(webhooks_module, "WEBHOOK_SECRET", "")

    assert service._generate_signature("{}") == ""


def test_generate_signature_returns_hex_with_secret(monkeypatch):
    service = WebhookService()
    monkeypatch.setattr(webhooks_module, "WEBHOOK_SECRET", "test-secret")

    signature = service._generate_signature("{}")
    assert len(signature) == 64


@pytest.mark.asyncio
async def test_send_webhook_adds_signature_header_when_secret_set(monkeypatch):
    service = WebhookService()
    service.enabled = True
    monkeypatch.setattr(webhooks_module, "WEBHOOK_EVENTS", ["translation.success"])
    monkeypatch.setattr(webhooks_module, "WEBHOOK_URLS", ["https://example.test"])
    monkeypatch.setattr(webhooks_module, "WEBHOOK_SECRET", "test-secret")

    captured = {}

    async def _capture(_url, _payload, headers):
        captured.update(headers)
        return True

    monkeypatch.setattr(service, "_send_single_webhook", _capture)

    result = await service.send_webhook("translation.success", {"k": "v"})
    assert result is True
    assert captured["X-Webhook-Signature"].startswith("sha256=")


@pytest.mark.asyncio
async def test_send_single_webhook_request_error_returns_false():
    service = WebhookService()
    service.client = AsyncMock()
    service.client.post.side_effect = httpx.RequestError("request failed")

    ok = await service._send_single_webhook(
        "https://example.test",
        "{}",
        {"Content-Type": "application/json"},
    )
    assert ok is False


@pytest.mark.asyncio
async def test_send_single_webhook_unexpected_error_returns_false():
    service = WebhookService()
    service.client = AsyncMock()
    service.client.post.side_effect = RuntimeError("boom")

    ok = await service._send_single_webhook(
        "https://example.test",
        "{}",
        {"Content-Type": "application/json"},
    )
    assert ok is False


@pytest.mark.asyncio
async def test_send_single_webhook_non_success_status_returns_false():
    service = WebhookService()
    response = MagicMock(status_code=500)
    service.client = AsyncMock()
    service.client.post.return_value = response

    ok = await service._send_single_webhook(
        "https://example.test",
        "{}",
        {"Content-Type": "application/json"},
    )
    assert ok is False


@pytest.mark.asyncio
async def test_send_single_webhook_lazy_init_creates_client(monkeypatch):
    service = WebhookService()
    service.client = None

    class _FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def post(self, *_args, **_kwargs):
            return MagicMock(status_code=200)

    monkeypatch.setattr(webhooks_module.httpx, "AsyncClient", _FakeClient)

    ok = await service._send_single_webhook(
        "https://example.test",
        "{}",
        {"Content-Type": "application/json"},
    )
    assert ok is True
    assert service.client is not None


@pytest.mark.asyncio
async def test_notify_translation_completed_calls_send_webhook(monkeypatch):
    service = WebhookService()
    send_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(service, "send_webhook", send_mock)

    await service.notify_translation_completed(
        translation_id="tid",
        airport_code="KJFK",
        iwxxm_version="2025-2",
        file_size_bytes=1024,
        duration_ms=20,
    )

    assert send_mock.await_args.kwargs["event"] == "translation.completed"


@pytest.mark.asyncio
async def test_notify_translation_failed_calls_send_webhook(monkeypatch):
    service = WebhookService()
    send_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(service, "send_webhook", send_mock)

    await service.notify_translation_failed(
        translation_id="tid",
        airport_code="KJFK",
        error_type="ParseError",
        error_message="bad tac",
    )

    assert send_mock.await_args.kwargs["event"] == "translation.failed"


@pytest.mark.asyncio
async def test_notify_validation_failed_calls_send_webhook(monkeypatch):
    service = WebhookService()
    send_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(service, "send_webhook", send_mock)

    await service.notify_validation_failed(
        translation_id="tid",
        airport_code="KJFK",
        failed_layers=["XML_SCHEMA"],
        error_details={"layer": "XML_SCHEMA"},
    )

    assert send_mock.await_args.kwargs["event"] == "validation.failed"


@pytest.mark.asyncio
async def test_notify_bulk_completed_calls_send_webhook(monkeypatch):
    service = WebhookService()
    send_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(service, "send_webhook", send_mock)

    await service.notify_bulk_completed(
        total_files=10,
        successful=9,
        failed=1,
        duration_ms=1000,
    )

    assert send_mock.await_args.kwargs["event"] == "bulk.completed"


def test_get_or_create_metric_helpers_reuse_existing_collectors(monkeypatch):
    from prometheus_client import REGISTRY

    fake_counter = object()
    fake_hist = object()
    monkeypatch.setitem(REGISTRY._names_to_collectors, "existing_counter", fake_counter)
    monkeypatch.setitem(REGISTRY._names_to_collectors, "existing_hist", fake_hist)

    assert observability_module._get_or_create_counter("existing_counter", "doc", ["x"]) is fake_counter
    assert observability_module._get_or_create_histogram("existing_hist", "doc", ["x"]) is fake_hist


def test_loki_handler_disables_push_when_requests_import_fails(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "requests":
            raise ImportError("requests unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setenv("LOKI_PUSH_URL", "https://loki.example/push")
    monkeypatch.setattr(builtins, "__import__", _fake_import)

    handler = LokiHandler(service_name="backend")
    assert handler.push_url == ""
    handler.close()


def test_loki_worker_loop_handles_queue_empty_branch(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()

    calls = {"count": 0}

    def _get(timeout=None):
        calls["count"] += 1
        handler._stop_event.set()
        raise observability_module.queue.Empty()

    monkeypatch.setattr(handler._queue, "get", _get)
    handler._worker_loop()

    assert calls["count"] >= 1
    handler.close()


def test_loki_worker_loop_drains_queue_in_chunks(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()

    handler.batch_size = 1
    sent_batches = []
    monkeypatch.setattr(handler, "_send_batch", lambda batch: sent_batches.append(list(batch)))

    handler._queue.put_nowait(
        {
            "timestamp": "1",
            "line": "a",
            "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
        }
    )
    handler._queue.put_nowait(
        {
            "timestamp": "2",
            "line": "b",
            "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
        }
    )
    handler._stop_event.set()
    handler._worker_loop()

    assert len(sent_batches) >= 2
    handler.close()


def test_get_or_create_counter_registers_new_metric(monkeypatch):
    observability_module._METRICS.clear()
    counter = observability_module._get_or_create_counter("unit_test_counter", "doc", ["label"])
    assert counter is observability_module._METRICS["unit_test_counter"]


def test_get_or_create_histogram_registers_new_metric(monkeypatch):
    observability_module._METRICS.clear()
    histogram = observability_module._get_or_create_histogram("unit_test_hist", "doc", ["label"])
    assert histogram is observability_module._METRICS["unit_test_hist"]


def test_loki_send_batch_noop_for_empty_batch():
    handler = LokiHandler(service_name="backend")
    handler._session = MagicMock()
    handler.push_url = "https://loki.example/push"

    handler._send_batch([])

    handler._session.post.assert_not_called()
    handler.close()


def test_loki_emit_handles_build_entry_failure(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._session = MagicMock()
    monkeypatch.setattr(handler, "_build_loki_entry", lambda _record: (_ for _ in ()).throw(RuntimeError("build fail")))

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="broken entry",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    assert handler._queue.qsize() == 0
    handler.close()


def test_loki_close_joins_alive_worker(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._session = MagicMock()
    handler._worker.is_alive = MagicMock(return_value=True)
    join_mock = MagicMock()
    handler._worker.join = join_mock

    handler.close()

    join_mock.assert_called_once()
    handler._session.close.assert_called_once()


def test_loki_worker_loop_flushes_on_batch_size(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    handler.batch_size = 1
    sent = []
    monkeypatch.setattr(handler, "_send_batch", lambda batch: sent.append(list(batch)))

    entry = {
        "timestamp": "1",
        "line": "a",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._queue.put_nowait({**entry, "timestamp": "2", "line": "b"})
    handler._stop_event.set()
    handler._worker_loop()

    assert len(sent) >= 1
    handler.close()


def test_loki_worker_loop_ignores_send_batch_errors(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    monkeypatch.setattr(handler, "_send_batch", lambda _batch: (_ for _ in ()).throw(RuntimeError("send fail")))

    handler._queue.put_nowait(
        {
            "timestamp": "1",
            "line": "a",
            "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
        }
    )
    handler._stop_event.set()
    handler._worker_loop()
    handler.close()


def test_get_or_create_counter_handles_duplicate_registration():
    from prometheus_client import REGISTRY, Counter

    observability_module._METRICS.clear()
    Counter("dup_counter_test", "doc", ["label"])
    counter = observability_module._get_or_create_counter("dup_counter_test", "doc", ["label"])
    assert counter is REGISTRY._names_to_collectors["dup_counter_test"]


def test_loki_worker_loop_flushes_batch_on_interval(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    handler.flush_interval = 0.01
    handler.batch_size = 100
    sent = []
    monkeypatch.setattr(handler, "_send_batch", lambda batch: sent.append(list(batch)))

    entry = {
        "timestamp": "1",
        "line": "a",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._stop_event.set()
    handler._worker_loop()

    assert sent
    handler.close()


def test_loki_handler_disables_push_on_session_init_exception(monkeypatch):
    import builtins

    real_import = builtins.__import__

    class _BrokenRequests:
        class Session:
            def __init__(self):
                raise RuntimeError("session init failed")

    def _fake_import(name, *args, **kwargs):
        if name == "requests":
            return _BrokenRequests
        return real_import(name, *args, **kwargs)

    monkeypatch.setenv("LOKI_PUSH_URL", "https://loki.example/push")
    monkeypatch.setattr(builtins, "__import__", _fake_import)

    handler = LokiHandler(service_name="backend")
    assert handler.push_url == ""
    handler.close()


def test_loki_worker_loop_flushes_remaining_batch_on_shutdown(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    sent = []
    monkeypatch.setattr(handler, "_send_batch", lambda batch: sent.append(list(batch)))

    entry = {
        "timestamp": "1",
        "line": "tail",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._stop_event.set()
    handler._worker_loop()

    assert sent
    handler.close()


def test_loki_worker_loop_drains_queue_in_batch_chunks(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    handler.batch_size = 1
    sent = []
    monkeypatch.setattr(handler, "_send_batch", lambda batch: sent.append(list(batch)))

    entry = {
        "timestamp": "1",
        "line": "a",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._queue.put_nowait({**entry, "timestamp": "2", "line": "b"})
    handler._stop_event.set()
    handler._worker_loop()

    assert len(sent) >= 2
    handler.close()


def test_get_or_create_histogram_handles_duplicate_registration():
    from prometheus_client import REGISTRY, Histogram

    observability_module._METRICS.clear()
    Histogram("dup_hist_test", "doc", ["label"])
    histogram = observability_module._get_or_create_histogram("dup_hist_test", "doc", ["label"])
    assert histogram is REGISTRY._names_to_collectors["dup_hist_test"]


def test_loki_worker_loop_processes_queue_item_before_stop(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    handler.batch_size = 100
    handler.flush_interval = 0.01
    sent = []
    monkeypatch.setattr(handler, "_send_batch", lambda batch: sent.append(list(batch)))

    entry = {
        "timestamp": "1",
        "line": "queued",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._stop_event.set()
    handler._worker_loop()

    assert sent
    handler.close()


def test_loki_worker_shutdown_drains_queue_in_batches_with_send_errors(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    handler.batch_size = 1
    calls = {"count": 0}

    def _fail_send(_batch):
        calls["count"] += 1
        raise RuntimeError("send failed")

    monkeypatch.setattr(handler, "_send_batch", _fail_send)

    entry = {
        "timestamp": "1",
        "line": "a",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._queue.put_nowait({**entry, "timestamp": "2", "line": "b"})
    handler._stop_event.set()
    handler._worker_loop()
    handler.close()

    assert calls["count"] >= 2


def test_loki_worker_loop_flushes_on_interval_with_send_error(monkeypatch):
    handler = LokiHandler(service_name="backend")
    handler.push_url = "https://loki.example/push"
    handler._worker.join(timeout=0.1)
    handler._session = MagicMock()
    handler.flush_interval = 0.001
    handler.batch_size = 100
    calls = {"count": 0}

    def _fail_send(_batch):
        calls["count"] += 1
        handler._stop_event.set()

    monkeypatch.setattr(handler, "_send_batch", _fail_send)

    entry = {
        "timestamp": "1",
        "line": "a",
        "labels": {"service": "backend", "environment": "test", "level": "info", "logger": "x"},
    }
    handler._queue.put_nowait(entry)
    handler._worker_loop()
    handler.close()

    assert calls["count"] >= 1
