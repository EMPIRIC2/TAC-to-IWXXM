"""TC-F6-054: the main convert path accepts a pasted abbreviated heading."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.utilities.security import verify_supabase_token

_METAR = "METAR TNCM 081200Z 10010KT 9999 FEW018 30/24 Q1017 NOSIG="
_SAMPLE = f"SAXX31 TNCM 081200\n{_METAR}"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Authenticated client for the convert routes."""

    async def override_verify_token() -> dict[str, str]:
        return {"sub": "test-user", "aud": "test-aud"}

    app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_main_convert_accepts_the_st_maarten_heading(client: TestClient) -> None:
    bulletin = client.post(
        "/api/v1/convert-bulletin",
        files={
            "manual_text": (None, _SAMPLE),
            "product": (None, "METAR"),
            "lint": (None, "false"),
        },
    )
    assert bulletin.status_code == 200
    bulletin_body = bulletin.json()
    assert bulletin_body["bulletin_meta"]["ahl"] == "SAXX31 TNCM 081200"
    assert bulletin_body["results"][0]["ok"] is True

    converted = client.post(
        "/api/v1/convert",
        data={
            "manual_text": _SAMPLE,
            "product": "METAR",
            "lint": "false",
            "bulletin_date": "2026-10-08",
        },
    )
    assert converted.status_code == 200
    payload = converted.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0
    xml = payload["results"][0]["content"]
    assert "TNCM" in xml
    assert "METAR" in xml
    assert payload["results"][0]["tac_input"] == _METAR
    assert not any("keyword" in issue["message"].lower() for issue in payload["issues"])


def test_heading_without_a_report_fails_on_the_main_convert_path(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        data={"manual_text": "SAXX31 TNCM 081200\n", "product": "METAR", "lint": "false"},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "empty_bulletin"
    assert detail["message"] == "No TAC reports found after the abbreviated heading."


def test_malformed_heading_fails_on_the_main_convert_path(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": f"QQXX31 TNCM 081200\n{_METAR}",
            "product": "METAR",
            "lint": "false",
        },
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_AHL"
    assert "abbreviated heading is not valid" in detail["message"]
