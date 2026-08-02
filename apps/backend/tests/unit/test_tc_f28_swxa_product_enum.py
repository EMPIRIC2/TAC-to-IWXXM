"""T11.5 / TC-F28-006 — runtime ``product=swxa`` enum (S036 / EV-029 / S02.M1).

Accepts ``swxa`` (case-insensitive) on lint/decode/convert; rejects ``swx`` with
``unknown_product`` 400 per api-contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

ANNEX3 = (
    Path(__file__).resolve().parents[4]
    / "packages"
    / "tac2iwxxm"
    / "tests"
    / "fixtures"
    / "annex3_golden"
    / "swxa_a7_3.tac"
)


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart(client: TestClient, path: str, fields: dict[str, str]):
    return client.post(path, files={k: (None, v) for k, v in fields.items()})


def test_normalize_api_product_accepts_swxa_rejects_swx() -> None:
    assert api_module.normalize_api_product("swxa") == "SWXA"
    assert api_module.normalize_api_product("SWXA") == "SWXA"
    with pytest.raises(api_module.HTTPException) as exc_info:
        api_module.normalize_api_product("swx")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "unknown_product"


def test_lint_tac_accepts_product_swxa(client: TestClient) -> None:
    tac = ANNEX3.read_text(encoding="utf-8")
    response = _multipart(client, "/api/v1/lint-tac", {"manual_text": tac, "product": "swxa"})
    assert response.status_code == 200, response.text[:400]
    assert response.json()["ok"] is True


def test_decode_tac_accepts_product_swxa(client: TestClient) -> None:
    tac = ANNEX3.read_text(encoding="utf-8")
    response = _multipart(client, "/api/v1/decode-tac", {"manual_text": tac, "product": "SWXA"})
    assert response.status_code == 200, response.text[:400]
    body = response.json()
    assert body["product"] == "SWXA"
    assert "summary" in body


def test_convert_accepts_product_swxa(client: TestClient) -> None:
    tac = ANNEX3.read_text(encoding="utf-8")
    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": tac,
            "product": "swxa",
            "profile": "annex3",
            "lint": "false",
        },
    )
    assert response.status_code == 200, response.text[:800]
    body = response.json()
    results = body.get("results") or []
    assert results, body
    xml = results[0].get("content") or results[0].get("xml") or ""
    assert "SpaceWeatherAdvisory" in xml


@pytest.mark.parametrize("bad", ("swx", "SWX", "notaproduct"))
def test_convert_rejects_unknown_product_alias(client: TestClient, bad: str) -> None:
    response = _multipart(
        client,
        "/api/v1/convert",
        {
            "manual_text": "SWX ADVISORY\nDTG: 20201108/0100Z\n",
            "product": bad,
            "profile": "annex3",
            "lint": "false",
        },
    )
    assert response.status_code == 400, response.text[:400]
    assert "unknown_product" in response.text
