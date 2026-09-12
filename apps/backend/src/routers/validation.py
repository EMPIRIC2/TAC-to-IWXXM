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
    """Return canonical content type: ``tac`` or ``xml``."""
    normalized = (raw or "tac").strip().lower()
    if normalized in _XML_CONTENT_TYPES:
        return "xml"
    if normalized == "tac":
        return "tac"
    raise ValueError(f"Unsupported content_type '{raw}'; expected 'tac', 'xml', or 'iwxxm'")


def _aggregated_from_comprehensive(
    comprehensive: ComprehensiveValidationResult,
) -> AggregatedValidationResult:
    """Map orchestrator output onto the AggregatedValidationResult HTTP shape."""
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
    """Validate a single item, honoring ``content_type`` and ``layers``."""
    content_type = _normalize_content_type(item.content_type)
    layers = item.layers
    version = item.iwxxm_version or "2025-2"

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
        layers = [layer for layer in layers if layer in _TAC_LAYERS] or None

    return get_validation_service().validate(
        content=item.content,
        content_type="tac",
        layers=layers,
        iwxxm_version=version,
    )


class ValidationLayerInfo(BaseModel):
    """Information about a validation layer."""

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
    """List of available validation layers with configurations."""

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
    """Request to validate multiple inputs."""

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
    """Response from batch validation."""

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
    """Get or create validation service."""
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
    """Validate METAR TAC or IWXXM XML content through multiple validation layers.

    ## Request Body
    - **content** (string, required): The METAR TAC or IWXXM XML content to validate
    - **content_type** (string, default="tac"): ``tac``, ``xml``, or ``iwxxm`` (alias of xml)
    - **layers** (array, optional): Specific validation layers to run.
      - TAC (``content_type=tac``): ``airport_icao``, ``tac_syntax`` (default both)
      - XML (``content_type=xml|iwxxm``): ``xml_wellformed``, ``xml_schema``,
        ``schematron``, ``gml_references``, ``wmo_codelists`` (default all XML layers)
    - **iwxxm_version** (string, optional): IWXXM version for XML layers (e.g., "2025-2")

    ## Response
    Returns aggregated validation results with:
    - **passed** (boolean): Whether all requested layers passed
    - **layers_validated** (array): Layers that were run
    - **total_issues** (integer): Total validation issues found
    - **results** (array): Per-layer validation details
    - **execution_time_ms** (float): Total execution time

    ## Example Success Response
    ```json
    {
      "passed": true,
      "layers_validated": ["airport_icao", "tac_syntax"],
      "total_issues": 0,
      "results": [
        {
          "passed": true,
          "layer": "airport_icao",
          "issues": [],
          "execution_time_ms": 5.2
        }
      ],
      "execution_time_ms": 10.5
    }
    ```

    ## Example Failure Response
    ```json
    {
      "passed": false,
      "layers_validated": ["airport_icao", "tac_syntax"],
      "total_issues": 1,
      "results": [
        {
          "passed": false,
          "layer": "tac_syntax",
          "issues": [
            {
              "layer": "tac_syntax",
              "level": "error",
              "message": "Invalid TAC format",
              "code": "INVALID_TAC_FORMAT"
            }
          ],
          "execution_time_ms": 8.3
        }
      ],
      "execution_time_ms": 8.3
    }
    ```
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
    summary="Validate multiple METAR TAC or IWXXM XML inputs",
)
async def validate_multiple(
    request: BatchValidationRequest,
) -> object:
    """Validate multiple METAR TAC or IWXXM XML inputs in a single request.

    Useful for batch validation of multiple entries. Each item is validated
    independently and can have different content types.

    ## Request Body
    - **items** (array, required): Array of validation requests (1-100 items)
      - Each item has: content, content_type, layers (optional), iwxxm_version (optional)
    - **layers** (array, optional): Default layers to apply to all items that omit layers

    ## Response
    Returns batch validation results with:
    - **results** (array): Aggregated validation result for each item
    - **total_items** (integer): Total items requested
    - **passed_items** (integer): Items that passed all layers
    - **failed_items** (integer): Items that failed at least one layer
    - **total_execution_time_ms** (float): Total execution time for all items

    ## Example Request
    ```json
    {
      "items": [
        {
          "content": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005",
          "content_type": "tac"
        },
        {
          "content": "METAR EGLL 231750Z 17008KT 9999 SCT035 12/08 Q1007",
          "content_type": "tac"
        }
      ],
      "layers": ["airport_icao", "tac_syntax"]
    }
    ```

    ## Example Response
    ```json
    {
      "results": [
        {
          "passed": true,
          "layers_validated": ["airport_icao", "tac_syntax"],
          "total_issues": 0,
          "results": [],
          "execution_time_ms": 12.3
        },
        {
          "passed": false,
          "layers_validated": ["airport_icao", "tac_syntax"],
          "total_issues": 1,
          "results": [],
          "execution_time_ms": 8.5
        }
      ],
      "total_items": 2,
      "passed_items": 1,
      "failed_items": 1,
      "total_execution_time_ms": 20.8
    }
    ```
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
    summary="Get available validation layers",
)
async def get_validation_layers() -> object:
    """Get information about available validation layers.

    Each layer validates specific aspects of METAR TAC or IWXXM XML content.
    Layers marked as blocking will stop further validation if they fail.

    ## Response
    Returns list of validation layers with:
    - **layer**: Layer identifier
    - **description**: What this layer validates
    - **blocking**: Whether it blocks further layers on failure
    - **supported_content_types**: Content types this layer supports ("tac" or "xml")

    ## Available Layers
    1. **airport_icao**: Extract and validate ICAO code against airport database
    2. **tac_syntax**: Parse and validate METAR TAC syntax
    3. **xml_wellformed**: Check if output XML is well-formed
    4. **xml_schema**: Validate against XSD schema
    5. **schematron**: SCHEMATRON rules validation
    6. **gml_references**: GML reference checks
    7. **wmo_codelists**: WMO code list validation

    ## Example Response
    ```json
    {
      "layers": [
        {
          "layer": "airport_icao",
          "description": "Extract and validate ICAO code against airport database",
          "blocking": true,
          "supported_content_types": ["tac"]
        },
        {
          "layer": "tac_syntax",
          "description": "Parse and validate METAR TAC syntax",
          "blocking": true,
          "supported_content_types": ["tac"]
        }
      ]
    }
    ```
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
