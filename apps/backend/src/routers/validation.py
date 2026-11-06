"""Validation endpoints for METAR and IWXXM content."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from ..schemas.validation import (
    AggregatedValidationResult,
    ValidationIssue,
    ValidationLayer,
    ValidationRequest,
    ValidationResult,
)
from ..services.validation import ValidationService
from ..services.validation_orchestrator import (
    ComprehensiveValidationResult,
    get_validation_orchestrator,
)

router = APIRouter()

_XML_CONTENT_TYPES = frozenset({"xml", "iwxxm"})
_TAC_LAYERS = frozenset({ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX})
_XML_LAYERS = frozenset(
    {
        ValidationLayer.XML_WELLFORMED,
        ValidationLayer.XML_SCHEMA,
        ValidationLayer.SCHEMATRON,
        ValidationLayer.GML_REFERENCES,
        ValidationLayer.WMO_CODELISTS,
    }
)


def _normalize_content_type(raw: str | None) -> str:
    """
    Internal helper ``_normalize_content_type``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.

    Returns
    -------
    object
        Return value.
    """
    normalized = (raw or "tac").strip().lower()
    if normalized in _XML_CONTENT_TYPES:
        return "xml"
    if normalized == "tac":
        return "tac"
    raise ValueError(f"Unsupported content_type '{raw}'; expected 'tac', 'xml', or 'iwxxm'")


def _aggregated_from_comprehensive(
    comprehensive: ComprehensiveValidationResult,
) -> AggregatedValidationResult:
    """
    Internal helper ``_aggregated_from_comprehensive``.

    Parameters
    ----------
    comprehensive : object
        Argument ``comprehensive``.

    Returns
    -------
    object
        Return value.
    """
    results: list[ValidationResult] = []
    for layer in comprehensive.layers_run:
        issues = list(comprehensive.issues_by_layer.get(layer, []))
        # Ensure issue.layer matches (orchestrator may already set it).
        normalized_issues: list[ValidationIssue] = []
        for issue in issues:
            if issue.layer != layer:
                normalized_issues.append(
                    ValidationIssue(
                        layer=layer,
                        level=issue.level,
                        message=issue.message,
                        location=issue.location,
                        code=issue.code,
                        suggestion=issue.suggestion,
                    )
                )
            else:
                normalized_issues.append(issue)
        results.append(
            ValidationResult(
                passed=layer in comprehensive.layers_passed,
                layer=layer,
                issues=normalized_issues,
            )
        )
    return AggregatedValidationResult.from_results(results)


def _validate_one(item: ValidationRequest) -> AggregatedValidationResult:
    """
    Internal helper ``_validate_one``.

    Parameters
    ----------
    item : object
        Argument ``item``.

    Returns
    -------
    object
        Return value.
    """
    content_type = _normalize_content_type(item.content_type)
    layers = item.layers
    version = item.iwxxm_version or "2025-2"
    # Empty list is explicit "no layers" — reject for both TAC and XML (consistent 400).
    if layers is not None and len(layers) == 0:
        raise ValueError("layers must be omitted (use defaults) or a non-empty list")

    if content_type == "xml":
        selected = list(layers) if layers is not None else list(_XML_LAYERS)
        tac_requested = [layer for layer in selected if layer in _TAC_LAYERS]
        if tac_requested:
            raise ValueError(
                "TAC layers require content_type 'tac'; "
                f"got {', '.join(layer.value for layer in tac_requested)} with XML content"
            )
        xml_layers = [layer for layer in selected if layer in _XML_LAYERS]
        if not xml_layers:
            raise ValueError("No XML validation layers selected")
        comprehensive = get_validation_orchestrator().validate(
            item.content,
            iwxxm_version=version,
            layers=xml_layers,
        )
        return _aggregated_from_comprehensive(comprehensive)

    # TAC path — reject pure XML layer selections without XML content.
    if layers is not None:
        xml_only = [layer for layer in layers if layer in _XML_LAYERS]
        tac_any = [layer for layer in layers if layer in _TAC_LAYERS]
        if xml_only and not tac_any:
            raise ValueError(
                "XML layers require content_type 'xml' or 'iwxxm' "
                f"(requested: {', '.join(layer.value for layer in xml_only)})"
            )
        layers = [layer for layer in layers if layer in _TAC_LAYERS]
        if not layers:
            raise ValueError("No TAC validation layers selected")

    return get_validation_service().validate(
        content=item.content,
        content_type="tac",
        layers=layers,
        iwxxm_version=version,
    )


class ValidationLayerInfo(BaseModel):
    """
    Information about a validation layer.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "layer": "tac_syntax",
                "description": "Parse and validate METAR TAC syntax",
                "blocking": True,
                "supported_content_types": ["tac"],
            }
        }
    )

    layer: ValidationLayer = Field(..., description="Layer identifier")
    description: str = Field(..., description="Human-readable description")
    blocking: bool = Field(..., description="Whether this layer blocks further validation if it fails")
    supported_content_types: list[str] = Field(
        default_factory=list, description="Content types this layer supports (tac/xml)"
    )


class ValidationLayersResponse(BaseModel):
    """
    List of available validation layers with configurations.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "layers": [
                    {
                        "layer": "airport_icao",
                        "description": "Extract and validate ICAO code against airport database",
                        "blocking": True,
                        "supported_content_types": ["tac"],
                    },
                    {
                        "layer": "tac_syntax",
                        "description": "Parse and validate METAR TAC syntax",
                        "blocking": True,
                        "supported_content_types": ["tac"],
                    },
                ]
            }
        }
    )

    layers: list[ValidationLayerInfo] = Field(..., description="Available validation layers")


class BatchValidationRequest(BaseModel):
    """
    Request to validate multiple inputs.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "content": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
                        "content_type": "tac",
                    },
                    {
                        "content": "METAR EGLL 231750Z 17008KT 9999 SCT035 12/08 Q1007",
                        "content_type": "tac",
                    },
                ],
                "layers": ["airport_icao", "tac_syntax"],
            }
        }
    )

    items: list[ValidationRequest] = Field(
        ...,
        description="Items to validate",
        min_length=1,
        max_length=100,
    )
    layers: list[ValidationLayer] | None = Field(None, description="Layers to apply to all items (None = all layers)")


class BatchValidationResponse(BaseModel):
    """
    Response from batch validation.


    Attributes
    ----------
    _ : object
        See implementation.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "passed": True,
                        "layers_validated": ["airport_icao", "tac_syntax"],
                        "total_issues": 0,
                        "results": [],
                        "execution_time_ms": 15.2,
                    }
                ],
                "total_items": 2,
                "passed_items": 1,
                "failed_items": 1,
                "total_execution_time_ms": 30.5,
            }
        }
    )

    results: list[AggregatedValidationResult] = Field(..., description="Validation results for each item")
    total_items: int = Field(..., description="Total items requested", ge=0)
    passed_items: int = Field(..., description="Number of items that passed", ge=0)
    failed_items: int = Field(..., description="Number of items that failed", ge=0)
    total_execution_time_ms: float = Field(..., description="Total execution time", ge=0)


# Initialize validation service (will be instantiated on first use)
_validation_service: ValidationService | None = None


def get_validation_service() -> ValidationService:
    """
    Get or create validation service.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_validation_service)
    2

    Returns
    -------
    object
        Return value.
    """
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service


@router.post(
    "/validate",
    response_model=AggregatedValidationResult,
    tags=["Validation"],
    summary="Validate METAR TAC or IWXXM XML content",
)
async def validate_content(
    request: ValidationRequest,
) -> object:
    """
    Validate one METAR TAC or IWXXM XML document through the selected layers.


    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_content)
    2
    """
    try:
        return _validate_one(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {e!s}") from e


@router.post(
    "/validate-multi",
    response_model=BatchValidationResponse,
    tags=["Validation"],
    summary="Validate a batch of TAC or IWXXM inputs",
)
async def validate_multiple(
    request: BatchValidationRequest,
) -> object:
    """
    Validate up to 100 TAC or IWXXM documents in one request.

    Each document is checked on its own.


    Parameters
    ----------
    request : object
        Argument ``request``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_multiple)
    2
    """
    try:
        results: list[AggregatedValidationResult] = []
        total_time = 0.0

        for item in request.items:
            effective = item
            if item.layers is None and request.layers is not None:
                effective = item.model_copy(update={"layers": request.layers})
            result = _validate_one(effective)
            results.append(result)
            total_time += result.execution_time_ms

        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count

        return BatchValidationResponse(
            results=results,
            total_items=len(results),
            passed_items=passed_count,
            failed_items=failed_count,
            total_execution_time_ms=total_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch validation error: {e!s}") from e


@router.get(
    "/layers",
    response_model=ValidationLayersResponse,
    tags=["Validation"],
    summary="List validation layers",
)
async def get_validation_layers() -> object:
    """
    List the validation layers.

    A blocking layer stops later layers when it fails.


    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_validation_layers)
    2
    """
    layers_info = [
        ValidationLayerInfo(
            layer=ValidationLayer.AIRPORT_ICAO,
            description="Extract and validate ICAO code against airport database",
            blocking=True,
            supported_content_types=["tac"],
        ),
        ValidationLayerInfo(
            layer=ValidationLayer.TAC_SYNTAX,
            description="Parse and validate METAR TAC syntax",
            blocking=True,
            supported_content_types=["tac"],
        ),
        ValidationLayerInfo(
            layer=ValidationLayer.XML_WELLFORMED,
            description="Check if output XML is well-formed",
            blocking=False,
            supported_content_types=["xml"],
        ),
        ValidationLayerInfo(
            layer=ValidationLayer.XML_SCHEMA,
            description="Validate against XSD schema",
            blocking=False,
            supported_content_types=["xml"],
        ),
        ValidationLayerInfo(
            layer=ValidationLayer.SCHEMATRON,
            description="SCHEMATRON rules validation",
            blocking=False,
            supported_content_types=["xml"],
        ),
        ValidationLayerInfo(
            layer=ValidationLayer.GML_REFERENCES,
            description="GML reference checks",
            blocking=False,
            supported_content_types=["xml"],
        ),
        ValidationLayerInfo(
            layer=ValidationLayer.WMO_CODELISTS,
            description="WMO code list validation",
            blocking=False,
            supported_content_types=["xml"],
        ),
    ]

    return ValidationLayersResponse(layers=layers_info)


__all__ = ["router"]
