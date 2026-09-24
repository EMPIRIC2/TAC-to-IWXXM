"""HTTP integration and end-to-end coverage for OurAirports reference lookup.

The public source is a committed fixture. These tests do not call the network.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from reference_lookup import set_coordinate_source
from reference_lookup.lookup import CsvCoordinateSource
from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "reference-lookup" / "tests" / "fixtures"
SRQ_TAC = "YUDD SIGMET 6 VALID 101200/101600 YUSO-\nYUDD SHANLON FIR/UIR SEV ICE FCST FROM SRQ MOV NE 30KT NC=\n"


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    source = CsvCoordinateSource(
        (FIXTURES / "navaids.csv").read_text(encoding="utf-8"),
        (FIXTURES / "airports.csv").read_text(encoding="utf-8"),
    )
    set_coordinate_source(source)
    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    set_coordinate_source(None)
    api_module.app.dependency_overrides.clear()


def _convert(client: TestClient, tac: str) -> dict:
    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, tac),
            "product": (None, "SIGMET"),
            "conversion_library_id": (None, "LIB.CONVERSION.US_FAA_NWS"),
            "iwxxm_version": (None, "2025-2"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    return response.json()


def test_integration_convert_srq_uses_the_public_fixture(client: TestClient) -> None:
    payload = _convert(client, SRQ_TAC)
    assert payload.get("successful", 0) >= 1
    content = payload["results"][0]["content"]
    assert "27.3978" in content


def test_e2e_health_then_srq_convert_and_unknown_vor(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] in {"healthy", "degraded"}

    hit = _convert(client, SRQ_TAC)
    assert "27.3978" in hit["results"][0]["content"]

    miss = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, SRQ_TAC.replace("FROM SRQ", "FROM ZZZ")),
            "product": (None, "SIGMET"),
            "conversion_library_id": (None, "LIB.CONVERSION.US_FAA_NWS"),
            "iwxxm_version": (None, "2025-2"),
            "lint": (None, "false"),
        },
    )
    assert miss.status_code == 400
    assert "unknown VOR reference 'ZZZ'" in miss.text
