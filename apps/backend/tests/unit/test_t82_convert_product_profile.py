"""T8.2 / F6.e: POST /api/v1/convert forwards product + profile to tac2iwxxm.

Spec: docs/api-contract.md §Conversion; docs/feature-list.md F6.e.
"""

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


def test_convert_forwards_product_and_profile(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Multipart product/profile must reach convert_metar_tac_with_metadata."""
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append({"tac": tac, **kwargs})
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (
                None,
                "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=",
            ),
            "product": (None, "METAR"),
            "profile": (None, "iwxxm_us"),
            "iwxxm_version": (None, "2025-2"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:400]
    assert len(seen) >= 1
    assert seen[0].get("product") == "METAR"
    assert seen[0].get("profile") == "iwxxm_us"


def test_convert_rejects_unknown_product(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """UJ-008 / F28: unknown product must not silently succeed as METAR (api-contract unknown_product)."""
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append({"tac": tac, **kwargs})
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (
                None,
                "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=",
            ),
            "product": (None, "NOTAPRODUCT"),
            "profile": (None, "annex3"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400, response.text[:400]
    assert "unknown_product" in response.text
    assert seen == []  # must fail before convert
