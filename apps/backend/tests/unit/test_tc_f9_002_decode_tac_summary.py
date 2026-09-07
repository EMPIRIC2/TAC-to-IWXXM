"""T1.5 / TC-F9-002: POST /api/v1/decode-tac returns additive ``summary`` (S013 / EV-009).

Spec: docs/api-contract.md §decode-tac; ADR-025. Existing segment/residual fields
remain unchanged (backward-compatible additive contract).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "product_matrix"

PRODUCTS = ("AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA")

PRODUCT_FILES = {
    "AIRMET": "airmet_basic.tac",
    "METAR": "metar_basic.tac",
    "SIGMET": "sigmet_basic.tac",
    "SPECI": "speci_basic.tac",
    "TAF": "taf_basic.tac",
    "VAA": "vaa_basic.tac",
    "TCA": "tca_basic.tac",
}


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _decode(client: TestClient, *, manual_text: str, product: str):
    return client.post(
        "/api/v1/decode-tac",
        files={
            "manual_text": (None, manual_text),
            "product": (None, product),
        },
    )


@pytest.mark.parametrize("product", PRODUCTS)
def test_decode_tac_response_includes_summary(client: TestClient, product: str) -> None:
    tac = (FIXTURES / PRODUCT_FILES[product]).read_text(encoding="utf-8").strip()
    response = _decode(client, manual_text=tac, product=product)
    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload
    assert isinstance(payload["summary"], str)
    assert payload["summary"].strip()
    # Pre-F9 fields still present (additive contract).
    assert isinstance(payload["segments"], list)
    assert isinstance(payload["residuals"], list)
    assert payload["product"].upper() == product


def test_decode_tac_summary_metar_value_aware(client: TestClient) -> None:
    tac = "METAR KJFK 121251Z 18004KT 10SM FEW250 24/18 A3011="
    response = _decode(client, manual_text=tac, product="METAR")
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert "kjfk" in summary.lower()
    assert "4 kt" in summary
    assert "24 °C" in summary or "24 °c" in summary.lower()
    assert "30.11" in summary


def test_decode_tac_existing_fields_unchanged_shape(client: TestClient) -> None:
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    response = _decode(client, manual_text=tac, product="METAR")
    payload = response.json()
    assert set(payload.keys()) >= {"product", "segments", "residuals", "summary"}
    for seg in payload["segments"]:
        assert set(seg.keys()) >= {"start", "end", "code", "explanation"}
