"""TC-EV063-003 - API profile wire validation (EV-063 / F35).

Spec: docs/test-plan.md §TC-EV063-003; docs/api-contract.md §EV-063.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.utilities.security import verify_supabase_token

_SAMPLE_METAR = "METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012="


@pytest.fixture
def client():
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def _convert_files(**fields: tuple[None, str]) -> dict:
    base = {
        "manual_text": (None, _SAMPLE_METAR),
        "product": (None, "METAR"),
        "iwxxm_version": (None, "2025-2"),
        "lint": (None, "false"),
    }
    base.update(fields)
    return base


def test_tc_ev063_003_unknown_semantic_profile_on_convert(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(semantic_profile=(None, "NOT_A_REAL_PROFILE")),
    )
    assert response.status_code == 400, response.text[:500]
    body = response.json()
    detail = body.get("detail", body)
    if isinstance(detail, dict):
        assert detail.get("code") == "invalid_semantic_profile"
    else:
        assert "invalid_semantic_profile" in response.text


def test_tc_ev063_003_unknown_semantic_profile_on_validate(client: TestClient) -> None:
    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, _SAMPLE_METAR),
            "semantic_profile": (None, "NOT_A_REAL_PROFILE"),
            "profile": (None, "annex3"),
        },
    )
    assert response.status_code == 400, response.text[:500]
    detail = response.json().get("detail", response.json())
    if isinstance(detail, dict):
        assert detail.get("code") == "invalid_semantic_profile"


def test_tc_ev063_003_unknown_exchange_profile_on_convert(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(exchange_profile=(None, "NOT_AN_EXCHANGE")),
    )
    assert response.status_code == 400, response.text[:500]
    detail = response.json().get("detail", response.json())
    if isinstance(detail, dict):
        assert detail.get("code") == "invalid_exchange_profile"


def test_semantic_profile_canonical_forwards_to_convert(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(semantic_profile=(None, "ICAO_2025")),
    )
    assert response.status_code == 200, response.text[:400]
    assert seen
    assert seen[0].get("profile") == "annex3"


def test_legacy_profile_annex3_still_accepted(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(profile=(None, "annex3")),
    )
    assert response.status_code == 200, response.text[:400]
    assert seen
    assert seen[0].get("profile") == "annex3"


def test_semantic_profile_preferred_over_legacy_profile(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "US_FAA_NWS"),
            profile=(None, "annex3"),
        ),
    )
    assert response.status_code == 200, response.text[:400]
    assert seen
    assert seen[0].get("profile") == "iwxxm_us"
