"""T2.3 / TC-F7-002: API contract for POST /api/v1/decode-tac (S011 / EV-008).

Spec: docs/api-contract.md Decode TAC; docs/test-plan.md TC-F7-002; UJ-015.
Expected red until T2.4 implements the route + decode library.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURES = Path(__file__).resolve().parents[4] / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "product_matrix"

PRODUCTS = ("AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA")

GOLDEN_PRODUCT_FILES = {
    "METAR": "metar_basic.tac",
    "SPECI": "speci_basic.tac",
    "TAF": "taf_basic.tac",
}


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart_decode(
    client: TestClient,
    *,
    manual_text: str,
    product: str | None = "METAR",
):
    """POST /decode-tac as multipart/form-data (same transport as lint-tac / convert)."""
    files: dict[str, tuple[None, str]] = {
        "manual_text": (None, manual_text),
    }
    if product is not None:
        files["product"] = (None, product)
    return client.post("/api/v1/decode-tac", files=files)


def _assert_well_formed_decode(payload: dict, *, product: str) -> None:
    assert payload["product"].upper() == product.upper()
    assert isinstance(payload["segments"], list)
    assert isinstance(payload["residuals"], list)
    for seg in payload["segments"]:
        assert isinstance(seg["start"], int)
        assert isinstance(seg["end"], int)
        assert 0 <= seg["start"] <= seg["end"]
        assert "code" in seg
        assert "explanation" in seg
    for residual in payload["residuals"]:
        assert isinstance(residual["start"], int)
        assert isinstance(residual["end"], int)
        assert "text" in residual


def test_decode_tac_route_exists_multipart(client: TestClient) -> None:
    """POST /api/v1/decode-tac accepts multipart and returns segments + residuals."""
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    response = _multipart_decode(client, manual_text=tac, product="METAR")
    assert response.status_code == 200
    payload = response.json()
    _assert_well_formed_decode(payload, product="METAR")


def test_decode_tac_product_required(client: TestClient) -> None:
    """product is required (S011 M2=A / api-contract)."""
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    response = _multipart_decode(client, manual_text=tac, product=None)
    assert response.status_code in {400, 422}


@pytest.mark.parametrize("product,filename", list(GOLDEN_PRODUCT_FILES.items()))
def test_decode_tac_golden_segments_non_empty(
    client: TestClient,
    product: str,
    filename: str,
) -> None:
    """TC-F7-002: METAR/SPECI/TAF golden fixtures yield non-empty segment lists."""
    tac = (FIXTURES / filename).read_text(encoding="utf-8").strip()
    response = _multipart_decode(client, manual_text=tac, product=product)
    assert response.status_code == 200
    payload = response.json()
    _assert_well_formed_decode(payload, product=product)
    assert payload["segments"], f"{product} expected non-empty segments"


@pytest.mark.parametrize("product", PRODUCTS)
def test_decode_tac_all_seven_products_well_formed(client: TestClient, product: str) -> None:
    """All seven products return a well-formed decode response (VAA/TCA may be residual-heavy)."""
    case_file = {
        "AIRMET": "airmet_basic.tac",
        "METAR": "metar_basic.tac",
        "SIGMET": "sigmet_basic.tac",
        "SPECI": "speci_basic.tac",
        "TAF": "taf_basic.tac",
        "VAA": "vaa_basic.tac",
        "TCA": "tca_basic.tac",
    }[product]
    tac = (FIXTURES / case_file).read_text(encoding="utf-8").strip()
    response = _multipart_decode(client, manual_text=tac, product=product)
    assert response.status_code == 200
    payload = response.json()
    _assert_well_formed_decode(payload, product=product)
    # Residuals OK when undecoded; response must still be shaped.
    assert isinstance(payload["segments"], list)
    assert isinstance(payload["residuals"], list)


def test_decode_tac_rejects_json_content_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/decode-tac",
        json={"manual_text": "METAR KJFK 231751Z NIL=", "product": "METAR"},
    )
    assert response.status_code in {415, 422}


def test_decode_tac_reads_uploaded_files(client: TestClient) -> None:
    tac = (FIXTURES / "metar_basic.tac").read_text(encoding="utf-8").strip()
    response = client.post(
        "/api/v1/decode-tac",
        files=[
            ("product", (None, "METAR")),
            ("manual_text", (None, "")),
            ("files", ("a.tac", tac.encode("utf-8"), "text/plain")),
        ],
    )
    assert response.status_code == 200
    payload = response.json()
    _assert_well_formed_decode(payload, product="METAR")
    assert payload["segments"]
