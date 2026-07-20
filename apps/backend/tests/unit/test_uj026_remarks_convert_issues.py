"""EV-013 / UJ-026 — convert API echoes REMARKS_EXCLUDED / retains iwxxm_us free text."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token


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
