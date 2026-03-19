"""Unit tests for validation router helpers and handlers."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from src.routers import validation as validation_router
from src.schemas.validation import (
    AggregatedValidationResult,
    ValidationLayer,
    ValidationResult,
)


def _aggregated_result(*, passed: bool, layer: ValidationLayer, execution_time_ms: float) -> AggregatedValidationResult:
    return AggregatedValidationResult.from_results([
        ValidationResult(
            passed=passed,
            layer=layer,
            issues=[],
            execution_time_ms=execution_time_ms,
        )
    ])


class TestGetValidationService:
    def test_get_validation_service_caches_instance(self, monkeypatch):
        created = []

        class FakeValidationService:
            def __init__(self):
                created.append(self)

        monkeypatch.setattr(validation_router, "ValidationService", FakeValidationService)
        monkeypatch.setattr(validation_router, "_validation_service", None)

        first = validation_router.get_validation_service()
        second = validation_router.get_validation_service()

        assert first is second
        assert len(created) == 1


class TestValidateContent:
    @pytest.mark.asyncio
    async def test_validate_content_returns_service_result(self, monkeypatch):
        expected = _aggregated_result(
            passed=True,
            layer=ValidationLayer.TAC_SYNTAX,
            execution_time_ms=4.2,
        )

        class FakeService:
            def validate_all_layers(self, tac_text):
                assert tac_text == "METAR TEST"
                return expected

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.ValidationRequest(content="METAR TEST", content_type="tac")

        result = await validation_router.validate_content(request, user={"sub": "user-1"})

        assert result == expected

    @pytest.mark.asyncio
    async def test_validate_content_maps_value_error_to_400(self, monkeypatch):
        class FakeService:
            def validate_all_layers(self, tac_text):
                raise ValueError(f"bad input: {tac_text}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.ValidationRequest(content="BAD", content_type="tac")

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request, user={"sub": "user-1"})

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "bad input: BAD"

    @pytest.mark.asyncio
    async def test_validate_content_maps_unexpected_error_to_500(self, monkeypatch):
        class FakeService:
            def validate_all_layers(self, tac_text):
                raise RuntimeError(f"boom: {tac_text}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.ValidationRequest(content="BAD", content_type="tac")

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request, user={"sub": "user-1"})

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Validation error: boom: BAD"


class TestValidateMultiple:
    @pytest.mark.asyncio
    async def test_validate_multiple_aggregates_counts_and_time(self, monkeypatch):
        responses = [
            _aggregated_result(passed=True, layer=ValidationLayer.AIRPORT_ICAO, execution_time_ms=5.0),
            _aggregated_result(passed=False, layer=ValidationLayer.TAC_SYNTAX, execution_time_ms=7.5),
        ]

        class FakeService:
            def validate_all_layers(self, tac_text):
                assert tac_text in {"METAR ONE", "METAR TWO"}
                return responses.pop(0)

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.BatchValidationRequest(
            items=[
                validation_router.ValidationRequest(content="METAR ONE", content_type="tac"),
                validation_router.ValidationRequest(content="METAR TWO", content_type="tac"),
            ],
            layers=[ValidationLayer.TAC_SYNTAX],
        )

        result = await validation_router.validate_multiple(request, user={"sub": "user-1"})

        assert result.total_items == 2
        assert result.passed_items == 1
        assert result.failed_items == 1
        assert result.total_execution_time_ms == 12.5
        assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_validate_multiple_maps_value_error_to_400(self, monkeypatch):
        class FakeService:
            def validate_all_layers(self, tac_text):
                raise ValueError(f"bad batch item: {tac_text}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.BatchValidationRequest(
            items=[validation_router.ValidationRequest(content="BAD", content_type="tac")]
        )

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_multiple(request, user={"sub": "user-1"})

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "bad batch item: BAD"

    @pytest.mark.asyncio
    async def test_validate_multiple_maps_unexpected_error_to_500(self, monkeypatch):
        class FakeService:
            def validate_all_layers(self, tac_text):
                raise RuntimeError(f"explode: {tac_text}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.BatchValidationRequest(
            items=[validation_router.ValidationRequest(content="BAD", content_type="tac")]
        )

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_multiple(request, user={"sub": "user-1"})

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Batch validation error: explode: BAD"


class TestGetValidationLayers:
    @pytest.mark.asyncio
    async def test_get_validation_layers_returns_expected_layer_metadata(self):
        response = await validation_router.get_validation_layers(user={"sub": "user-1"})

        assert len(response.layers) == 7
        assert response.layers[0].layer == ValidationLayer.AIRPORT_ICAO
        assert response.layers[0].blocking is True
        assert response.layers[0].supported_content_types == ["tac"]
        assert response.layers[-1].layer == ValidationLayer.WMO_CODELISTS
        assert response.layers[-1].supported_content_types == ["xml"]
