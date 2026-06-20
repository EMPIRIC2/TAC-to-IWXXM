"""Validation endpoints for METAR and IWXXM content."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from ..schemas.validation import (
    AggregatedValidationResult,
    ValidationLayer,
    ValidationRequest,
)
from ..services.validation import ValidationService
from ..utilities.security import verify_supabase_token

router = APIRouter()


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
    supported_content_types: List[str] = Field(
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

    layers: List[ValidationLayerInfo] = Field(..., description="Available validation layers")


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

    items: List[ValidationRequest] = Field(
        ...,
        description="Items to validate",
        min_length=1,
        max_length=100,
    )
    layers: Optional[List[ValidationLayer]] = Field(
        None, description="Layers to apply to all items (None = all layers)"
    )


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

    results: List[AggregatedValidationResult] = Field(..., description="Validation results for each item")
    total_items: int = Field(..., description="Total items requested", ge=0)
    passed_items: int = Field(..., description="Number of items that passed", ge=0)
    failed_items: int = Field(..., description="Number of items that failed", ge=0)
    total_execution_time_ms: float = Field(..., description="Total execution time", ge=0)


# Initialize validation service (will be instantiated on first use)
_validation_service: Optional[ValidationService] = None


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
    responses={401: {"description": "Unauthorized - Invalid or missing authentication token"}},
)
async def validate_content(
    request: ValidationRequest,
    user: dict = Depends(verify_supabase_token),
):
    """Validate METAR TAC or IWXXM XML content through multiple validation layers.

    ## Request Body
    - **content** (string, required): The METAR TAC or IWXXM XML content to validate
    - **content_type** (string, default="tac"): Type of content ("tac" or "xml")
    - **layers** (array, optional): Specific validation layers to run. If None, runs all layers:
      - `airport_icao`: Validate ICAO airport code
      - `tac_syntax`: Validate METAR TAC syntax
      - `xml_wellformed`: Check XML is well-formed
      - `xml_schema`: Validate against XSD schema
      - `schematron`: SCHEMATRON rules validation
      - `gml_references`: GML reference checks
      - `wmo_codelists`: WMO code list validation
    - **iwxxm_version** (string, optional): IWXXM version for context (e.g., "3.0.1")

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
    service = get_validation_service()

    try:
        result = service.validate_all_layers(tac_text=request.content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post(
    "/validate-multi",
    response_model=BatchValidationResponse,
    tags=["Validation"],
    summary="Validate multiple METAR TAC or IWXXM XML inputs",
    responses={401: {"description": "Unauthorized - Invalid or missing authentication token"}},
)
async def validate_multiple(
    request: BatchValidationRequest,
    user: dict = Depends(verify_supabase_token),
):
    """Validate multiple METAR TAC or IWXXM XML inputs in a single request.

    Useful for batch validation of multiple entries. Each item is validated
    independently and can have different content types.

    ## Request Body
    - **items** (array, required): Array of validation requests (1-100 items)
      - Each item has: content, content_type, layers (optional), iwxxm_version (optional)
    - **layers** (array, optional): Default layers to apply to all items

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
    service = get_validation_service()

    try:
        results: List[AggregatedValidationResult] = []
        total_time = 0.0

        for item in request.items:
            result = service.validate_all_layers(tac_text=item.content)
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch validation error: {str(e)}")


@router.get(
    "/layers",
    response_model=ValidationLayersResponse,
    tags=["Validation"],
    summary="Get available validation layers",
    responses={401: {"description": "Unauthorized - Invalid or missing authentication token"}},
)
async def get_validation_layers(
    user: dict = Depends(verify_supabase_token),
):
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
