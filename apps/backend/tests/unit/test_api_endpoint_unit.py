"""Endpoint-level unit tests for /api/v1/convert with mocked dependencies."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from src import api as api_module
from src.schemas.validation import AggregatedValidationResult, ValidationLayer, ValidationResult
from src.utilities.security import verify_supabase_token


class _FakeValidationService:
    def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
        return AggregatedValidationResult.from_results(
            [
                ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO),
                ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX),
            ]
        )


@pytest.fixture
def client(monkeypatch):
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    def fake_convert(_tac: str, iwxxm_version: str = "2025-2", validate: bool = False, **_kwargs: Any):
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _FakeValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_convert_rejects_empty_input(client):
    response = client.post("/api/v1/convert", data={})

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "NO_INPUT"


def test_convert_rejects_invalid_json_body(client):
    response = client.post(
        "/api/v1/convert",
        content="{bad-json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "INVALID_JSON_BODY"


def test_convert_rejects_invalid_json_schema_body(client):
    response = client.post(
        "/api/v1/convert",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "bad"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "REQUEST_VALIDATION_ERROR"


def test_convert_handles_manual_text_with_mocked_converter(client):
    response = client.post(
        "/api/v1/convert",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0
    assert "<iwxxm:METAR" in payload["results"][0]["content"]


def test_convert_json_body_propagates_residuals_flag(client, monkeypatch):
    """TC-EV981 — JSON ConversionRequest wires propagate_residuals_to_remarks."""
    captured: dict[str, Any] = {}

    def fake_convert(_tac: str, iwxxm_version: str = "2025-2", validate: bool = False, **kwargs: Any):
        captured.update(kwargs)
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013 ZZZZ="],
            "version": "2025-2",
            "profile": "iwxxm_us",
            "propagate_residuals_to_remarks": True,
        },
    )

    assert response.status_code == 200, response.text[:500]
    assert captured.get("propagate_residuals_to_remarks") is True


def test_convert_manual_recent_weather_resh_is_normalized_before_validation(client, monkeypatch):
    class _StrictRecentWxValidationService:
        def validate_all_layers(self, tac_text: str) -> AggregatedValidationResult:
            if " RESH " in f" {tac_text} ":
                layer = ValidationResult(passed=False, layer=ValidationLayer.TAC_SYNTAX)
                layer.add_issue(level="error", message="truncated recent weather", code="BAD_REWX")
                return AggregatedValidationResult.from_results([layer])

            return AggregatedValidationResult.from_results(
                [ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX)]
            )

    def _assert_normalized_convert(
        tac: str,
        iwxxm_version: str = "2025-2",
        validate: bool = False,
        **_kwargs: Any,
    ):
        assert "RESHUP" in tac
        assert " RESH " not in f" {tac} "
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _StrictRecentWxValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _assert_normalized_convert)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR TTPP 121000Z 00000KT 9999 FEW010 26/25 Q1013 RESH NOSIG",
            "stop_on_error": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0
    assert any(issue["code"] == "RECENT_WX_NORMALIZED" for issue in payload["issues"])


def test_convert_manual_recent_weather_reshra_passes_without_rewrite(client, monkeypatch):
    class _RecentWxValidationService:
        def validate_all_layers(self, _tac_text: str) -> AggregatedValidationResult:
            return AggregatedValidationResult.from_results(
                [ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX)]
            )

    def _assert_no_rewrite_convert(
        tac: str,
        iwxxm_version: str = "2025-2",
        validate: bool = False,
        **_kwargs: Any,
    ):
        assert "RESHRA" in tac
        assert "RESHUP" not in tac
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _RecentWxValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _assert_no_rewrite_convert)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR TTPP 121000Z 00000KT 9999 FEW010 26/25 Q1013 RESHRA NOSIG",
            "stop_on_error": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0


def test_convert_json_recent_weather_resh_is_normalized_before_validation(client, monkeypatch):
    class _StrictRecentWxValidationService:
        def validate_all_layers(self, tac_text: str) -> AggregatedValidationResult:
            if " RESH " in f" {tac_text} ":
                layer = ValidationResult(passed=False, layer=ValidationLayer.TAC_SYNTAX)
                layer.add_issue(level="error", message="truncated recent weather", code="BAD_REWX")
                return AggregatedValidationResult.from_results([layer])

            return AggregatedValidationResult.from_results(
                [ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX)]
            )

    def _assert_json_normalized_convert(
        tac: str,
        iwxxm_version: str = "2025-2",
        validate: bool = False,
        **kwargs: Any,
    ):
        assert "RESHUP" in tac
        assert " RESH " not in f" {tac} "
        assert kwargs.get("lenient") is False
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _StrictRecentWxValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _assert_json_normalized_convert)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR TTPP 121000Z 00000KT 9999 FEW010 26/25 Q1013 RESH NOSIG"],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0
    assert any(issue["code"] == "RECENT_WX_NORMALIZED" for issue in payload["issues"])


def test_convert_json_recent_weather_reshra_passes_without_rewrite(client, monkeypatch):
    class _RecentWxValidationService:
        def validate_all_layers(self, _tac_text: str) -> AggregatedValidationResult:
            return AggregatedValidationResult.from_results(
                [ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX)]
            )

    def _assert_json_no_rewrite_convert(
        tac: str,
        iwxxm_version: str = "2025-2",
        validate: bool = False,
        **kwargs: Any,
    ):
        assert "RESHRA" in tac
        assert "RESHUP" not in tac
        assert kwargs.get("lenient") is False
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _RecentWxValidationService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", _assert_json_no_rewrite_convert)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR TTPP 121000Z 00000KT 9999 FEW010 26/25 Q1013 RESHRA NOSIG"],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0
    assert all(issue["code"] != "RECENT_WX_NORMALIZED" for issue in payload["issues"])


def test_convert_handles_file_upload_with_mocked_converter(client):
    response = client.post(
        "/api/v1/convert",
        files=[("files", ("sample.tac", "METAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013", "text/plain"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 1
    assert payload["successful"] == 1


def test_convert_stop_on_error_true_stops_after_first_failure(client, monkeypatch):
    class _StopOnErrorValidationService:
        def validate_all_layers(self, tac_text: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            if "BAD" in tac_text:
                failed.add_issue(
                    level="error",
                    message="bad tac",
                    code="BAD_TAC",
                )
            else:
                failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            return AggregatedValidationResult.from_results([failed])

    monkeypatch.setattr(api_module, "ValidationService", _StopOnErrorValidationService)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "BAD METAR PAYLOAD",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1
    assert len(detail["errors"]) == 1


def test_convert_invalid_iwxxm_version_returns_error(client):
    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            "iwxxm_version": "9999-9",
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "INVALID_IWXXM_VERSION"


def test_convert_xml_rejection_tac_only_path(client, monkeypatch):
    class _FakeOrchestrator:
        def validate_wellformed(self, _xml):
            return SimpleNamespace(passed=True, issues=[])

        def validate_xml_schema(self, _xml, _version):
            return SimpleNamespace(is_valid=True, issues=[])

    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _FakeOrchestrator())

    response = client.post(
        "/api/v1/convert",
        data={"validate_output": "true"},
        files=[("files", ("sample.xml", "<iwxxm/>", "application/xml"))],
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "XML_INPUT_NOT_CONVERTIBLE"


def test_convert_mixed_manual_and_xml_file_partial_success(client, monkeypatch):
    class _FakeOrchestrator:
        def validate_wellformed(self, _xml):
            return SimpleNamespace(passed=True, issues=[])

        def validate_xml_schema(self, _xml, _version):
            return SimpleNamespace(is_valid=True, issues=[])

    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _FakeOrchestrator())

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            "validate_output": "true",
            "stop_on_error": "false",
        },
        files=[("files", ("sample.xml", "<iwxxm/>", "application/xml"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 2
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "XML_INPUT_NOT_CONVERTIBLE" for issue in payload["issues"])
