"""Repro: convert-bulletin drops product/profile after tac2iwxxm cutover.

Bug: docs/bug-reports/BUG-2026-07-12-convert-bulletin-product-profile.md
Review: PR #706 / 18-pr-review PRR-009
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

METAR_BULLETIN = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
"""


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_convert_bulletin_forwards_product_and_profile(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Form product/profile must reach convert_metar_tac_with_metadata."""
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append({"tac": tac, **kwargs})
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, METAR_BULLETIN),
            "product": (None, "METAR"),
            "profile": (None, "iwxxm_us"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:400]
    assert len(seen) >= 1
    assert seen[0].get("product") == "METAR"
    assert seen[0].get("profile") == "iwxxm_us"
