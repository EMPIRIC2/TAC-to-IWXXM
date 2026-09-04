"""Unit tests for overlay HMAC helpers (TC-EV933-003)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException
from src.services import profile_overlay as ov


def test_secret_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROFILE_OVERLAY_HMAC_SECRET", raising=False)
    with pytest.raises(HTTPException) as exc:
        ov.overlay_hmac_secret()
    assert exc.value.status_code == 503


def test_sign_and_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "test-secret")
    user_id = uuid4()
    body = {"lint": {"severity": "warning"}}
    sig = ov.sign_overlay(user_id=user_id, base_profile_id="ICAO_2025", body=body)
    assert len(sig) == 64
    ov.verify_overlay_signature(user_id=user_id, base_profile_id="ICAO_2025", body=body, signature=sig)


def test_verify_rejects_tamper_and_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROFILE_OVERLAY_HMAC_SECRET", "test-secret")
    user_id = uuid4()
    body = {"a": 1}
    with pytest.raises(HTTPException) as exc:
        ov.verify_overlay_signature(user_id=user_id, base_profile_id="ICAO_2025", body=body, signature="")
    assert exc.value.status_code == 400
    with pytest.raises(HTTPException) as exc2:
        ov.verify_overlay_signature(
            user_id=user_id,
            base_profile_id="ICAO_2025",
            body=body,
            signature="0" * 64,
        )
    assert exc2.value.status_code == 400


def test_canonical_sorts_keys() -> None:
    assert ov.canonical_overlay_body({"b": 1, "a": 2}) == '{"a":2,"b":1}'
