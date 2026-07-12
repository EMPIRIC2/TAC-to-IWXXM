"""TC-F6-030 T2 / T3.3: POST /convert-bulletin multi-result schema (Q6=A, Q7=C)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

FIXTURE_TEXT = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
"""


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _multipart_bulletin(
    client: TestClient,
    *,
    manual_text: str,
    product: str = "METAR",
    profile: str = "annex3",
    lint: str = "true",
):
    return client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, manual_text),
            "product": (None, product),
            "profile": (None, profile),
            "lint": (None, lint),
        },
    )


def test_convert_bulletin_route_multi_result_schema(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Partial-success multi-result shape: bulletin_meta + results[] (Q6=A, Q7=C)."""

    def fake_convert(tac: str, **kwargs):
        return f"<iwxxm:METAR>{tac[:20]}</iwxxm:METAR>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(client, manual_text=FIXTURE_TEXT)
    assert response.status_code == 200
    payload = response.json()

    meta = payload["bulletin_meta"]
    assert meta["ahl"] == "SAUS31 KZNY 121200"
    assert meta["report_count"] == 2
    assert meta["tt"] == "SA"
    assert meta["aa"] == "US"
    assert meta["cccc"] == "KZNY"
    assert meta["yygggg"] == "121200"

    results = payload["results"]
    assert len(results) == 2
    assert results[0]["report_index"] == 0
    assert results[0]["ok"] is True
    assert results[0]["tac_input"].startswith("METAR KJFK")
    assert results[0]["xml"]
    assert results[0]["issues"] == []
    assert isinstance(results[0]["fixes"], list)
    assert results[1]["report_index"] == 1
    assert results[1]["ok"] is True


def test_convert_bulletin_partial_success_on_per_report_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """HTTP 200 when split succeeds even if some reports fail (Q6=A)."""
    calls = {"n": 0}

    def fake_convert(tac: str, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return "<iwxxm:METAR>ok</iwxxm:METAR>", None
        raise api_module.ConversionError("parse boom")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = _multipart_bulletin(client, manual_text=FIXTURE_TEXT, lint="false")
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["ok"] is True
    assert results[1]["ok"] is False
    assert results[1]["xml"] is None
    assert any(i["code"] == "parse_failed" for i in results[1]["issues"])


def test_convert_bulletin_empty_bulletin_400(client: TestClient) -> None:
    response = _multipart_bulletin(client, manual_text="SAUS31 KZNY 121200\n")
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "empty_bulletin"


def test_convert_bulletin_split_failed_422(client: TestClient) -> None:
    response = _multipart_bulletin(
        client,
        manual_text="METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\n",
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "bulletin_split_failed"


def test_convert_bulletin_requires_product(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert-bulletin",
        files={"manual_text": (None, FIXTURE_TEXT)},
    )
    assert response.status_code == 422
