"""TC-EV063 / EV-bridge — Convert profile wire after library hard cut.

Spec: docs/test-plan.md §TC-EVBRIDGE-007; docs/api-contract.md (library ids).
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


def test_unknown_conversion_library_on_convert(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(conversion_library_id=(None, "LIB.CONVERSION.NOT_A_REAL_PROFILE")),
    )
    assert response.status_code == 400, response.text[:500]
    assert "Unknown conversion library" in response.text


def test_legacy_semantic_profile_rejected_on_convert(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(semantic_profile=(None, "ICAO_2025")),
    )
    assert response.status_code == 422, response.text[:500]
    assert "Legacy convert fields" in response.text
    assert "semantic_profile" in response.text


def test_legacy_exchange_profile_rejected_on_convert(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(exchange_profile=(None, "GLOBAL_AFS")),
    )
    assert response.status_code == 422, response.text[:500]
    assert "exchange_profile" in response.text


def test_legacy_profile_alias_rejected_on_convert(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(profile=(None, "annex3")),
    )
    assert response.status_code == 422, response.text[:500]
    assert "profile" in response.text


def test_conversion_library_forwards_emit_key(
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
        files=_convert_files(conversion_library_id=(None, "LIB.CONVERSION.ICAO_2025")),
    )
    assert response.status_code == 200, response.text[:400]
    assert seen
    assert seen[0].get("profile") == "annex3"


def test_us_conversion_library_forwards_emit_key(
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
        files=_convert_files(conversion_library_id=(None, "LIB.CONVERSION.US_FAA_NWS")),
    )
    assert response.status_code == 200, response.text[:400]
    assert seen
    assert seen[0].get("profile") == "iwxxm_us"


def test_tc_ev063_003_unknown_semantic_profile_on_validate(client: TestClient) -> None:
    """Validate still uses semantic_profile (not Convert hard cut)."""
    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, _SAMPLE_METAR),
            "semantic_profile": (None, "NOT_A_REAL_PROFILE"),
            "product": (None, "METAR"),
        },
    )
    assert response.status_code == 400, response.text[:500]
    detail = response.json().get("detail", response.json())
    if isinstance(detail, dict):
        assert detail.get("code") == "invalid_semantic_profile"
