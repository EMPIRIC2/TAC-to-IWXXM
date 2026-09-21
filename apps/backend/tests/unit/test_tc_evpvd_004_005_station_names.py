"""TC-EVPVD-004..005 — /decode-tac airport name enrichment via F3 (#724 / #1221).

[Corpus: product §F9] [Corpus: api] [Corpus: tests §TC-EVPVD]
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token() -> dict[str, str]:
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _decode(client: TestClient, tac: str, product: str = "METAR") -> dict:
    response = client.post(
        "/api/v1/decode-tac",
        files={
            "manual_text": (None, tac),
            "product": (None, product),
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_tc_evpvd_004_decode_tac_kjfk_includes_airport_name(client: TestClient) -> None:
    body = _decode(
        client,
        "METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3012=",
    )
    station = next(s for s in body["segments"] if s["code"].upper() == "KJFK")
    assert "Kennedy" in station["explanation"] or "JFK" in station["explanation"]
    assert "KJFK" in body["summary"]
    assert "station" in body["summary"].lower()
    # Name + ICAO together in summary when lookup hits
    assert "(" in body["summary"]
    assert "KJFK" in body["summary"]


def test_tc_evpvd_005_decode_tac_unknown_icao_soft_fails(client: TestClient) -> None:
    body = _decode(
        client,
        "METAR ZZ99 121251Z 18004KT 10SM FEW250 24/18 A3012=",
    )
    station = next(s for s in body["segments"] if s["code"].upper() == "ZZ99")
    assert "ZZ99" in station["explanation"]
    assert "station ZZ99" in body["summary"]
    assert body["product"] == "METAR"
