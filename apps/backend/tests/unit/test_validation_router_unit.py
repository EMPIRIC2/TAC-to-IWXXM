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
    return AggregatedValidationResult.from_results(
        [
            ValidationResult(
                passed=passed,
                layer=layer,
                issues=[],
                execution_time_ms=execution_time_ms,
            )
        ]
    )


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
            def validate(self, content, content_type="tac", layers=None, iwxxm_version=None):
                assert content == "METAR TEST"
                assert content_type == "tac"
                return expected

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.ValidationRequest(content="METAR TEST", content_type="tac")

        result = await validation_router.validate_content(request)

        assert result == expected

    @pytest.mark.asyncio
    async def test_validate_content_maps_value_error_to_400(self, monkeypatch):
        class FakeService:
            def validate(self, content, content_type="tac", layers=None, iwxxm_version=None):
                raise ValueError(f"bad input: {content}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.ValidationRequest(content="BAD", content_type="tac")

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "bad input: BAD"

    @pytest.mark.asyncio
    async def test_validate_content_maps_unexpected_error_to_500(self, monkeypatch):
        class FakeService:
            def validate(self, content, content_type="tac", layers=None, iwxxm_version=None):
                raise RuntimeError(f"boom: {content}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.ValidationRequest(content="BAD", content_type="tac")

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Validation error: boom: BAD"

    @pytest.mark.asyncio
    async def test_validate_content_xml_uses_orchestrator(self, monkeypatch):
        from src.services.validation_orchestrator import ComprehensiveValidationResult

        expected_layers = [ValidationLayer.XML_WELLFORMED, ValidationLayer.XML_SCHEMA]

        class FakeOrch:
            def validate(self, xml_content, *, iwxxm_version, layers=None):
                assert xml_content.startswith("<?xml")
                assert iwxxm_version == "2025-2"
                assert layers == expected_layers
                return ComprehensiveValidationResult(
                    is_valid=True,
                    layers_run=list(expected_layers),
                    layers_passed=list(expected_layers),
                    layers_failed=[],
                    all_issues=[],
                    issues_by_layer={},
                    version=iwxxm_version,
                )

        monkeypatch.setattr(validation_router, "get_validation_orchestrator", lambda: FakeOrch())
        request = validation_router.ValidationRequest(
            content="<?xml version='1.0'?><iwxxm:METAR/>",
            content_type="iwxxm",
            layers=expected_layers,
            iwxxm_version="2025-2",
        )
        result = await validation_router.validate_content(request)
        assert result.passed is True
        assert result.layers_validated == expected_layers

    @pytest.mark.asyncio
    async def test_validate_content_rejects_xml_layers_on_tac(self):
        request = validation_router.ValidationRequest(
            content="METAR KJFK 010000Z 00000KT CAVOK",
            content_type="tac",
            layers=[ValidationLayer.XML_SCHEMA],
        )
        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request)
        assert exc_info.value.status_code == 400
        assert "xml" in str(exc_info.value.detail).lower()


class TestValidateMultiple:
    @pytest.mark.asyncio
    async def test_validate_multiple_aggregates_counts_and_time(self, monkeypatch):
        responses = [
            _aggregated_result(passed=True, layer=ValidationLayer.AIRPORT_ICAO, execution_time_ms=5.0),
            _aggregated_result(passed=False, layer=ValidationLayer.TAC_SYNTAX, execution_time_ms=7.5),
        ]

        class FakeService:
            def validate(self, content, content_type="tac", layers=None, iwxxm_version=None):
                assert content in {"METAR ONE", "METAR TWO"}
                return responses.pop(0)

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.BatchValidationRequest(
            items=[
                validation_router.ValidationRequest(content="METAR ONE", content_type="tac"),
                validation_router.ValidationRequest(content="METAR TWO", content_type="tac"),
            ],
            layers=[ValidationLayer.TAC_SYNTAX],
        )

        result = await validation_router.validate_multiple(request)

        assert result.total_items == 2
        assert result.passed_items == 1
        assert result.failed_items == 1
        assert result.total_execution_time_ms == 12.5
        assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_validate_multiple_maps_value_error_to_400(self, monkeypatch):
        class FakeService:
            def validate(self, content, content_type="tac", layers=None, iwxxm_version=None):
                raise ValueError(f"bad batch item: {content}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.BatchValidationRequest(
            items=[validation_router.ValidationRequest(content="BAD", content_type="tac")]
        )

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_multiple(request)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "bad batch item: BAD"

    @pytest.mark.asyncio
    async def test_validate_multiple_maps_unexpected_error_to_500(self, monkeypatch):
        class FakeService:
            def validate(self, content, content_type="tac", layers=None, iwxxm_version=None):
                raise RuntimeError(f"explode: {content}")

        monkeypatch.setattr(validation_router, "get_validation_service", lambda: FakeService())
        request = validation_router.BatchValidationRequest(
            items=[validation_router.ValidationRequest(content="BAD", content_type="tac")]
        )

        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_multiple(request)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Batch validation error: explode: BAD"


class TestGetValidationLayers:
    @pytest.mark.asyncio
    async def test_get_validation_layers_returns_expected_layer_metadata(self):
        response = await validation_router.get_validation_layers()

        assert len(response.layers) == 7
        assert response.layers[0].layer == ValidationLayer.AIRPORT_ICAO
        assert response.layers[0].blocking is True
        assert response.layers[0].supported_content_types == ["tac"]
        assert response.layers[-1].layer == ValidationLayer.WMO_CODELISTS
        assert response.layers[-1].supported_content_types == ["xml"]


class TestValidateHelpersCoverage:
    def test_normalize_content_type_rejects_unknown(self):
        with pytest.raises(ValueError, match="Unsupported content_type"):
            validation_router._normalize_content_type("pdf")

    def test_aggregated_from_comprehensive_rewrites_mismatched_issue_layer(self):
        from src.schemas.validation import ValidationIssue, ValidationLevel
        from src.services.validation_orchestrator import ComprehensiveValidationResult

        wrong = ValidationIssue(
            layer=ValidationLayer.TAC_SYNTAX,
            level=ValidationLevel.ERROR,
            message="mismatched",
            code="X",
        )
        comp = ComprehensiveValidationResult(
            is_valid=False,
            layers_run=[ValidationLayer.XML_WELLFORMED],
            layers_passed=[],
            layers_failed=[ValidationLayer.XML_WELLFORMED],
            all_issues=[wrong],
            issues_by_layer={ValidationLayer.XML_WELLFORMED: [wrong]},
            version="2025-2",
        )
        agg = validation_router._aggregated_from_comprehensive(comp)
        assert agg.results[0].layer == ValidationLayer.XML_WELLFORMED
        assert agg.results[0].issues[0].layer == ValidationLayer.XML_WELLFORMED

    def test_aggregated_from_comprehensive_keeps_matching_issue_layer(self):
        from src.schemas.validation import ValidationIssue, ValidationLevel
        from src.services.validation_orchestrator import ComprehensiveValidationResult

        matching = ValidationIssue(
            layer=ValidationLayer.XML_WELLFORMED,
            level=ValidationLevel.WARNING,
            message="ok layer",
            code="W",
        )
        comp = ComprehensiveValidationResult(
            is_valid=True,
            layers_run=[ValidationLayer.XML_WELLFORMED],
            layers_passed=[ValidationLayer.XML_WELLFORMED],
            layers_failed=[],
            all_issues=[matching],
            issues_by_layer={ValidationLayer.XML_WELLFORMED: [matching]},
            version="2025-2",
        )
        agg = validation_router._aggregated_from_comprehensive(comp)
        assert agg.results[0].issues[0] is matching

    @pytest.mark.asyncio
    async def test_validate_content_rejects_tac_layers_on_xml(self):
        request = validation_router.ValidationRequest(
            content="<?xml version='1.0'?><root/>",
            content_type="xml",
            layers=[ValidationLayer.AIRPORT_ICAO],
        )
        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request)
        assert exc_info.value.status_code == 400
        assert "TAC layers" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_content_rejects_empty_layers_for_xml_and_tac(self):
        for content_type, content in (
            ("xml", "<?xml version='1.0'?><root/>"),
            ("tac", "METAR KJFK 010000Z 00000KT CAVOK"),
        ):
            request = validation_router.ValidationRequest(
                content=content,
                content_type=content_type,
                layers=[],
            )
            with pytest.raises(HTTPException) as exc_info:
                await validation_router.validate_content(request)
            assert exc_info.value.status_code == 400
            assert "non-empty" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_validate_content_rejects_when_xml_layer_set_empty(self, monkeypatch):
        """Defensive path: selected layers exist but none map to _XML_LAYERS."""
        monkeypatch.setattr(validation_router, "_XML_LAYERS", frozenset())
        request = validation_router.ValidationRequest(
            content="<?xml version='1.0'?><root/>",
            content_type="xml",
            layers=[ValidationLayer.XML_WELLFORMED],
        )
        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request)
        assert exc_info.value.status_code == 400
        assert "No XML validation layers" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_content_rejects_when_tac_layer_set_empty(self, monkeypatch):
        """Defensive path: requested layers exist but none map to _TAC_LAYERS."""
        monkeypatch.setattr(validation_router, "_TAC_LAYERS", frozenset())
        request = validation_router.ValidationRequest(
            content="METAR KJFK 010000Z 00000KT CAVOK",
            content_type="tac",
            layers=[ValidationLayer.AIRPORT_ICAO],
        )
        with pytest.raises(HTTPException) as exc_info:
            await validation_router.validate_content(request)
        assert exc_info.value.status_code == 400
        assert "No TAC validation layers" in str(exc_info.value.detail)
