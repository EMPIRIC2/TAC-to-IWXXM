"""TC-EV068-004 — API extensions=IWXXM_CA wire (EV-068 M5).

Spec: docs/test-plan.md §TC-EV068-004; docs/api-contract.md §EV-063 extensions.
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


class _FakeStage:
    def __init__(self, stage: str, label: str, ok: bool, issues: list) -> None:
        self.stage = stage
        self.label = label
        self.ok = ok
        self.issues = issues


class _FakeReport:
    def __init__(self, *, product: str | None, stages: list[_FakeStage]) -> None:
        self.ok = True
        self.issues = []
        self.stages = stages
        self.product = product


def test_tc_ev068_004_iwxxm_ca_forwards_product_and_stages(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_validate(xml: str, **kwargs):
        seen.append(kwargs)
        return _FakeReport(
            product=kwargs.get("product"),
            stages=[
                _FakeStage("wellformed", "Well-formed XML", True, []),
                _FakeStage("ca_xsd", "Canadian extension schema", True, []),
            ],
        )

    monkeypatch.setattr(api_module, "_call_iwxxm_validate", fake_validate)

    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, _CA_METAR),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "product": (None, "METAR"),
            "extensions": (None, "IWXXM_CA"),
            "stop_on_error": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    body = response.json()
    assert seen and seen[0].get("product") == "METAR"
    assert body.get("extensions") == ["IWXXM_CA"]
    stages = body.get("package_stages") or []
    assert any(stage.get("stage") == "ca_xsd" for stage in stages)
    assert all(stage.get("label") for stage in stages)


def test_tc_ev068_004_without_iwxxm_ca_skips_product(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_validate_iwxxm(xml: str, **kwargs):
        seen.append(kwargs)
        return _FakeReport(product=kwargs.get("product"), stages=[])

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_validate_iwxxm)

    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, _CA_METAR),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "product": (None, "METAR"),
            "stop_on_error": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert seen and seen[0].get("product") is None
    assert "package_stages" not in response.json()


def test_tc_ev068_004_unknown_extension_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/validate",
        files={
            "manual_text": (None, _CA_METAR),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "extensions": (None, "IWXXM_US_3"),
            "stop_on_error": (None, "false"),
        },
    )
    assert response.status_code == 400, response.text[:500]


def test_tc_ev068_004_convert_tac_forwards_extensions_on_validate_output(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_validate_iwxxm(xml: str, **kwargs):
        seen.append(kwargs)
        return _FakeReport(product=kwargs.get("product"), stages=[])

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_validate_iwxxm)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, _CA_METAR),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "validate_output": (None, "true"),
            "extensions": (None, "IWXXM_CA"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert seen and seen[0].get("product") == "METAR"


def test_tc_ev068_004_convert_iwxxm_pass_through_forwards_extensions(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []
    xml_payload = "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>"

    def fake_validate_iwxxm(xml: str, **kwargs):
        seen.append(kwargs)
        return _FakeReport(product=kwargs.get("product"), stages=[])

    monkeypatch.setattr(api_module, "iwxxm_validate_fn", fake_validate_iwxxm)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, xml_payload),
            "product": (None, "iwxxm"),
            "semantic_profile": (None, "CA_ECCC"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "validate_output": (None, "true"),
            "extensions": (None, "IWXXM_CA"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert seen and seen[0].get("product") == "IWXXM"
