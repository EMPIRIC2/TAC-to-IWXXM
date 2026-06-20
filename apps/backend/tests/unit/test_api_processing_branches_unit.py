"""Additional API endpoint tests for JSON/metars and file-processing branches."""

from __future__ import annotations

import builtins
from types import SimpleNamespace
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


class _ValidationPassService:
    def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
        return AggregatedValidationResult.from_results(
            [ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)]
        )


@pytest.fixture
def client(monkeypatch):
    async def override_verify_token():
        return {"sub": "test-user", "aud": "test-aud"}

    def fake_convert(_tac: str, iwxxm_version: str = "2025-2", validate: bool = False, **_kwargs: Any):
        _ = validate
        xml = f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>'
        return xml, None

    monkeypatch.setattr(api_module, "ValidationService", _ValidationPassService)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)
    monkeypatch.setattr(api_module, "statistics_service", _FakeStatsService())
    monkeypatch.setattr(api_module, "webhook_service", _FakeWebhookService())

    api_module.app.dependency_overrides[verify_supabase_token] = override_verify_token
    test_client = TestClient(api_module.app)
    yield test_client
    api_module.app.dependency_overrides.clear()


def test_convert_json_metars_validation_service_error_continue(client, monkeypatch):
    class _ValidationErrorOnFirst:
        def __init__(self):
            self.calls = 0

        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            self.calls += 1
            if self.calls == 1:
                raise api_module.ValidationServiceError("validation subsystem failed")
            return AggregatedValidationResult.from_results(
                [ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)]
            )

    monkeypatch.setattr(api_module, "ValidationService", _ValidationErrorOnFirst)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 2
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "VALIDATION_SERVICE_ERROR" for issue in payload["issues"])


def test_convert_json_metars_conversion_error_stop_on_error(client, monkeypatch):
    def always_fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced conversion failure")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", always_fail_convert)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1
    assert detail["issues"][0]["code"] == "CONVERSION_ERROR"


def test_convert_json_metars_unexpected_error_issue(client, monkeypatch):
    call_count = {"value": 0}

    def flaky_convert(*_args: Any, **_kwargs: Any):
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise RuntimeError("unexpected failure")
        return "<iwxxm:METAR>ok</iwxxm:METAR>", None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", flaky_convert)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "UNEXPECTED_BACKEND_ERROR" for issue in payload["issues"])


def test_convert_file_processing_read_error_then_success(client, monkeypatch):
    async def fake_read_uploaded_text(upload_file):
        if (upload_file.filename or "").startswith("bad"):
            return None, "empty file"
        return "METAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013", None

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)

    response = client.post(
        "/api/v1/convert",
        data={"stop_on_error": "false"},
        files=[
            ("files", ("bad.txt", "ignored", "text/plain")),
            ("files", ("good.txt", "ignored", "text/plain")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 2
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "INVALID_INPUT_FILE" for issue in payload["issues"])


def test_convert_file_xml_validation_unavailable(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "<iwxxm:METAR/>", None

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: None)

    response = client.post(
        "/api/v1/convert",
        data={"validate_output": "true"},
        files=[("files", ("sample.xml", "ignored", "application/xml"))],
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "XML_VALIDATION_UNAVAILABLE"


def test_convert_file_output_validation_failed_warning(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    class _FailingOrchestrator:
        def validate_complete(self, **_kwargs: Any):
            raise RuntimeError("validator unavailable")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _FailingOrchestrator())

    response = client.post(
        "/api/v1/convert",
        data={"validate_output": "true"},
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert any(issue["code"] == "OUTPUT_VALIDATION_FAILED" for issue in payload["issues"])


def test_convert_json_metars_skips_blank_entries(client):
    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "   ",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_processed"] == 1
    assert payload["successful"] == 1


def test_convert_json_metars_validation_failed_stop_on_error(client, monkeypatch):
    class _ValidationFailService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            failed.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([failed])

    monkeypatch.setattr(api_module, "ValidationService", _ValidationFailService)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1
    assert any(issue["code"] == "VALIDATION_FAILED" for issue in detail["issues"])


def test_convert_json_metars_unhandled_error_path(client, monkeypatch):
    class _ValidationBoomService:
        def validate_all_layers(self, _tac: str):
            raise RuntimeError("boom")

    monkeypatch.setattr(api_module, "ValidationService", _ValidationBoomService)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert any(issue["code"] == "UNHANDLED_BACKEND_ERROR" for issue in detail["issues"])


def test_convert_manual_validate_output_warning_path(client, monkeypatch):
    fake_validation = SimpleNamespace(is_valid=False, all_issues=["x"])

    def fake_convert(_tac: str, iwxxm_version: str = "2025-2", validate: bool = False, **_kwargs: Any):
        _ = (iwxxm_version, validate)
        return "<iwxxm:METAR>ok</iwxxm:METAR>", fake_validation

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            "validate_output": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert any(issue["code"] == "OUTPUT_VALIDATION_WARNING" for issue in payload["issues"])


def test_convert_json_metars_success_when_stats_logging_fails(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1


def test_convert_json_metars_validation_and_logging_exceptions_continue(client, monkeypatch):
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
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert any(issue["code"] == "VALIDATION_FAILED" for issue in detail["issues"])


def test_convert_json_metars_validation_service_error_logging_exception_breaks(client, monkeypatch):
    class _ValidationServiceErr:
        def validate_all_layers(self, _tac: str):
            raise api_module.ValidationServiceError("validation subsystem failed")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "ValidationService", _ValidationServiceErr)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1
    assert detail["issues"][0]["code"] == "VALIDATION_SERVICE_ERROR"


def test_convert_manual_success_logging_exception_non_blocking(client, monkeypatch):
    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1


def test_convert_file_output_validation_warning_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    class _WarnValidationOrchestrator:
        def validate_complete(self, **_kwargs: Any):
            return SimpleNamespace(is_valid=False, all_issues=["warn-1"])

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _WarnValidationOrchestrator())

    response = client.post(
        "/api/v1/convert",
        data={"validate_output": "true"},
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert any(issue["code"] == "OUTPUT_VALIDATION_WARNING" for issue in payload["issues"])


def test_convert_file_conversion_error_logging_exception_non_blocking(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    def fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced conversion failure")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_convert)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert",
        data={"stop_on_error": "false"},
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "CONVERSION_ERROR"


def test_convert_file_unexpected_error_logging_exception_non_blocking(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    def fail_unexpected(*_args: Any, **_kwargs: Any):
        raise RuntimeError("forced unexpected failure")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_unexpected)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert",
        data={"stop_on_error": "false"},
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "UNEXPECTED_BACKEND_ERROR"


def test_convert_manual_validation_service_error_continues(client, monkeypatch):
    class _ValidationErrorOnFirst:
        def __init__(self):
            self.calls = 0

        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            self.calls += 1
            if self.calls == 1:
                raise api_module.ValidationServiceError("manual validation failed")
            return AggregatedValidationResult.from_results(
                [ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)]
            )

    monkeypatch.setattr(api_module, "ValidationService", _ValidationErrorOnFirst)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": (
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013\nMETAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013"
            ),
            "stop_on_error": "false",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "VALIDATION_SERVICE_ERROR" for issue in payload["issues"])


def test_convert_manual_conversion_error_continue_to_next_entry(client, monkeypatch):
    call_count = {"value": 0}

    def fail_once_convert(_tac: str, iwxxm_version: str = "2025-2", **_kwargs: Any):
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise ConversionError("manual conversion boom")
        return f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>', None

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_once_convert)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": (
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013\nMETAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013"
            ),
            "stop_on_error": "false",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "CONVERSION_ERROR" for issue in payload["issues"])


def test_convert_files_validation_service_error_stop_on_error_breaks(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    class _AlwaysValidationError:
        def validate_all_layers(self, _tac: str):
            raise api_module.ValidationServiceError("validation subsystem down")

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "ValidationService", _AlwaysValidationError)

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
    assert detail["issues"][0]["code"] == "VALIDATION_SERVICE_ERROR"


def test_convert_files_unexpected_error_continue(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    call_count = {"value": 0}

    def fail_once_convert(_tac: str, iwxxm_version: str = "2025-2", **_kwargs: Any):
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise RuntimeError("file conversion exploded")
        return f'<iwxxm:METAR version="{iwxxm_version}">ok</iwxxm:METAR>', None

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fail_once_convert)

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
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert any(issue["code"] == "UNEXPECTED_BACKEND_ERROR" for issue in payload["issues"])


def test_convert_manual_validation_failed_branch_continue(client, monkeypatch):
    class _ValidationFailService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            failed.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([failed])

    monkeypatch.setattr(api_module, "ValidationService", _ValidationFailService)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": (
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013\nMETAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013"
            ),
            "stop_on_error": "false",
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 2
    assert any(issue["code"] == "VALIDATION_FAILED" for issue in detail["issues"])


def test_convert_file_validation_failed_branch(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", None

    class _ValidationFailService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            failed.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([failed])

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "ValidationService", _ValidationFailService)

    response = client.post(
        "/api/v1/convert",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["issues"][0]["code"] == "VALIDATION_FAILED"


def test_convert_file_read_error_stop_on_error_breaks(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return None, "empty file"

    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)

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
    assert detail["issues"][0]["code"] == "INVALID_INPUT_FILE"


def test_convert_manual_validate_output_true_path_adds_all_layers(client, monkeypatch):
    fake_validation = SimpleNamespace(is_valid=True, all_issues=[])

    def fake_convert(_tac: str, iwxxm_version: str = "2025-2", validate: bool = False, **_kwargs: Any):
        _ = (iwxxm_version, validate)
        return "<iwxxm:METAR>ok</iwxxm:METAR>", fake_validation

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", fake_convert)

    response = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            "validate_output": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert payload["failed"] == 0


def test_convert_json_validate_output_uses_orchestrator_validate_pass(client, monkeypatch):
    class _StatsCapture:
        def __init__(self):
            self.calls = []

        async def log_translation(self, **kwargs: Any) -> str:
            self.calls.append(kwargs)
            return "tid-1"

    class _Orchestrator:
        def validate(self, *_args: Any, **_kwargs: Any):
            return SimpleNamespace(passed=True)

    stats = _StatsCapture()
    monkeypatch.setattr(api_module, "statistics_service", stats)
    monkeypatch.setattr(api_module, "get_validation_orchestrator", lambda: _Orchestrator())

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013"],
            "version": "2025-2",
            "validation_level": "schema",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 200
    assert stats.calls
    layers = stats.calls[0]["validation_layers_passed"]
    assert ValidationLayer.XML_WELLFORMED in layers
    assert ValidationLayer.XML_SCHEMA in layers
    assert ValidationLayer.SCHEMATRON in layers
    assert ValidationLayer.GML_REFERENCES in layers
    assert ValidationLayer.WMO_CODELISTS in layers


def test_convert_json_conversion_error_logging_exception_stop_on_error(client, monkeypatch):
    def always_fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced conversion failure")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", always_fail_convert)
    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["total_errors"] == 1


def test_convert_json_unexpected_error_stop_on_error_breaks(client, monkeypatch):
    def always_boom(*_args: Any, **_kwargs: Any):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", always_boom)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": [
                "METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013",
                "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013",
            ],
            "version": "2025-2",
            "stop_on_error": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["total_errors"] == 1


def test_convert_manual_validation_logging_exceptions_stop_on_error(client, monkeypatch):
    class _ValidationFailService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO)
            failed.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([failed])

    class _ValidationErrorService:
        def validate_all_layers(self, _tac: str):
            raise api_module.ValidationServiceError("manual validation failed")

    class _BadStatsService:
        async def log_translation(self, **_kwargs: Any) -> str:
            raise RuntimeError("stats down")

    monkeypatch.setattr(api_module, "statistics_service", _BadStatsService())

    # First hit validation-failed + logging exception path.
    monkeypatch.setattr(api_module, "ValidationService", _ValidationFailService)
    response1 = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013\nMETAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013",
            "stop_on_error": "true",
        },
    )

    assert response1.status_code == 400
    assert response1.json()["detail"]["total_errors"] == 1

    # Then hit validation-service-error + logging exception path.
    monkeypatch.setattr(api_module, "ValidationService", _ValidationErrorService)
    response2 = client.post(
        "/api/v1/convert",
        data={
            "manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013\nMETAR KLAX 010000Z 00000KT CAVOK 10/08 Q1013",
            "stop_on_error": "true",
        },
    )

    assert response2.status_code == 400
    assert response2.json()["detail"]["total_errors"] == 1


def test_convert_and_convert_zip_version_import_fallback(client, monkeypatch):
    """Cover fallback imports in version resolution for /convert and /convert-zip."""
    original_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "src.config.iwxxm_versions":
            raise ImportError("force fallback")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)

    convert_response = client.post(
        "/api/v1/convert",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", "iwxxm_version": "2025-2"},
    )
    assert convert_response.status_code == 200

    zip_response = client.post(
        "/api/v1/convert-zip",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013", "iwxxm_version": "2025-2"},
    )
    assert zip_response.status_code == 200


class _CaptureWebhookService:
    def __init__(self):
        self.success_calls = []
        self.failed_calls = []
        self.completed_calls = []

    async def notify_translation_success(
        self,
        translation_id: str,
        airport_code: str,
        icao_region: str,
        iwxxm_version: str,
        duration_ms: int,
    ) -> None:
        self.success_calls.append(
            {
                "translation_id": translation_id,
                "airport_code": airport_code,
                "icao_region": icao_region,
                "iwxxm_version": iwxxm_version,
                "duration_ms": duration_ms,
            }
        )

    async def notify_translation_failed(
        self,
        translation_id: str,
        airport_code: str,
        error_type: str,
        error_message: str,
    ) -> None:
        self.failed_calls.append(
            {
                "translation_id": translation_id,
                "airport_code": airport_code,
                "error_type": error_type,
                "error_message": error_message,
            }
        )

    async def notify_translation_completed(
        self,
        translation_id: str,
        airport_code: str,
        iwxxm_version: str,
        file_size_bytes: int,
        duration_ms: int,
    ) -> None:
        self.completed_calls.append(
            {
                "translation_id": translation_id,
                "airport_code": airport_code,
                "iwxxm_version": iwxxm_version,
                "file_size_bytes": file_size_bytes,
                "duration_ms": duration_ms,
            }
        )


def test_convert_manual_success_emits_translation_success_notification(client, monkeypatch):
    capture = _CaptureWebhookService()
    monkeypatch.setattr(api_module, "webhook_service", capture)
    monkeypatch.setattr(api_module, "get_icao_region", lambda _icao: "NAM")

    response = client.post(
        "/api/v1/convert",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert len(capture.success_calls) == 1
    assert len(capture.failed_calls) == 0
    assert len(capture.completed_calls) == 0

    call = capture.success_calls[0]
    assert call["translation_id"] == "test-translation-id"
    assert call["airport_code"] == "KJFK"
    assert call["icao_region"] == "NAM"
    assert call["iwxxm_version"] == "2025-2"
    assert call["duration_ms"] >= 0


def test_convert_manual_validation_failure_emits_translation_failed_notification(client, monkeypatch):
    class _ValidationFailService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            failed = ValidationResult(passed=False, layer=ValidationLayer.AIRPORT_ICAO)
            failed.add_issue(level="error", message="bad tac", code="BAD_TAC")
            return AggregatedValidationResult.from_results([failed])

    capture = _CaptureWebhookService()
    monkeypatch.setattr(api_module, "ValidationService", _ValidationFailService)
    monkeypatch.setattr(api_module, "webhook_service", capture)

    response = client.post(
        "/api/v1/convert",
        data={"manual_text": "METAR KJFK 010000Z 00000KT CAVOK 10/08 Q1013"},
    )

    assert response.status_code == 400
    assert len(capture.failed_calls) == 1
    assert len(capture.success_calls) == 0
    assert len(capture.completed_calls) == 0

    call = capture.failed_calls[0]
    assert call["translation_id"] == "test-translation-id"
    assert call["airport_code"] == "KJFK"
    assert call["error_type"] == "validation_failed"
    assert "validation issue" in call["error_message"]


def test_convert_json_success_emits_translation_completed_notification(client, monkeypatch):
    capture = _CaptureWebhookService()
    monkeypatch.setattr(api_module, "webhook_service", capture)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013"],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert len(capture.completed_calls) == 1
    assert len(capture.success_calls) == 0
    assert len(capture.failed_calls) == 0

    call = capture.completed_calls[0]
    assert call["translation_id"] == "test-translation-id"
    assert call["airport_code"] == "KDEN"
    assert call["iwxxm_version"] == "2025-2"
    assert call["file_size_bytes"] > 0
    assert call["duration_ms"] >= 0


def test_convert_file_success_emits_translation_success_notification(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    capture = _CaptureWebhookService()
    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "webhook_service", capture)
    monkeypatch.setattr(api_module, "get_icao_region", lambda _icao: "PAC")

    response = client.post(
        "/api/v1/convert",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] == 1
    assert len(capture.success_calls) == 1
    assert len(capture.failed_calls) == 0
    assert len(capture.completed_calls) == 0

    call = capture.success_calls[0]
    assert call["translation_id"] == "test-translation-id"
    assert call["airport_code"] == "KSEA"
    assert call["icao_region"] == "PAC"
    assert call["iwxxm_version"] == "2025-2"


def test_convert_json_conversion_error_emits_translation_failed_notification(client, monkeypatch):
    def always_fail_convert(*_args: Any, **_kwargs: Any):
        raise ConversionError("forced conversion failure")

    capture = _CaptureWebhookService()
    monkeypatch.setattr(api_module, "convert_metar_tac_with_metadata", always_fail_convert)
    monkeypatch.setattr(api_module, "webhook_service", capture)

    response = client.post(
        "/api/v1/convert",
        json={
            "metars": ["METAR KDEN 010000Z 00000KT CAVOK 10/08 Q1013"],
            "version": "2025-2",
            "stop_on_error": False,
        },
    )

    assert response.status_code == 400
    assert len(capture.failed_calls) == 1
    assert len(capture.success_calls) == 0
    assert len(capture.completed_calls) == 0

    call = capture.failed_calls[0]
    assert call["translation_id"] == "unknown"
    assert call["airport_code"] == "KDEN"
    assert call["error_type"] == "conversion_error"
    assert "forced conversion failure" in call["error_message"]


def test_convert_file_validation_service_error_emits_translation_failed_notification(client, monkeypatch):
    async def fake_read_uploaded_text(_upload_file):
        return "METAR KSEA 010000Z 00000KT CAVOK 10/08 Q1013", None

    class _ValidationErrorService:
        def validate_all_layers(self, _tac: str) -> AggregatedValidationResult:
            raise api_module.ValidationServiceError("validation service unavailable")

    capture = _CaptureWebhookService()
    monkeypatch.setattr(api_module, "read_uploaded_text", fake_read_uploaded_text)
    monkeypatch.setattr(api_module, "ValidationService", _ValidationErrorService)
    monkeypatch.setattr(api_module, "webhook_service", capture)

    response = client.post(
        "/api/v1/convert",
        files=[("files", ("sample.txt", "ignored", "text/plain"))],
    )

    assert response.status_code == 400
    assert len(capture.failed_calls) == 1
    call = capture.failed_calls[0]
    assert call["translation_id"] == "test-translation-id"
    assert call["airport_code"] == "KSEA"
    assert call["error_type"] == "validation_error"
    assert "validation service unavailable" in call["error_message"]
