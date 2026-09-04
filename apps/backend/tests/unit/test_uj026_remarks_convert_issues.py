"""EV-013 / UJ-026 - convert API echoes REMARKS_EXCLUDED / retains iwxxm_us free text."""

from __future__ import annotations

from enum import Enum

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.conversion import _normalize_issue_severity
from src.utilities.security import verify_supabase_token


class _Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _convert(client: TestClient, *, tac: str, profile: str) -> dict:
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, tac),
            "product": (None, "METAR"),
            "profile": (None, profile),
            "iwxxm_version": (None, "2025-2"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    return response.json()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("info", "info"),
        ("WARNING", "warning"),
        (_Severity.ERROR, "error"),
        ("Severity.WARNING", "warning"),
        (None, "info"),
        ("unknown", "info"),
    ],
)
def test_normalize_issue_severity(raw: object, expected: str) -> None:
    assert _normalize_issue_severity(raw) == expected


def test_annex3_convert_echoes_remarks_excluded(client: TestClient) -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2 SLP176="
    body = _convert(client, tac=tac, profile="annex3")
    codes = [i.get("code") for i in (body.get("issues") or [])]
    assert "REMARKS_EXCLUDED" in codes
    assert body.get("successful", 0) >= 1
    xml = (body.get("results") or [{}])[0].get("content") or ""
    assert "iwxxm-us:Addendum" not in xml


def test_iwxxm_us_convert_retains_human_readable_text(client: TestClient) -> None:
    tac = "METAR KJFK 231751Z 18012KT 10SM CLR 15/07 A3005 RMK AO2 WND DATA ESTMD="
    body = _convert(client, tac=tac, profile="iwxxm_us")
    codes = [i.get("code") for i in (body.get("issues") or [])]
    assert "REMARKS_EXCLUDED" not in codes
    xml = (body.get("results") or [{}])[0].get("content") or ""
    assert "iwxxm-us:humanReadableText" in xml
    assert "WND DATA ESTMD" in xml


def test_convert_absorbs_enum_like_and_warning_error_severities(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cover absorb_convert_issues severity branches (enum-style / warning / error)."""

    def _fake_convert(*_args, soft_preview_out=None, **_kwargs):
        if soft_preview_out is not None:
            soft_preview_out.clear()
            soft_preview_out["ok"] = True
            soft_preview_out["failed_spans"] = []
            soft_preview_out["convert_issues"] = [
                {
                    "severity": "Severity.ERROR",
                    "code": "FAKE_ERROR",
                    "message": "error-ish",
                },
                {
                    "severity": "warning",
                    "code": "FAKE_WARN",
                    "message": "warn-ish",
                },
                {
                    "severity": "info",
                    "code": "FAKE_INFO",
                    "message": "info-ish",
                },
            ]
        return ('<?xml version="1.0"?><iwxxm:METAR/>', None)

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _fake_convert)
    body = _convert(
        client,
        tac="METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        profile="annex3",
    )
    by_code = {i.get("code"): i.get("severity") for i in (body.get("issues") or [])}
    assert by_code.get("FAKE_ERROR") == "error"
    assert by_code.get("FAKE_WARN") == "warning"
    assert by_code.get("FAKE_INFO") == "info"
