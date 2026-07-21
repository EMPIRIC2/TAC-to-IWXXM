"""Unit tests for dissemination redaction and rate limit helpers (T2.3 support)."""

from __future__ import annotations

import pytest

from dissemination.rate_limit import DisseminationRateLimiter, RateLimitExceeded
from dissemination.redact import redact_secrets, redact_uri


def test_redact_uri_password() -> None:
    uri = "postgresql://alice:s3cret@db.example.com:5432/wx"
    out = redact_uri(uri)
    assert "s3cret" not in out
    assert "***" in out
    assert "alice" in out
    assert "db.example.com" in out


def test_redact_secrets_json_password_field() -> None:
    raw = '{"password": "hunter2", "host": "x"}'
    out = redact_secrets(raw)
    assert "hunter2" not in out
    assert "***" in out


def test_rate_limiter_allows_then_denies() -> None:
    lim = DisseminationRateLimiter(max_per_minute=2)
    lim.check("u1", now=1000.0)
    lim.check("u1", now=1001.0)
    with pytest.raises(RateLimitExceeded):
        lim.check("u1", now=1002.0)
    # Different user unaffected
    lim.check("u2", now=1002.0)


def test_rate_limiter_env_and_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISSEMINATION_RATE_LIMIT_PER_MIN", "5")
    lim = DisseminationRateLimiter()
    assert lim.max_per_minute == 5
    lim.check("u", now=1.0)
    lim.reset("u")
    lim.check("u", now=1.0)
    lim.reset()
