"""TC-EV064-004 - API CA_ECCC semantic profile wire (EV-064 M6).

Spec: docs/test-plan.md §TC-EV064-004; docs/api-contract.md §EV-063.
"""

from __future__ import annotations

from typing import ClassVar

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.routers import conversion as conversion_router
from src.schemas.validation import AggregatedValidationResult, ValidationLayer, ValidationResult
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
    assert seen
    assert seen[0].get("profile") == "ca_eccc"
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
    assert seen
    assert seen[0].get("profile") == "ca_eccc"


def test_tc_ev064_004_ca_eccc_rejects_wrong_iwxxm_version(client: TestClient) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "CA_ECCC"),
            iwxxm_version=(None, "2025-2"),
        ),
    )
    assert response.status_code in {400, 422}, response.text[:500]


@pytest.mark.parametrize("semantic_profile", ["ICAO_2025", "US_FAA_NWS", "AU_BOM", "NZ_CAA_MET"])
def test_tc_ev064_004_non_ca_profiles_reject_profile_scoped_3_0_0(
    client: TestClient,
    semantic_profile: str,
) -> None:
    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, semantic_profile),
            iwxxm_version=(None, _CA_IWXXM_VERSION),
        ),
    )
    assert response.status_code == 400, response.text[:500]
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "INVALID_IWXXM_VERSION"


def test_tc_ev064_004_ca_eccc_defaults_profile_pinned_version_when_omitted(
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
        files={
            "manual_text": (None, _CA_METAR),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert seen
    assert seen[0].get("profile") == "ca_eccc"
    assert seen[0].get("iwxxm_version") == _CA_IWXXM_VERSION


def test_tc_ev1050_ca_eccc_forwards_report_variant(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm-ca:LWIS xmlns:iwxxm-ca='https://example.test/iwxxm-ca'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "CA_ECCC"),
            report_variant=(None, "LWIS"),
        ),
    )
    assert response.status_code == 200, response.text[:500]
    assert seen
    assert seen[0].get("report_variant") == "LWIS"


def test_tc_ev1050_ca_eccc_rejects_report_variant_product_mismatch(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_convert(tac: str, **kwargs):
        nonlocal called
        called = True
        return "<iwxxm:SPECI xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, "SPECI CYUL 231800Z 24010KT 9999 FEW240 22/12 A3012="),
            "product": (None, "SPECI"),
            "semantic_profile": (None, "CA_ECCC"),
            "report_variant": (None, "LWIS"),
            "iwxxm_version": (None, _CA_IWXXM_VERSION),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400, response.text[:500]
    assert called is False
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "INVALID_REPORT_VARIANT"


def test_tc_ev1050_non_ca_profile_rejects_report_variant(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_convert(tac: str, **kwargs):
        nonlocal called
        called = True
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="),
            "product": (None, "METAR"),
            "semantic_profile": (None, "ICAO_2025"),
            "report_variant": (None, "LWIS"),
            "iwxxm_version": (None, "2025-2"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 400, response.text[:500]
    assert called is False
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "INVALID_REPORT_VARIANT"


def test_tc_ev1050_json_body_forwards_report_variant(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[dict] = []

    def fake_convert(tac: str, **kwargs):
        seen.append(kwargs)
        return "<iwxxm-ca:LWIS xmlns:iwxxm-ca='https://example.test/iwxxm-ca'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [_CA_METAR],
            "product": "METAR",
            "semantic_profile": "CA_ECCC",
            "report_variant": "LWIS",
        },
    )
    assert response.status_code == 200, response.text[:500]
    assert seen
    assert seen[0].get("report_variant") == "LWIS"


def test_tc_ev1050_metadata_echoes_explicit_report_variant(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return "<iwxxm-ca:LWIS xmlns:iwxxm-ca='https://example.test/iwxxm-ca'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files=_convert_files(
            semantic_profile=(None, "CA_ECCC"),
            report_variant=(None, "LWIS"),
        ),
    )
    assert response.status_code == 200, response.text[:500]
    metadata = response.json()["metadata"]
    assert metadata["report_variant"] == "LWIS"


def test_tc_ev1050_metadata_auto_detects_lwis_when_variant_omitted(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _PassValidationService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            return AggregatedValidationResult.from_results(
                [
                    ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO),
                    ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX),
                ]
            )

    def fake_convert(tac: str, **kwargs):
        return "<iwxxm-ca:LWIS xmlns:iwxxm-ca='https://example.test/iwxxm-ca'/>", None

    monkeypatch.setattr(api_module, "ValidationService", _PassValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, "LWIS CYUL 292000Z AUTO 31006KT M00/M02 A2926="),
            "product": (None, "METAR"),
            "semantic_profile": (None, "CA_ECCC"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    metadata = response.json()["metadata"]
    assert metadata["report_variant"] == "LWIS"


def test_tc_ev1050_metadata_omits_report_variant_for_non_ca_profiles(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_convert(tac: str, **kwargs):
        return "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2025-2'/>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        files={
            "manual_text": (None, "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="),
            "product": (None, "METAR"),
            "semantic_profile": (None, "ICAO_2025"),
            "lint": (None, "false"),
        },
    )
    assert response.status_code == 200, response.text[:500]
    metadata = response.json()["metadata"]
    assert "report_variant" not in metadata


def test_tc_ev1050_report_variant_inference_falls_back_to_product() -> None:
    assert (
        conversion_router._infer_report_variant_from_sample(
            "ca_eccc",
            "METAR",
            "AUTO CYUL 292000Z 31006KT 10SM FEW020 M00/M02 A2926=",
        )
        == "METAR"
    )


def test_tc_ev1050_report_variant_inference_returns_none_without_supported_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        conversion_router,
        "supported_report_variants_for_profile",
        lambda emit_profile, product: frozenset({"LWIS"}),
    )
    assert (
        conversion_router._infer_report_variant_from_sample(
            "ca_eccc",
            "METAR",
            "AUTO CYUL 292000Z 31006KT 10SM FEW020 M00/M02 A2926=",
        )
        is None
    )


def test_tc_ev064_004_validate_accepts_ca_eccc_profile(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_validate(xml: str, **kwargs):
        assert kwargs.get("profile") == "ca_eccc"
        assert kwargs.get("iwxxm_version") == _CA_IWXXM_VERSION

        class _Report:
            ok = True
            issues: ClassVar[list[object]] = []

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
