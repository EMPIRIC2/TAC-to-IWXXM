"""TC-EV060-1005 / UJ-062: Bulletin ID and Issuing Center on convert (#1005).

Spec: docs/test-plan.md TC-EV060-1005-001..003; [Corpus: api] [Corpus: tests]
[Corpus: product §F7].
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

TAC_SAMPLE = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="


def test_parse_optional_bulletin_fields_empty_and_valid() -> None:
    assert api_module.parse_optional_bulletin_id("") == ""
    assert api_module.parse_optional_bulletin_id("saaa00") == "SAAA00"
    assert api_module.parse_optional_issuing_center(None) == ""
    assert api_module.parse_optional_issuing_center("kwbc") == "KWBC"


@pytest.fixture
def client() -> TestClient:
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _convert(client: TestClient, fields: dict[str, str]):
    payload = {"manual_text": TAC_SAMPLE, "product": "METAR", **fields}
    return client.post("/api/v1/convert", files={k: (None, v) for k, v in payload.items()})


def test_tc_ev060_1005_001_bulletin_fields_round_trip(client: TestClient) -> None:
    response = _convert(
        client,
        {"bulletin_id": "saaa00", "issuing_center": "kwbc"},
    )
    assert response.status_code == 200, response.text[:400]
    metadata = response.json().get("metadata") or {}
    assert metadata.get("bulletin_id") == "SAAA00"
    assert metadata.get("issuing_center") == "KWBC"


def test_tc_ev060_1005_002_empty_bulletin_fields_ok(client: TestClient) -> None:
    response = _convert(client, {"bulletin_id": "", "issuing_center": ""})
    assert response.status_code == 200, response.text[:400]
    metadata = response.json().get("metadata") or {}
    assert not metadata.get("bulletin_id")
    assert not metadata.get("issuing_center")
    codes = [i.get("code") for i in (response.json().get("issues") or [])]
    assert "INVALID_BULLETIN_ID" not in codes
    assert "INVALID_ISSUING_CENTER" not in codes


def test_tc_ev060_1005_003_invalid_issuing_center_one_error(client: TestClient) -> None:
    response = _convert(client, {"issuing_center": "KW1C"})
    assert response.status_code == 400
    detail = response.json().get("detail") or {}
    issues = detail.get("issues") or []
    assert len(issues) == 1
    assert issues[0]["code"] == "INVALID_ISSUING_CENTER"
    assert "issuing" in (issues[0].get("message") or "").lower()


def test_tc_ev060_1005_003_invalid_bulletin_id_one_error(client: TestClient) -> None:
    response = _convert(client, {"bulletin_id": "SAAA0X"})
    assert response.status_code == 400
    detail = response.json().get("detail") or {}
    issues = detail.get("issues") or []
    assert len(issues) == 1
    assert issues[0]["code"] == "INVALID_BULLETIN_ID"
