"""API unit tests for convert-zip branches and remaining stop_on_error paths."""

from __future__ import annotations

import io
import zipfile
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src import api as api_module
from src.schemas.validation import AggregatedValidationResult, ValidationLayer, ValidationResult
from src.utilities.conversion import ConversionError
from src.utilities.security import verify_supabase_token


class _FakeStatsService:
    async def log_translation(self, **_kwargs: Any) -> str:
        return "test-translation-id"


class _FakeWebhookService:
    async def notify_translation_failed(self, **_kwargs: Any) -> None:
        return None

    async def notify_translation_success(self, **_kwargs: Any) -> None:
        return None

    async def notify_translation_completed(self, **_kwargs: Any) -> None:
        return None

    async def notify_bulk_completed(self, **_kwargs: Any) -> None:
        return None


class _ValidationPassService:
    def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
        return AggregatedValidationResult.from_results(
            [ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)]
        )


def _read_zip_payload(content: bytes) -> dict[str, str]:
    with zipfile.ZipFile(io.BytesIO(content), "r") as zf:
        return {name: zf.read(name).decode("utf-8") for name in zf.namelist()}


@pytest.fixture
def client(monkeypatch):
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    def fake_convert(tac: str, iwxxm_version: str = "2025-2", **_kwargs: Any):
        xml = f'<iwxxm:METAR version="{iwxxm_version}">{tac[:16]}</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _ValidationPassService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(api_module, "statistics_service", _FakeStatsService())
    monkeypatch.setattr(api_module, "webhook_service", _FakeWebhookService())

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_convert_zip_rejects_invalid_json_body(client):
    response = client.post(
        "/api/v1/convert-zip",
        content="{bad-json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 422
    assert "Invalid JSON in request body" in response.json()["detail"]


def test_convert_zip_rejects_invalid_json_schema_body(client):
    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "bad"},
    )

    assert response.status_code == 422
    assert "Validation error:" in response.json()["detail"]


def test_convert_zip_json_metars_mixed_success_and_validation_failure(client, monkeypatch):
    class _ValidationMixedService:
        def validate_all_layers(self, tac_text: str) -> AggregatedValidationResult:
            result = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            if "BAD" in tac_text:
                result.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([result])

    monkeypatch.setattr(api_module, "ValidationService", _ValidationMixedService)

    response = client.post(
        "/api/v1/convert-zip",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "BAD METAR PAYLOAD",
            ],
            "version": "2025-2",
        },
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "metar_1.xml" in zip_data
    assert "errors.txt" in zip_data
    assert "Validation failed" in zip_data["errors.txt"]


def test_convert_zip_file_read_and_xml_rejection_branches(client, monkeypatch):
    async def fake_read_uploaded_text(upload_file):
        if (upload_file.filename or "").startswith("empty"):
            return None, "empty file"
        return "<iwxxm:METAR/>", None

    def fake_classify(**_kwargs: Any):
        return {
            "message": "XML input is valid, but /api/v1/convert-zip is TAC only.",
            "hint": "Use TAC files for conversion.",
            "code": "XML_INPUT_NOT_CONVERTIBLE",
            "layer": "xml_input",
        }

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "classify_and_validate_upload_content", fake_classify)

    response = client.post(
        "/api/v1/convert-zip",
        files=[
            ("files", ("empty.txt", "ignored", "text/plain")),
            ("files", ("sample.xml", "ignored", "application/xml")),
        ],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "empty.txt: empty file" in zip_data["errors.txt"]
    assert "sample.xml: XML input is valid" in zip_data["errors.txt"]


def test_convert_zip_json_conversion_and_unexpected_error_paths(client, monkeypatch):
    call_count = {"value": 0}

    def flaky_convert(_tac: str, iwxxm_version: str = "2025-2", **_kwargs: Any):
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise ConversionError("conversion failed")
        if call_count["value"] == 2:
            raise RuntimeError("unexpected failure")
        return f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>', None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", flaky_convert)

    response = client.post(
        "/api/v1/convert-zip",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
        },
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "metar_3.xml" in zip_data
    assert "errors.txt" in zip_data
    assert "metar_1: conversion failed" in zip_data["errors.txt"]
    assert "metar_2: unexpected error unexpected failure" in zip_data["errors.txt"]


def test_convert_stop_on_error_true_manual_breaks_on_conversion_error(client, monkeypatch):
    def always_fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced conversion failure")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", always_fail_convert)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": (
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013\nMETAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013"
            ),
            "stop_on_error": "true",
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1
    assert detail["issues"][0]["code"] == "CONVERSION_ERROR"


def test_convert_stop_on_error_true_files_break_on_conversion_error(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    def always_fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced conversion failure")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", always_fail_convert)

    response = client.post(
        "/api/v1/convert",
        data={"stop_on_error": "true"},
        files=[
            ("files", ("one.txt", "ignored", "text/plain")),
            ("files", ("two.txt", "ignored", "text/plain")),
        ],
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1


def test_convert_stop_on_error_false_files_continue_after_conversion_error(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    call_count = {"value": 0}

    def fail_then_succeed_convert(_tac: str, iwxxm_version: str = "2025-2", **_kwargs: Any):
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise ConversionError("forced conversion failure")
        return f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>', None

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_then_succeed_convert)

    response = client.post(
        "/api/v1/convert",
        data={"stop_on_error": "false"},
        files=[
            ("files", ("one.txt", "ignored", "text/plain")),
            ("files", ("two.txt", "ignored", "text/plain")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 2
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "CONVERSION_ERROR" for issue in payload["issues"])


def test_convert_zip_manual_success_when_stats_logging_fails(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "manual_input.xml" in zip_data


def test_convert_zip_manual_conversion_error_log_failure_non_blocking(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    def fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced failure")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)

    response = client.post(
        "/api/v1/convert-zip",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "manual_input: forced failure" in zip_data["errors.txt"]


def test_convert_zip_json_metars_validation_service_error_branch(client, monkeypatch):
    class _ValidationErrorService:
        def validate_all_layers(self, _tac: str):
            raise api_module.ValidationServiceError("validation subsystem failed")

    monkeypatch.setattr(api_module, "ValidationService", _ValidationErrorService)

    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2025-2"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "validation subsystem failed" in zip_data["errors.txt"]


def test_convert_zip_manual_conversion_error_webhook_failure_branch(client, monkeypatch):
    class _WebhookFail(_FakeWebhookService):
        async def notify_translation_failed(self, **_kwargs: Any) -> None:
            raise RuntimeError("webhook down")

    def fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced failure")

    monkeypatch.setattr(api_module, "webhook_service", _WebhookFail())
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)

    response = client.post(
        "/api/v1/convert-zip",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "manual_input: forced failure" in zip_data["errors.txt"]


def test_convert_zip_file_success_logging_exception_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "sample.xml" in zip_data


def test_convert_zip_file_conversion_error_logging_exception_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    def fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced file failure")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "sample.txt: forced file failure" in zip_data["errors.txt"]


def test_convert_zip_file_unexpected_error_logging_exception_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    def fail_unexpected(*_args: Any, **_kwargs: Any):
        raise RuntimeError("forced file unexpected")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_unexpected)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "sample.txt: unexpected error forced file unexpected" in zip_data["errors.txt"]


def test_convert_zip_json_validation_service_error_logging_exception_branch(client, monkeypatch):
    class _ValidationErrorService:
        def validate_all_layers(self, _tac: str):
            raise api_module.ValidationServiceError("validation subsystem failed")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "ValidationService", _ValidationErrorService)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2025-2"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "validation subsystem failed" in zip_data["errors.txt"]


def test_convert_zip_json_metars_skips_blank_entries(client):
    response = client.post(
        "/api/v1/convert-zip",
        json={
            "metars": [
                "   ",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
        },
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "metar_2.xml" in zip_data


def test_convert_zip_file_conversion_error_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    def fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("file conversion failed")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)

    response = client.post(
        "/api/v1/convert-zip",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "sample.txt: file conversion failed" in zip_data["errors.txt"]


def test_convert_zip_file_unexpected_error_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    def fail_unexpected(*_args: Any, **_kwargs: Any):
        raise RuntimeError("unexpected conversion exception")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_unexpected)

    response = client.post(
        "/api/v1/convert-zip",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "sample.txt: unexpected error unexpected conversion exception" in zip_data["errors.txt"]


def test_convert_zip_bulk_webhook_failure_is_non_blocking(client, monkeypatch):
    class _WebhookBulkFail(_FakeWebhookService):
        async def notify_bulk_completed(self, **_kwargs: Any) -> None:
            raise RuntimeError("bulk webhook failed")

    monkeypatch.setattr(api_module, "webhook_service", _WebhookBulkFail())

    response = client.post(
        "/api/v1/convert-zip",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "manual_input.xml" in zip_data


def test_convert_zip_no_input_returns_400(client):
    response = client.post("/api/v1/convert-zip", data={})
    assert response.status_code == 400
    assert response.json()["detail"]["issues"][0]["code"] == "NO_INPUT"


def test_convert_zip_invalid_version_returns_400(client):
    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2099-9"},
    )
    assert response.status_code == 400
    assert "Invalid IWXXM version" in response.json()["detail"]["message"]


def test_convert_zip_file_success_path_logs_translation(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)

    response = client.post(
        "/api/v1/convert-zip",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "sample.xml" in zip_data


def test_convert_zip_json_validation_failed_logging_exception_branch(client, monkeypatch):
    class _ValidationFailService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            failed.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([failed])

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "ValidationService", _ValidationFailService)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2025-2"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "Validation failed" in zip_data["errors.txt"]


def test_convert_zip_json_success_logging_exception_branch(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2025-2"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "metar_1.xml" in zip_data


def test_convert_zip_json_conversion_error_logging_exception_branch(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    def fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("conversion failure")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)

    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2025-2"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "conversion failure" in zip_data["errors.txt"]


def test_convert_zip_json_unexpected_error_logging_exception_branch(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    def fail_unexpected(*_args: Any, **_kwargs: Any):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_unexpected)

    response = client.post(
        "/api/v1/convert-zip",
        json={"metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"], "version": "2025-2"},
    )

    assert response.status_code == 200
    zip_data = _read_zip_payload(response.content)
    assert "errors.txt" in zip_data
    assert "unexpected error unexpected failure" in zip_data["errors.txt"]
