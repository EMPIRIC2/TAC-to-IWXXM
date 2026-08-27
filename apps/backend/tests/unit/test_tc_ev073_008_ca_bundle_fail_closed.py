"""TC-EV073-008 - Fail-closed when CA extension vendor pin missing (EV-073 M2)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from src import api as api_module

_CA_METAR = "METAR CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012="
_CA_IWXXM_VERSION = "3.0.0"


@pytest.fixture
def client() -> TestClient:
    return TestClient(api_module.app)


def test_tc_ev073_008_convert_rejects_missing_ca_bundle(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_bundle.ca_eccc_bundle_available",
        lambda **_: False,
    )

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _CA_METAR),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "extensions": (None, "IWXXM_CA"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400, response.text[:500]
    detail = response.json()["detail"]
    assert detail.get("code") == "missing_ca_extension_bundle"
    assert "Canadian" in detail.get("message", "")


def test_tc_ev073_008_schema_status_surfaces_bundle_pin(client: TestClient) -> None:
    response = client.get("/api/v1/schema-status")
    assert response.status_code == 200
    pins = response.json().get("profile_pins") or {}
    ca = pins.get("ca_eccc") or {}
    assert ca.get("iwxxm_version") == "3.0.0"
    assert isinstance(ca.get("extension_bundle_available"), bool)
