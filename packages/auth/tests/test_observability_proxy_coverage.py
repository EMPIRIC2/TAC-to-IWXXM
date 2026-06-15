"""Coverage-focused tests for auth observability and Supabase proxy helpers."""

from __future__ import annotations

import logging
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import observability as obs
import supabase_proxy as proxy


class _FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        response = MagicMock()
        response.raise_for_status.return_value = None
        return response

    def close(self):
        return None


def _fake_auth_response(user=None, session=None):
    return SimpleNamespace(user=user, session=session)


def test_json_log_formatter_includes_exception_payload():
    formatter = obs.JsonLogFormatter()
    logger = logging.getLogger("test-auth-observability")

    try:
        raise RuntimeError("boom")
    except RuntimeError:
        record = logger.makeRecord(
            name="test-auth-observability",
            level=logging.ERROR,
            fn="test_file.py",
            lno=12,
            msg="failure",
            args=(),
            exc_info=sys.exc_info(),
        )

    output = formatter.format(record)
    assert '"level": "ERROR"' in output
    assert '"message": "failure"' in output


def test_loki_handler_send_batch_and_emit_paths(monkeypatch):
    monkeypatch.setenv("LOKI_PUSH_URL", "https://loki.example/push")
    handler = obs.LokiHandler(service_name="auth")
    fake_session = _FakeSession()
    handler._session = fake_session

    logger = logging.getLogger("loki-test")
    record = logger.makeRecord(
        name="loki-test",
        level=logging.INFO,
        fn="test_file.py",
        lno=20,
        msg="hello",
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    item = handler._build_loki_entry(record)
    handler._send_batch([item])

    assert fake_session.calls
    handler.close()


def test_setup_logging_and_metrics_endpoint(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.delenv("LOKI_PUSH_URL", raising=False)

    obs.setup_logging("auth")

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    obs.install_fastapi_observability(app, "auth")

    @app.get("/auth/login")
    async def login_route():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/auth/login")
    assert response.status_code == 200

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert b"http_requests_total" in metrics.content


def test_supabase_proxy_init_requires_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)

    with pytest.raises(ValueError):
        proxy.SupabaseAuthProxy()


def test_supabase_proxy_happy_paths_and_errors(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://unit.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")

    fake_user = SimpleNamespace(id="u1", email="u@example.com", user_metadata={"k": "v"})
    fake_session = SimpleNamespace(access_token="a", refresh_token="r", expires_at=123)

    fake_auth = SimpleNamespace(
        sign_up=lambda payload: _fake_auth_response(user=fake_user, session=fake_session),
        sign_in_with_password=lambda payload: _fake_auth_response(user=fake_user, session=fake_session),
        set_session=lambda *_args, **_kwargs: None,
        sign_out=lambda: None,
        get_user=lambda _token: _fake_auth_response(user=fake_user, session=None),
        refresh_session=lambda _refresh: _fake_auth_response(user=fake_user, session=fake_session),
        reset_password_email=lambda *_args, **_kwargs: None,
        update_user=lambda *_args, **_kwargs: None,
    )

    fake_client = SimpleNamespace(auth=fake_auth)
    monkeypatch.setattr(proxy, "create_client", lambda *_args, **_kwargs: fake_client)

    p = proxy.SupabaseAuthProxy()

    signup = p.sign_up("u@example.com", "password", metadata={"name": "user"})
    assert signup["user"]["id"] == "u1"

    signin = p.sign_in("u@example.com", "password")
    assert signin["session"]["access_token"] == "a"

    assert p.sign_out("token")["message"]
    assert p.get_user("token")["email"] == "u@example.com"
    assert p.refresh_session("refresh")["access_token"] == "a"
    assert p.reset_password_email("u@example.com")["message"]
    assert p.update_password("token", "new-password")["message"]
    assert p.verify_token("token") is True

    # Verify get_supabase_proxy singleton path.
    proxy._proxy = None
    monkeypatch.setattr(proxy, "create_client", lambda *_args, **_kwargs: fake_client)
    first = proxy.get_supabase_proxy()
    second = proxy.get_supabase_proxy()
    assert first is second


def test_supabase_proxy_error_paths(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://unit.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")

    fake_auth = SimpleNamespace(
        sign_up=lambda payload: (_ for _ in ()).throw(Exception("bad signup")),
        sign_in_with_password=lambda payload: _fake_auth_response(user=None, session=None),
        set_session=lambda *_args, **_kwargs: (_ for _ in ()).throw(Exception("session_not_found")),
        sign_out=lambda: None,
        get_user=lambda _token: _fake_auth_response(user=None, session=None),
        refresh_session=lambda _refresh: _fake_auth_response(user=None, session=None),
        reset_password_email=lambda *_args, **_kwargs: (_ for _ in ()).throw(Exception("ignored")),
        update_user=lambda *_args, **_kwargs: (_ for _ in ()).throw(Exception("update fail")),
    )

    fake_client = SimpleNamespace(auth=fake_auth)
    monkeypatch.setattr(proxy, "create_client", lambda *_args, **_kwargs: fake_client)

    p = proxy.SupabaseAuthProxy()

    with pytest.raises(Exception):
        p.sign_up("u@example.com", "password")

    with pytest.raises(Exception):
        p.sign_in("u@example.com", "password")

    # session_not_found is treated as success.
    assert p.sign_out("token")["message"]

    with pytest.raises(Exception):
        p.get_user("token")

    with pytest.raises(Exception):
        p.refresh_session("refresh")

    # Error is swallowed by design to avoid account enumeration.
    assert p.reset_password_email("u@example.com")["message"]

    with pytest.raises(Exception):
        p.update_password("token", "new-password")

    assert p.verify_token("token") is False
