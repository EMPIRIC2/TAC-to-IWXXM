"""TC-EV064-004 — API CA_ECCC semantic profile wire (EV-064 M6).

Spec: docs/test-plan.md §TC-EV064-004; docs/api-contract.md §EV-063.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.utilities.security import verify_supabase_token

_CA_METAR = "METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012="
_CA_IWXXM_VERSION = "3.0.0"


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
        "manual_text": (None, _CA_METAR),
        "product": (None, "METAR"),
        "iwxxm_version": (None, _CA_IWXXM_VERSION),
        "lint": (None, "false"),
    }
    base.update(fields)
    return base


def test_tc_ev064_004_semantic_profile_ca_eccc_forwards_emit_key(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(semantic_profile=(None, "CA_ECCC")),
    )
    assert response.status_code == 200, response.text[:500]
    assert seen and seen[0].get("profile") == "ca_eccc"
    assert seen[0].get("iwxxm_version") == _CA_IWXXM_VERSION


def test_tc_ev064_004_legacy_profile_ca_eccc_alias(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(profile=(None, "ca_eccc")),
    )
    assert response.status_code == 200, response.text[:500]
    assert seen and seen[0].get("profile") == "ca_eccc"


def test_tc_ev064_004_ca_eccc_rejects_wrong_iwxxm_version(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "CA_ECCC"),
            iwxxm_version=(None, "2025-2"),
        ),
    )
    assert response.status_code in {400, 422}, response.text[:500]


def test_tc_ev064_004_validate_accepts_ca_eccc_profile(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_validate(xml: str, **kwargs):
        assert kwargs.get("profile") == "ca_eccc"
        assert kwargs.get("iwxxm_version") == _CA_IWXXM_VERSION

        class _Report:
            ok = True
            issues = []

        return _Report()

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_validate)

    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, _CA_METAR),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "profile": (None, "annex3"),
        },
    )
    assert response.status_code == 200, response.text[:500]
