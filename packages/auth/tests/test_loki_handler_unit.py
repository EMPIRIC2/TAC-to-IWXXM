"""Unit tests for LokiHandler in auth observability.py – 0% coverage target."""

import logging
import os
import queue
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from auth.observability import JsonLogFormatter, LokiHandler


class TestJsonLogFormatter:
    def test_format_produces_json(self):
        formatter = JsonLogFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="hello world", args=(), exc_info=None
        )
        import json

        output = json.loads(formatter.format(record))
        assert output["level"] == "INFO"
        assert output["message"] == "hello world"
        assert "timestamp" in output
        assert "service" in output

    def test_format_includes_exception_info(self):
        formatter = JsonLogFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0, msg="error occurred", args=(), exc_info=exc_info
        )
        import json

        output = json.loads(formatter.format(record))
        assert "exception" in output


class TestLokiHandlerInitNoPushUrl:
    def test_init_without_push_url(self):
        """When LOKI_PUSH_URL is not set, handler should be inert."""
        with patch.dict(os.environ, {"LOKI_PUSH_URL": ""}, clear=False):
            handler = LokiHandler(service_name="test-svc")
        assert handler.push_url == ""
        assert handler._session is None
        assert handler._requests is None
        handler.close()

    def test_init_defaults(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": ""}, clear=False):
            handler = LokiHandler(service_name="test")
        assert handler.service_name == "test"
        assert handler.batch_size >= 1
        assert handler.flush_interval >= 0.1
        handler.close()

    def test_emit_noop_when_no_push_url(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": ""}, clear=False):
            handler = LokiHandler(service_name="test")
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="test", args=(), exc_info=None
        )
        # Should not raise and should be a no-op
        handler.emit(record)
        handler.close()

    def test_close_stops_worker_thread(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": ""}, clear=False):
            handler = LokiHandler(service_name="test")
        worker = handler._worker
        handler.close()
        worker.join(timeout=3.0)
        assert not worker.is_alive()


class TestLokiHandlerEnvConfig:
    def test_batch_size_env(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": "", "LOKI_BATCH_SIZE": "25"}, clear=False):
            handler = LokiHandler(service_name="test")
        assert handler.batch_size == 25
        handler.close()

    def test_flush_interval_env(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": "", "LOKI_FLUSH_INTERVAL_SECONDS": "0.5"}, clear=False):
            handler = LokiHandler(service_name="test")
        assert handler.flush_interval == 0.5
        handler.close()

    def test_min_level_env(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": "", "LOKI_MIN_LEVEL": "WARNING"}, clear=False):
            handler = LokiHandler(service_name="test")
        assert handler.min_level == logging.WARNING
        handler.close()

    def test_invalid_batch_size_clamped_to_1(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": "", "LOKI_BATCH_SIZE": "0"}, clear=False):
            handler = LokiHandler(service_name="test")
        assert handler.batch_size == 1
        handler.close()

    def test_invalid_flush_interval_clamped(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": "", "LOKI_FLUSH_INTERVAL_SECONDS": "0.0"}, clear=False):
            handler = LokiHandler(service_name="test")
        assert handler.flush_interval >= 0.1
        handler.close()


class TestLokiHandlerBuildEntry:
    def test_build_loki_entry_structure(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": ""}, clear=False):
            handler = LokiHandler(service_name="test-svc")
        record = logging.LogRecord(
            name="mylogger", level=logging.INFO, pathname="", lineno=0, msg="test message", args=(), exc_info=None
        )
        entry = handler._build_loki_entry(record)
        assert "timestamp" in entry
        assert "line" in entry
        assert "labels" in entry
        assert entry["labels"]["service"] == "test-svc"
        assert entry["labels"]["level"] == "info"
        handler.close()


class TestLokiHandlerEmitMinLevel:
    def test_emit_skips_below_min_level(self):
        with patch.dict(os.environ, {"LOKI_PUSH_URL": "http://loki:3100", "LOKI_MIN_LEVEL": "ERROR"}, clear=False):
            mock_requests = MagicMock()
            mock_session = MagicMock()
            mock_requests.Session.return_value = mock_session
            with patch.dict("sys.modules", {"requests": mock_requests}):
                import importlib
                import observability as obs_mod

                importlib.reload(obs_mod)
                handler = obs_mod.LokiHandler(service_name="test")
                # Patch session and push_url for test
                handler._session = mock_session
                handler.push_url = "http://loki:3100"
                handler.min_level = logging.ERROR

                info_record = logging.LogRecord(
                    name="test", level=logging.INFO, pathname="", lineno=0, msg="info msg", args=(), exc_info=None
                )
                # INFO < ERROR → should be skipped
                original_qsize = handler._queue.qsize()
                handler.emit(info_record)
                assert handler._queue.qsize() == original_qsize
                handler.close()
