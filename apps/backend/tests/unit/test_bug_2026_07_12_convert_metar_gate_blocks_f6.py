"""Repro: /convert METAR-only TAC validation blocks F6 non-METAR products (PR #710).

Bug: docs/bug-reports/BUG-2026-07-12-convert-metar-gate-blocks-f6.md
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

TAF_TAC = "TAF KJFK 121730Z 1218/1324 24012KT P6SM SCT040 BKN080"


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_convert_taf_product_not_blocked_by_metar_keyword_gate(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """product=TAF must reach convert_metar_tac_with_metadata (not VALIDATION_FAILED)."""
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append({"tac": tac, **kwargs})
        return "<iwxxm:TAF xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, TAF_TAC),
            "product": (None, "TAF"),
            "profile": (None, "annex3"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert "VALIDATION_FAILED" not in response.text
    assert "Missing METAR/SPECI" not in response.text
    assert len(seen) >= 1
    assert seen[0].get("product") == "TAF"
