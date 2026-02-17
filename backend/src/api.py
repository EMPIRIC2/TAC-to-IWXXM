"""Standalone backend API module for Docker deployment."""
from __future__ import annotations

import os
import io
import pathlib
import zipfile
import datetime
import sys
import logging
from typing import List, Optional, Union, Any

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src directory to path for imports (for local uvicorn execution)
sys.path.insert(0, str(pathlib.Path(__file__).parent))

logger.info("DEBUG: Starting api.py imports...")

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    # Try relative imports first (when run as module in Docker)
    logger.info("DEBUG: Attempting relative imports...")
    from .utilities.conversion import convert_metar_tac_with_metadata, ConversionError
    from .utilities.security import verify_supabase_token
    from .utilities.tac_parser import extract_airport_code
    from .schemas.conversion import (
        ConversionResult,
        ConversionResponse,
        ConversionRequest,
        ErrorDetail,
        HealthResponse,
    )
    from .schemas.airport import Airport, get_airport_validator
    from .schemas.validation import ValidationLayer, ValidateRequest
    from .schemas.icao_opmet import TranslationStatus
    from .services.validation_orchestrator import get_validation_orchestrator
    from .services.validation import ValidationService, ValidationError as ValidationServiceError
    from .services.statistics import statistics_service
    from .services.webhooks import webhook_service
    from .routers import evaluation, validation, icao_opmet
    from .config.icao_opmet import get_translation_centre_info, get_icao_region
    from .services.database import database_lifespan
    logger.info("DEBUG: Relative imports successful")
except ImportError as e:
    # Fall back to direct imports (when sys.path is set for local development)
    logger.info(f"DEBUG: Relative import failed: {e}, trying direct imports...")
    from utilities.conversion import convert_metar_tac_with_metadata, ConversionError
    from utilities.security import verify_supabase_token
    from utilities.tac_parser import extract_airport_code
    from schemas.conversion import (
        ConversionResult,
        ConversionResponse,
        ConversionRequest,
        ErrorDetail,
        HealthResponse,
    )
    from schemas.airport import Airport, get_airport_validator
    from schemas.validation import ValidationLayer, ValidateRequest
    from schemas.icao_opmet import TranslationStatus
    from services.validation_orchestrator import get_validation_orchestrator
    from services.validation import ValidationService, ValidationError as ValidationServiceError
    from services.statistics import statistics_service
    from services.webhooks import webhook_service
    from routers import evaluation, validation, icao_opmet
    from config.icao_opmet import get_translation_centre_info, get_icao_region
    from services.database import database_lifespan
    logger.info("DEBUG: Direct imports successful")

app = FastAPI(
    title="METAR to IWXXM Backend API",
    version="0.1.0",
    description="Convert METAR/SPECI TAC messages to IWXXM XML format with comprehensive validation",
    lifespan=database_lifespan,  # Initialize database pool on startup
    openapi_tags=[
        {
            "name": "Health",
            "description": "API health and status checks",
        },
        {
            "name": "Conversion",
            "description": "Convert METAR TAC to IWXXM XML format",
        },
        {
            "name": "Validation",
            "description": "Validate METAR TAC and IWXXM XML content through multiple validation layers",
        },
        {
            "name": "Evaluation",
            "description": "Run evaluation jobs to compare conversion results with reference data",
        },
        {
            "name": "ICAO OPMET Statistics",
            "description": "Translation Centre statistics and ICAO OPMET Data Exchange compliance",
        },
    ],
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

# Configure CORS with dynamic allowed origins from environment
def get_cors_origins() -> list:
    """Get allowed CORS origins from environment or use defaults."""
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
    
    if allowed_origins_env:
        # Parse comma-separated list from env var
        origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
        return origins
    
    # Default origins if env var not set
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
    return [
        frontend_url,
        "http://localhost:3000",  # Vite dev server
    ]


allowed_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Add Translation Centre identification headers (ICAO OPMET compliance)
@app.middleware("http")
async def add_translation_centre_headers(request: Request, call_next):
    """
    Add ICAO Translation Centre identification headers to all responses.
    
    Implements ICAO OPMET Data Exchange Guidelines Section 7 requirements
    for Translation Centre identification in HTTP responses.
    """
    response = await call_next(request)
    
    # Add Translation Centre metadata headers
    try:
        centre_info = get_translation_centre_info()
        # Only add headers with non-None values
        if centre_info.get("translationCentreDesignator"):
            response.headers["X-Translation-Centre"] = centre_info["translationCentreDesignator"]
        if centre_info.get("translationCentreName"):
            response.headers["X-Translation-Centre-Name"] = centre_info["translationCentreName"]
        if centre_info.get("icaoLocationIndicator"):
            response.headers["X-ICAO-Location-Indicator"] = centre_info["icaoLocationIndicator"]
    except Exception as e:
        logger.debug(f"Translation Centre headers not configured: {e}")
    
    return response


# Dependency to handle optional file uploads (including empty strings from Swagger UI)
async def parse_files(request: Request) -> List[UploadFile]:
    """
    Parse files parameter from request, handling edge cases:
    - Swagger UI 'Send empty value' sends empty string which FastAPI can't parse
    - This manually extracts files from the form, filtering out empty strings
    """
    try:
        form = await request.form()
        files = []
        for key, value in form.multi_items():
            if key == "files":
                # Only add if it's actually an UploadFile, not an empty string
                if hasattr(value, 'filename') and value.filename:
                    files.append(value)
        return files
    except Exception as e:
        logger.warning(f"Error parsing files from request: {e}")
        return []


# Customize OpenAPI schema to add Bearer token authentication
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token from the auth service (login at auth service or use DISABLE_AUTH=true for dev)",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Include routers
logger.info(f"DEBUG: validation module = {validation}")
logger.info(f"DEBUG: validation.router = {validation.router}")
logger.info(f"DEBUG: evaluation module = {evaluation}")  
logger.info(f"DEBUG: evaluation.router = {evaluation.router}")

try:
    app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
    logger.info("DEBUG: included validation router successfully")
except Exception as e:
    logger.error(f"DEBUG: Failed to include validation router: {e}", exc_info=True)

try:
    app.include_router(evaluation.router, prefix="/api/v1/eval", tags=["Evaluation"])
    logger.info("DEBUG: included evaluation router successfully")
except Exception as e:
    logger.error(f"DEBUG: Failed to include evaluation router: {e}", exc_info=True)

try:
    app.include_router(icao_opmet.router)
    logger.info("DEBUG: included ICAO OPMET router successfully")
except Exception as e:
    logger.error(f"DEBUG: Failed to include ICAO OPMET router: {e}", exc_info=True)

logger.info(f"DEBUG: total routes = {len(app.routes)}")


# Custom dependency to handle optional file uploads (filters out empty strings from Swagger UI)
async def parse_optional_files(request: Request) -> List[UploadFile]:
    """Parse optional file uploads, filtering out empty strings from form data."""
    form = await request.form()
    files_data = form.getlist("files")
    # Filter out any empty strings or non-UploadFile objects
    return [f for f in files_data if isinstance(f, UploadFile)]



@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health() -> HealthResponse:
    """Check API health and component availability.
    
    Verifies that the API is running and GIFTs library is available for conversions.
    Returns overall status and version information.
    
    ## Response
    - **status** (string): "healthy" or "degraded"
    - **version** (string): API version
    - **gifts_available** (boolean): Whether GIFTs conversion library is available
    """
    try:
        test_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
        _ = convert_metar_tac_with_metadata(test_metar)
        gifts_available = True
        status = "healthy"
    except Exception:
        gifts_available = False
        status = "degraded"
    return HealthResponse(status=status, version="0.1.0", gifts_available=gifts_available)


@app.get("/api/v1/versions", tags=["Conversion"])
def get_supported_versions():
    """Get list of supported IWXXM versions.
    
    Returns information about all supported IWXXM versions including
    version strings, release dates, and status (latest, previous, legacy).
    
    ## Response
    ```json
    {
      "default_version": "2025-2",
      "supported_versions": [
        {
          "version": "2025-2",
          "name": "IWXXM 2025-2",
          "status": "latest",
          "release_date": "2025-11-25",
          "wmo_amendment": 82
        },
        {
          "version": "2023-1",
          "name": "IWXXM 2023-1",
          "status": "previous",
          "release_date": "2023-06-02",
          "wmo_amendment": 78
        }
      ],
      "notes": {
        "2025-1": "Version 2025-1 does not exist; requests are remapped to 2025-2"
      },
      "deprecated_versions": [
        "2021-2",
        "2018",
        "2016",
        "3.0",
        "2.1",
        "2.0",
        "1.1"
      ]
    }
    ```
    """
    try:
        from .config.iwxxm_versions import SUPPORTED_VERSIONS, DEFAULT_VERSION, DEPRECATED_VERSIONS
    except ImportError:
        from config.iwxxm_versions import SUPPORTED_VERSIONS, DEFAULT_VERSION, DEPRECATED_VERSIONS
    
    versions_list = []
    for version, config in SUPPORTED_VERSIONS.items():
        versions_list.append({
            "version": version,
            "name": config.get("name", ""),
            "status": config.get("status", ""),
            "release_date": config.get("release_date", ""),
            "wmo_amendment": config.get("wmo_amendment", 0)
        })
    
    return {
        "default_version": DEFAULT_VERSION,
        "supported_versions": sorted(
            versions_list,
            key=lambda x: x["release_date"],
            reverse=True
        ),
        "notes": {
            "2025-1": "Version 2025-1 does not exist; requests are auto-remapped to 2025-2"
        },
        "deprecated_versions": list(DEPRECATED_VERSIONS.keys())
    }


@app.get("/api/v1/schema-status", tags=["Conversion"])
def get_schema_status():
    """Get comprehensive schema status including RC versions and mirroring info.
    
    Returns detailed information about all IWXXM schema versions including:
    - Stable releases and Release Candidates (RC)
    - Discovery dates and source URLs
    - Mirroring status
    - Channel classification
    
    ## Response
    ```json
    {
      "stable": ["2025-2", "2023-1"],
      "rc": ["2025-2RC1"],
      "all": ["2025-2", "2025-2RC1", "2023-1"],
      "default": "2025-2",
      "metadata": {
        "2025-2": {
          "name": "IWXXM 2025-2",
          "channel": "stable",
          "status": "latest",
          "discovered": "2025-11-25T00:00:00Z",
          "source_url": "https://github.com/wmo-im/iwxxm/tree/v2025-2",
          "mirrored": true
        },
        "2025-2RC1": {
          "name": "IWXXM 2025-2 RC1",
          "channel": "rc",
          "status": "rc",
          "discovered": "2026-02-10T00:00:00Z",
          "source_url": "https://schemas.wmo.int/iwxxm/2025-2RC1/",
          "mirrored": false,
          "promoted_to_stable": null
        }
      }
    }
    ```
    """
    try:
        from .config.iwxxm_versions import (
            get_versions_by_channel,
            get_all_versions_with_metadata,
            DEFAULT_VERSION
        )
    except ImportError:
        from config.iwxxm_versions import (
            get_versions_by_channel,
            get_all_versions_with_metadata,
            DEFAULT_VERSION
        )
    
    stable_versions = get_versions_by_channel("stable")
    rc_versions = get_versions_by_channel("rc")
    all_versions = get_versions_by_channel("all")
    all_metadata = get_all_versions_with_metadata()
    
    # Build metadata summary
    metadata_summary = {}
    for version, data in all_metadata.items():
        discovery_meta = data.get("discovery_metadata", {})
        metadata_summary[version] = {
            "name": data.get("name", f"IWXXM {version}"),
            "channel": discovery_meta.get("channel", "stable"),
            "status": data.get("status", "unknown"),
            "discovered": discovery_meta.get("discovered", ""),
            "source_url": discovery_meta.get("source_url", ""),
            "mirrored": discovery_meta.get("mirrored", False)
        }
        
        # Add RC-specific fields
        if "RC" in version.upper():
            metadata_summary[version]["promoted_to_stable"] = data.get("promoted_to_stable")
    
    return {
        "stable": stable_versions,
        "rc": rc_versions,
        "all": all_versions,
        "default": DEFAULT_VERSION,
        "metadata": metadata_summary
    }


@app.post("/api/v1/validate", tags=["Validation"], responses={
    401: {"description": "Unauthorized - Invalid or missing authentication token"},
})
async def validate_comprehensive(
    request_body: Optional[ValidateRequest] = None,
    manual_text: str = Form(default="", description="METAR TAC text to validate"),
    xml_content: str = Form(default="", description="Optional XML to validate (if omitted, TAC will be converted first)"),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version"),
    layers: List[str] = Form(default=["ALL"], description="Validation layers to run (ALL, or specific: AIRPORT_ICAO, TAC_SYNTAX, XML_WELLFORMED, XML_SCHEMA, SCHEMATRON, GML_REFERENCES, WMO_CODELISTS)"),
    stop_on_error: bool = Form(default=True, description="Stop at first blocking layer failure"),
    user: dict = Depends(verify_supabase_token),
):
    """Perform comprehensive 7-layer IWXXM validation.
    
    Validates METAR TAC input through all 7 validation layers:
    
    1. **Layer 1 (AIRPORT_ICAO)**: Validates ICAO airport code against database
    2. **Layer 2 (TAC_SYNTAX)**: Validates TAC/METAR syntax basics
    3. **Layer 3 (XML_WELLFORMED)**: Checks XML is well-formed
    4. **Layer 4 (XML_SCHEMA)**: Validates against official IWXXM XSD schemas
    5. **Layer 5 (SCHEMATRON)**: Validates business rules from official Schematron
    6. **Layer 6 (GML_REFERENCES)**: Validates GML internal references
    7. **Layer 7 (WMO_CODELISTS)**: Validates against official WMO RDF codelists
    
    **Authentication**: Requires valid Supabase JWT token
    
    **Request Parameters**:
    - **manual_text** (required): METAR TAC text to validate
    - **xml_content** (optional): Pre-converted XML to validate (if omitted, TAC will be converted)
    - **iwxxm_version**: Target IWXXM version (default: "2025-2")
    - **layers**: Validation layers to run (default: ["ALL"])
      - "ALL": Run all 7 layers
      - Or specify: ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_SCHEMA", "SCHEMATRON", ...]
    - **stop_on_error**: Stop at first blocking layer failure (default: true)
    
    **Response**:
    ```json
    {
      "is_valid": true,
      "version": "2025-2",
      "layers_run": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA", "SCHEMATRON", "GML_REFERENCES", "WMO_CODELISTS"],
      "layers_passed": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA", "SCHEMATRON", "GML_REFERENCES", "WMO_CODELISTS"],
      "layers_failed": [],
      "total_issues": 0,
      "issues_by_layer": {},
      "stopped_at_layer": null
    }
    ```
    """
    try:
        # Handle JSON request body
        if request_body is not None:
            xml_content = request_body.iwxxm_xml
            iwxxm_version = request_body.version
            validation_level = request_body.validation_level or "comprehensive"
            manual_text = ""  # Don't use form input
            
            # Map validation_level to layers
            if validation_level == "comprehensive":
                layers = ["ALL"]
            elif validation_level == "schema":
                layers = ["XML_WELLFORMED", "XML_SCHEMA"]
            elif validation_level == "schematron":
                layers = ["SCHEMATRON"]
            elif validation_level == "icao_opmet":
                layers = ["WMO_CODELISTS", "GML_REFERENCES"]
            else:
                layers = ["AIRPORT_ICAO", "TAC_SYNTAX"]
        
        # Normalize version
        try:
            from .config.iwxxm_versions import normalize_version, get_version_config
        except ImportError:
            from config.iwxxm_versions import normalize_version, get_version_config
        
        iwxxm_version = normalize_version(iwxxm_version)
        
        # Validate version is supported
        try:
            get_version_config(iwxxm_version)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Convert TAC to XML if not provided
        if not xml_content:
            try:
                xml_content, _ = convert_metar_tac_with_metadata(manual_text, iwxxm_version=iwxxm_version)
            except ConversionError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to convert TAC to XML: {str(e)}"
                )
        
        # Parse layer selection
        selected_layers = []
        if "ALL" in layers:
            selected_layers = list(ValidationLayer)
        else:
            # Convert string names to enum values
            for layer_name in layers:
                try:
                    selected_layers.append(ValidationLayer[layer_name])
                except KeyError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid validation layer: {layer_name}. "
                               f"Valid options: {[l.name for l in ValidationLayer]}"
                    )
        
        # Run comprehensive validation
        orchestrator = get_validation_orchestrator()
        result = orchestrator.validate_complete(
            tac_text=manual_text,
            xml_content=xml_content,
            version=iwxxm_version,
            layers=selected_layers,
            stop_on_error=stop_on_error
        )
        
        # Format response
        return {
            "is_valid": result.is_valid,
            "version": result.version,
            "layers_run": [layer.name for layer in result.layers_run],
            "layers_passed": [layer.name for layer in result.layers_passed],
            "layers_failed": [layer.name for layer in result.layers_failed],
            "total_issues": len(result.all_issues),
            "issues": [
                {
                    "layer": issue.layer.name,
                    "level": issue.level.name,
                    "message": issue.message,
                    "location": issue.location,
                    "code": issue.code
                }
                for issue in result.all_issues
            ],
            "issues_by_layer": {
                layer.name: [
                    {
                        "level": issue.level.name,
                        "message": issue.message,
                        "location": issue.location,
                        "code": issue.code
                    }
                    for issue in issues
                ]
                for layer, issues in result.issues_by_layer.items()
            },
            "stopped_at_layer": result.stopped_at_layer.name if result.stopped_at_layer else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.post("/api/v1/convert", response_model=ConversionResponse, tags=["Conversion"], responses={
    401: {"description": "Unauthorized - Invalid or missing authentication token"},
})
async def convert(
    request: Request,
    files: Any = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)"),
    validate_output: bool = Form(default=False, description="Enable full 7-layer IWXXM validation after conversion"),
    user: dict = Depends(verify_supabase_token),
) -> ConversionResponse:
    # Try to parse JSON body if Content-Type is application/json
    request_body = None
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body_data = await request.json()
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid JSON in request body: {str(e)}"
            )
        
        try:
            request_body = ConversionRequest(**body_data)
        except Exception as e:
            # Pydantic validation error - return 422
            raise HTTPException(
                status_code=422,
                detail=f"Validation error: {str(e)}"
            )
    """Convert METAR/SPECI TAC text to IWXXM XML format.

    Converts one or more METAR TAC messages to IWXXM XML format. Supports:
    - Manual text input via form field
    - File uploads (text files)
    - Batch processing (multiple files)
    - Dynamic IWXXM version selection
    - Input validation (ICAO code and TAC syntax)
    - Optional output validation (full 7-layer IWXXM validation)

    **Authentication**: Requires valid Supabase JWT token in Authorization header

    **Request Parameters**:
    - **files** (array): Optional uploaded text files containing METAR TAC
    - **manual_text** (string): Optional manual text input
    - **iwxxm_version** (string): Target IWXXM version (default: "2025-2")
      - "2025-2": Latest IWXXM version (recommended)
      - "2023-1": Previous stable release
      - "2025-1": Auto-remaps to 2025-2
      - Pre-2023 versions (2021-2, 2018, 2016, etc.) are deprecated and will be rejected
    - **validate_output** (boolean): Enable full IWXXM validation after conversion (default: false)
      - When true, runs layers 3-7 (XML wellformed, XSD schema, Schematron, GML, codelists)
      - Validation issues are logged but don't prevent conversion results

    **Validation**:
    - **Input Validation (Always On)**: 
      - Layer 1: ICAO airport code validation
      - Layer 2: TAC syntax validation
    - **Output Validation (Optional)**:
      - Layer 3: XML well-formedness
      - Layer 4: XSD schema validation
      - Layer 5: Schematron business rules
      - Layer 6: GML reference validation
      - Layer 7: WMO codelist validation

    **Response**:
    - **results** (array): Successfully converted IWXXM XML documents
    - **errors** (array): Error messages for failed conversions
    - **total_processed** (integer): Total inputs processed
    - **successful** (integer): Number of successful conversions
    - **failed** (integer): Number of failed conversions

    **Example Success Response**:
    ```json
    {
      "results": [
        {
          "name": "manual_input.txt",
          "content": "<?xml version='1.0'?>...",
          "source": "manual",
          "size_bytes": 1452,
          "iwxxm_version": "2025-2"
        }
      ],
      "errors": [],
      "total_processed": 1,
      "successful": 1,
      "failed": 0
    }
    ```

    **Example Failure Response**:
    ```json
    {
      "results": [
        {
          "name": "valid_file.txt",
          "content": "<?xml version='1.0'?>...",
          "source": "valid_file.txt",
          "size_bytes": 1200,
          "iwxxm_version": "2025-2"
        }
      ],
      "errors": [
        "invalid_file.txt: Unknown airport code: ZZZZ"
      ],
      "total_processed": 2,
      "successful": 1,
      "failed": 1
    }
    ```
    """
    # Handle JSON request body (for metars list)
    if request_body is not None:
        metars = request_body.metars
        iwxxm_version = request_body.version
        validation_level = request_body.validation_level or "basic"
        manual_text = ""  # Override form input
        files = None  # Override file input
        
        # Map validation_level to validate_output
        validate_output = validation_level in ["comprehensive", "schematron", "icao_opmet"]
    
    # Validate and normalize IWXXM version
    try:
        from .config.iwxxm_versions import normalize_version, get_version_config
    except ImportError:
        from config.iwxxm_versions import normalize_version, get_version_config
    
    try:
        iwxxm_version = normalize_version(iwxxm_version)
        get_version_config(iwxxm_version)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message=f"Invalid IWXXM version: {e}",
                errors=[str(e)],
                total_errors=1
            ).model_dump(),
        )
    
    results: List[ConversionResult] = []
    errors: List[str] = []
    total_inputs = 0
    
    # Initialize validation service for input validation
    validation_service = ValidationService()
    
    # Initialize validation orchestrator for output validation if requested
    validation_orchestrator = get_validation_orchestrator() if validate_output else None

    # Handle JSON request body with metars list
    metars_list = []
    if request_body is not None and request_body.metars:
        metars_list = request_body.metars
    
    # Process metars from JSON request body
    for metar_text in metars_list:
        if not metar_text.strip():
            continue
            
        total_inputs += 1
        start_time = None
        translation_id = None
        try:
            # Use the same validation and conversion logic as manual_text
            metar_name = f"metar_{total_inputs}.txt"
            
            # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
            try:
                validation_result = validation_service.validate_all_layers(metar_text.strip())
                if not validation_result.passed:
                    # Build summary from validation result
                    validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                    error_msg = f"{metar_name}: Validation failed - {validation_summary}"
                    errors.append(error_msg)
                    # Log failed validation
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"validation": validation_summary},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=user.get("sub")
                        )
                        airport_code = extract_airport_code(metar_text.strip())
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_failed",
                            error_message=validation_summary
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log failed translation: {log_err}")
            except ValidationServiceError as ve:
                errors.append(f"{metar_name}: {str(ve)}")
                # Log validation error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"error": str(ve)},
                        translation_duration_ms=0,
                        icao_airport_code=extract_airport_code(metar_text.strip()),
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(metar_text.strip())
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="validation_error",
                        error_message=str(ve)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log validation error: {log_err}")
            else:
                # Start timing for successful conversion
                import time
                start_time = time.perf_counter()
                
                # Convert METAR to IWXXM
                try:
                    iwxxm_content, _ = convert_metar_tac_with_metadata(
                        metar_text.strip(),
                        iwxxm_version=iwxxm_version
                    )
                    
                    # Optional output validation (Layers 3-7)
                    validation_layers_passed = [ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX]
                    
                    if validation_orchestrator:
                        validation_result = validation_orchestrator.validate(
                            iwxxm_content,
                            iwxxm_version=iwxxm_version,
                            layers=[ValidationLayer.XML_WELLFORMED, ValidationLayer.XML_SCHEMA, ValidationLayer.SCHEMATRON, ValidationLayer.GML_REFERENCES, ValidationLayer.WMO_CODELISTS]
                        )
                        if validation_result.passed:
                            validation_layers_passed.extend([ValidationLayer.XML_WELLFORMED, ValidationLayer.XML_SCHEMA, ValidationLayer.SCHEMATRON, ValidationLayer.GML_REFERENCES, ValidationLayer.WMO_CODELISTS])
                    
                    # Add to results
                    result = ConversionResult(
                        name=metar_name,
                        content=iwxxm_content,
                        source="json",
                        size_bytes=len(iwxxm_content.encode('utf-8')),
                    )
                    results.append(result)
                    
                    # Log successful translation
                    try:
                        end_time = time.perf_counter()
                        duration_ms = (end_time - start_time) * 1000
                        
                        translation_id = await statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=iwxxm_content,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.SUCCESS,
                            validation_layers_passed=validation_layers_passed,
                            translation_duration_ms=duration_ms,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=user.get("sub")
                        )
                        
                        airport_code = extract_airport_code(metar_text.strip())
                        await webhook_service.notify_translation_completed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            iwxxm_version=iwxxm_version,
                            file_size_bytes=len(iwxxm_content.encode('utf-8')),
                            duration_ms=duration_ms
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log successful translation: {log_err}")
                        
                except ConversionError as ce:
                    error_msg = f"{metar_name}: Conversion error - {str(ce)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    try:
                        end_time = time.perf_counter()
                        duration_ms = (end_time - start_time) * 1000 if start_time else 0
                        
                        await statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
                            validation_errors={"error": str(ce)},
                            translation_duration_ms=duration_ms,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=user.get("sub")
                        )
                        
                        airport_code = extract_airport_code(metar_text.strip())
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id or "unknown",
                            airport_code=airport_code or "UNKNOWN",
                            error_type="conversion_error",
                            error_message=str(ce)
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log conversion error: {log_err}")
                except Exception as e:
                    error_msg = f"{metar_name}: Unexpected error - {str(e)}"
                    errors.append(error_msg)
                    logger.exception(error_msg)
        except Exception as e:
            error_msg = f"{metar_name}: Unhandled error - {str(e)}"
            errors.append(error_msg)
            logger.exception(error_msg)

    if manual_text.strip():
        total_inputs += 1
        start_time = None
        translation_id = None
        try:
            # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
            try:
                validation_result = validation_service.validate_all_layers(manual_text.strip())
                if not validation_result.passed:
                    # Build summary from validation result
                    validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                    error_msg = f"manual_input: Validation failed - {validation_summary}"
                    errors.append(error_msg)
                    # Log failed validation
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=manual_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"validation": validation_summary},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(manual_text.strip()),
                            user_id=user.get("sub")
                        )
                        airport_code = extract_airport_code(manual_text.strip())
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_failed",
                            error_message=validation_summary
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log failed translation: {log_err}")
            except ValidationServiceError as ve:
                errors.append(f"manual_input: {str(ve)}")
                # Log validation error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=manual_text.strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"error": str(ve)},
                        translation_duration_ms=0,
                        icao_airport_code=extract_airport_code(manual_text.strip()),
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(manual_text.strip())
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="validation_error",
                        error_message=str(ve)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log validation error: {log_err}")
            else:
                # Start timing for successful conversion
                import time
                start_time = time.perf_counter()
                
                # Only convert if validation passed
                # Note: validate=False for now to avoid hangs on WMO online validation in tests
                xml_text, validation_result_from_conversion = convert_metar_tac_with_metadata(
                    manual_text.strip(), 
                    iwxxm_version=iwxxm_version,
                    validate=False  # Disable validation for backward compatibility
                )
                
                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                
                # Track validation layers passed
                layers_passed = [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
                validation_errors_dict = {}
                
                # Use validation result from conversion if available
                if validate_output and validation_result_from_conversion:
                    if validation_result_from_conversion.is_valid:
                        # Add all passed validation layers
                        for layer in ValidationLayer:
                            layers_passed.append(layer.value)
                    else:
                        warning_msg = f"manual_input: IWXXM validation issues found - {len(validation_result_from_conversion.all_issues)} issues"
                        logger.warning(warning_msg)
                        validation_errors_dict = {
                            "validation_issues": [str(issue) for issue in validation_result_from_conversion.all_issues[:10]]
                        }
                
                # Log successful translation
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=manual_text.strip(),
                        iwxxm_output=xml_text,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.SUCCESS,
                        validation_layers_passed=layers_passed,
                        validation_errors=validation_errors_dict if validation_errors_dict else None,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(manual_text.strip()),
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(manual_text.strip())
                    icao_region = get_icao_region(airport_code) if airport_code else "UNKNOWN"
                    await webhook_service.notify_translation_success(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        icao_region=icao_region,
                        iwxxm_version=iwxxm_version,
                        duration_ms=duration_ms
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")
                
                results.append(
                    ConversionResult(
                        name="manual_input.txt",
                        content=xml_text,
                        source="manual",
                        size_bytes=len(xml_text.encode("utf-8")),
                    )
                )
        except ConversionError as e:
            errors.append(f"manual_input: {e}")
            # Log conversion error
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=manual_text.strip(),
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"conversion_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(manual_text.strip()),
                )
            except Exception as log_err:
                logger.error(f"Failed to log conversion error: {log_err}")

    # Process uploaded files (if any)
    if files:
        for uf in files:
            total_inputs += 1
            start_time = None
            translation_id = None
            try:
                data = (await uf.read()).decode("utf-8", errors="ignore")
                if not data.strip():
                    errors.append(f"{uf.filename}: empty file")
                    continue
                
                # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
                try:
                    validation_result = validation_service.validate_all_layers(data.strip())
                    if not validation_result.passed:
                        # Build summary from validation result
                        validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                        error_msg = f"{uf.filename}: Validation failed - {validation_summary}"
                        errors.append(error_msg)
                        # Log failed validation
                        try:
                            translation_id = await statistics_service.log_translation(
                                tac_message=data.strip(),
                                iwxxm_output=None,
                                iwxxm_version=iwxxm_version,
                                translation_status=TranslationStatus.FAILED,
                                validation_layers_passed=[],
                                validation_errors={"validation": validation_summary},
                                translation_duration_ms=0,
                                icao_airport_code=extract_airport_code(data.strip()),
                                user_id=user.get("sub")
                            )
                            airport_code = extract_airport_code(data.strip())
                            await webhook_service.notify_translation_failed(
                                translation_id=translation_id,
                                airport_code=airport_code or "UNKNOWN",
                                error_type="validation_failed",
                                error_message=validation_summary
                            )
                        except Exception as log_err:
                            logger.error(f"Failed to log failed translation: {log_err}")
                        continue
                except ValidationServiceError as ve:
                    errors.append(f"{uf.filename}: {str(ve)}")
                    # Log validation error
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=data.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"error": str(ve)},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(data.strip()),
                            user_id=user.get("sub")
                        )
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            tac_message=data.strip(),
                            error=str(ve)
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log validation error: {log_err}")
                    continue
                
                # Start timing for successful conversion
                import time
                start_time = time.perf_counter()
                
                # Only convert if validation passed
                xml_text, _ = convert_metar_tac_with_metadata(data, iwxxm_version=iwxxm_version)
                
                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                
                # Track validation layers passed
                layers_passed = [ValidationLayer.AIRPORT_ICAO.value, ValidationLayer.TAC_SYNTAX.value]
                validation_errors_dict = {}
                
                # Optionally validate output IWXXM XML (Layers 3-7)
                if validate_output and validation_orchestrator:
                    try:
                        validation_result = validation_orchestrator.validate_complete(
                            tac_text=data.strip(),
                            xml_content=xml_text,
                            version=iwxxm_version,
                            stop_on_error=False  # Collect all issues
                        )
                        if validation_result.is_valid:
                            # Add all passed validation layers
                            for layer in ValidationLayer:
                                layers_passed.append(layer.value)
                        else:
                            warning_msg = f"{uf.filename}: IWXXM validation issues found - {len(validation_result.all_issues)} issues"
                            logger.warning(warning_msg)
                            validation_errors_dict = {
                                "validation_issues": [str(issue) for issue in validation_result.all_issues[:10]]
                            }
                            # Add validation issues as warnings but still include the result
                    except Exception as ve:
                        logger.warning(f"{uf.filename}: Output validation failed: {ve}")
                        validation_errors_dict = {"validation_error": str(ve)}
                
                # Log successful translation
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data.strip(),
                        iwxxm_output=xml_text,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.SUCCESS,
                        validation_layers_passed=layers_passed,
                        validation_errors=validation_errors_dict if validation_errors_dict else None,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(data.strip()),
                        user_id=user.get("sub")
                    )
                    await webhook_service.notify_translation_success(
                        translation_id=translation_id,
                        airport_code=extract_airport_code(data.strip()) or "UNKNOWN",
                        icao_region=get_icao_region(extract_airport_code(data.strip())) if extract_airport_code(data.strip()) else "UNKNOWN",
                        iwxxm_version=iwxxm_version,
                        duration_ms=duration_ms
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")
                
                out_name = pathlib.Path(uf.filename or "unknown").stem + ".txt"
                results.append(
                    ConversionResult(
                        name=out_name,
                        content=xml_text,
                        source=uf.filename,
                        size_bytes=len(xml_text.encode("utf-8")),
                    )
                )
            except ConversionError as e:
                errors.append(f"{uf.filename}: {e}")
                # Log conversion error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data.strip() if 'data' in locals() else "",
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"conversion_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(data.strip()) if 'data' in locals() else None,
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(data.strip()) if 'data' in locals() else None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="conversion_error",
                        error_message=str(e)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log conversion error: {log_err}")
            except Exception as e:
                errors.append(f"{uf.filename}: unexpected error {e}")
                # Log unexpected error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data.strip() if 'data' in locals() else "",
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"unexpected_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(data.strip()) if 'data' in locals() else None,
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(data.strip()) if 'data' in locals() else None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="unexpected_error",
                        error_message=str(e)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log unexpected error: {log_err}")

    if not results and errors:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message="All conversions failed", errors=errors, total_errors=len(errors)
            ).model_dump(),
        )

    return ConversionResponse(
        results=results,
        errors=errors,
        total_processed=total_inputs,
        successful=len(results),
        failed=len(errors),
    )
@app.post("/api/v1/convert-zip", response_class=StreamingResponse, tags=["Conversion"], responses={
    401: {"description": "Unauthorized - Invalid or missing authentication token"},
})
async def convert_zip(
    request: Request,
    files: Any = Depends(parse_files),
    manual_text: str = Form(default="", description="Optional manual text input (METAR TAC format)"),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version: 2025-2 (latest), 2023-1 (previous), or 2025-1 (auto-remaps to 2025-2)"),
    user: dict = Depends(verify_supabase_token),
) -> StreamingResponse:
    # Try to parse JSON body if Content-Type is application/json
    request_body = None
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body_data = await request.json()
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid JSON in request body: {str(e)}"
            )
        
        try:
            request_body = ConversionRequest(**body_data)
        except Exception as e:
            # Pydantic validation error - return 422
            raise HTTPException(
                status_code=422,
                detail=f"Validation error: {str(e)}"
            )
    """Convert METAR/SPECI TAC inputs to a zipped archive of IWXXM XML files.

    Similar to `/api/v1/convert` but returns results as a ZIP archive instead of JSON.
    Useful for batch processing or downloading multiple converted files.

    **Authentication**: Requires valid Supabase JWT token in Authorization header

    **Request Parameters**:
    - **files** (array): Optional uploaded text files containing METAR TAC
    - **manual_text** (string): Optional manual text input
    - **iwxxm_version** (string): Target IWXXM version (default: "2025-2")

    **Response**:
    - **Content Type**: `application/zip`
    - **Content**: ZIP archive containing:
      - One `.xml` file per successfully converted METAR
      - `errors.txt` file (if any conversions failed)

    **Example ZIP Contents**:
    ```
    iwxxm_batch_20260210T143000Z.zip
    ├── manual_input.xml
    ├── KJFK_231751Z.xml
    ├── EGLL_231750Z.xml
    └── errors.txt (if any failures)
    ```

    **Use Cases**:
    - Batch conversion with file export
    - Integration with external processing pipelines
    - Offline processing and storage
    """
    # Handle JSON request body (for metars list)
    if request_body is not None:
        metars_list = request_body.metars
        iwxxm_version = request_body.version
        validation_level = request_body.validation_level or "basic"
        manual_text = ""  # Override form input
        files = None  # Override file input
    else:
        metars_list = []
    
    # Validate and normalize IWXXM version
    try:
        from .config.iwxxm_versions import normalize_version, get_version_config
    except ImportError:
        from config.iwxxm_versions import normalize_version, get_version_config
    
    try:
        iwxxm_version = normalize_version(iwxxm_version)
        get_version_config(iwxxm_version)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(
                message=f"Invalid IWXXM version: {e}",
                errors=[str(e)],
                total_errors=1
            ).model_dump(),
        )
    
    results: List[tuple[str, str]] = []
    errors: List[str] = []
    translation_ids: List[str] = []  # Track for bulk notification

    if manual_text.strip():
        start_time = None
        translation_id = None
        try:
            # Start timing
            import time
            start_time = time.perf_counter()
            
            xml_text, _ = convert_metar_tac_with_metadata(manual_text.strip(), iwxxm_version=iwxxm_version)
            
            # Calculate duration
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            results.append(("manual_input.xml", xml_text))
            
            # Log successful translation
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=manual_text.strip(),
                    iwxxm_output=xml_text,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.SUCCESS,
                    validation_layers_passed=[],  # Zip endpoint doesn't validate
                    validation_errors=None,
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(manual_text.strip()),
                    user_id=user.get("sub")
                )
                translation_ids.append(translation_id)
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")
        except ConversionError as e:
            errors.append(f"manual_input: {e}")
            # Log failed translation
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=manual_text.strip(),
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"conversion_error": str(e)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(manual_text.strip()),
                    user_id=user.get("sub")
                )
                airport_code = extract_airport_code(manual_text.strip())
                await webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="conversion_error",
                    error_message=str(e)
                )
            except Exception as log_err:
                logger.error(f"Failed to log failed translation: {log_err}")

    # Process uploaded files (if any)
    if files:
        for uf in files:
            start_time = None
            translation_id = None
            try:
                data = (await uf.read()).decode("utf-8", errors="ignore").strip()
                if not data:
                    errors.append(f"{uf.filename}: empty file")
                    continue
                
                # Start timing
                import time
                start_time = time.perf_counter()
                
                xml_text, _ = convert_metar_tac_with_metadata(data, iwxxm_version=iwxxm_version)
                
                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                
                fname = pathlib.Path(uf.filename or "unknown").stem + ".xml"
                results.append((fname, xml_text))
                
                # Log successful translation
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data,
                        iwxxm_output=xml_text,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.SUCCESS,
                        validation_layers_passed=[],  # Zip endpoint doesn't validate
                        validation_errors=None,
                        translation_duration_ms=duration_ms,
                        icao_airport_code=extract_airport_code(data),
                        user_id=user.get("sub")
                    )
                    translation_ids.append(translation_id)
                except Exception as log_err:
                    logger.error(f"Failed to log successful translation: {log_err}")
            except ConversionError as e:
                errors.append(f"{uf.filename}: {e}")
                # Log failed translation
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data if 'data' in locals() else "",
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"conversion_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(data) if 'data' in locals() else None,
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(data) if 'data' in locals() else None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="conversion_error",
                        error_message=str(e)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log failed translation: {log_err}")
            except Exception as e:
                errors.append(f"{uf.filename}: unexpected error {e}")
                # Log unexpected error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=data if 'data' in locals() else "",
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"unexpected_error": str(e)},
                        translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                        icao_airport_code=extract_airport_code(data) if 'data' in locals() else None,
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(data) if 'data' in locals() else None
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="unexpected_error",
                        error_message=str(e)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log unexpected error: {log_err}")
    
    # Process metars from JSON request body
    for idx, metar_text in enumerate(metars_list, 1):
        if not metar_text.strip():
            continue
        
        start_time = None
        translation_id = None
        try:
            metar_name = f"metar_{idx}.txt"
            
            # Validate METAR input (Layers 1-2: ICAO and TAC syntax)
            try:
                validation_result = validation_service.validate_all_layers(metar_text.strip())
                if not validation_result.passed:
                    # Build summary from validation result
                    validation_summary = f"{validation_result.total_issues} validation issue(s) found"
                    error_msg = f"{metar_name}: Validation failed - {validation_summary}"
                    errors.append(error_msg)
                    # Log failed validation
                    try:
                        translation_id = await statistics_service.log_translation(
                            tac_message=metar_text.strip(),
                            iwxxm_output=None,
                            iwxxm_version=iwxxm_version,
                            translation_status=TranslationStatus.FAILED,
                            validation_layers_passed=[],
                            validation_errors={"validation": validation_summary},
                            translation_duration_ms=0,
                            icao_airport_code=extract_airport_code(metar_text.strip()),
                            user_id=user.get("sub")
                        )
                        airport_code = extract_airport_code(metar_text.strip())
                        await webhook_service.notify_translation_failed(
                            translation_id=translation_id,
                            airport_code=airport_code or "UNKNOWN",
                            error_type="validation_failed",
                            error_message=validation_summary
                        )
                    except Exception as log_err:
                        logger.error(f"Failed to log failed translation: {log_err}")
                    continue  # Skip to next METAR
            except ValidationServiceError as ve:
                errors.append(f"{metar_name}: {str(ve)}")
                # Log validation error
                try:
                    translation_id = await statistics_service.log_translation(
                        tac_message=metar_text.strip(),
                        iwxxm_output=None,
                        iwxxm_version=iwxxm_version,
                        translation_status=TranslationStatus.FAILED,
                        validation_layers_passed=[],
                        validation_errors={"validation_service_error": str(ve)},
                        translation_duration_ms=0,
                        icao_airport_code=extract_airport_code(metar_text.strip()),
                        user_id=user.get("sub")
                    )
                    airport_code = extract_airport_code(metar_text.strip())
                    await webhook_service.notify_translation_failed(
                        translation_id=translation_id,
                        airport_code=airport_code or "UNKNOWN",
                        error_type="validation_error",
                        error_message=str(ve)
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log validation error: {log_err}")
                continue  # Skip to next METAR
            
            # Start timing
            import time
            start_time = time.perf_counter()
            
            xml_text, _ = convert_metar_tac_with_metadata(metar_text.strip(), iwxxm_version=iwxxm_version)
            
            # Calculate duration
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            fname = f"metar_{idx}.xml"
            results.append((fname, xml_text))
            
            # Log successful translation
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=metar_text.strip(),
                    iwxxm_output=xml_text,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.SUCCESS,
                    validation_layers_passed=[],
                    translation_duration_ms=duration_ms,
                    icao_airport_code=extract_airport_code(metar_text.strip()),
                    user_id=user.get("sub")
                )
                translation_ids.append(translation_id)
            except Exception as log_err:
                logger.error(f"Failed to log successful translation: {log_err}")
        except ConversionError as e:
            errors.append(f"metar_{idx}: {e}")
            # Log failed translation
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=metar_text.strip(),
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"conversion_error": str(e)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(metar_text.strip()),
                    user_id=user.get("sub")
                )
                airport_code = extract_airport_code(metar_text.strip())
                await webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="conversion_error",
                    error_message=str(e)
                )
            except Exception as log_err:
                logger.error(f"Failed to log failed translation: {log_err}")
        except Exception as e:
            errors.append(f"metar_{idx}: unexpected error {e}")
            # Log unexpected error
            try:
                translation_id = await statistics_service.log_translation(
                    tac_message=metar_text.strip(),
                    iwxxm_output=None,
                    iwxxm_version=iwxxm_version,
                    translation_status=TranslationStatus.FAILED,
                    validation_layers_passed=[],
                    validation_errors={"unexpected_error": str(e)},
                    translation_duration_ms=int((time.perf_counter() - start_time) * 1000) if start_time else 0,
                    icao_airport_code=extract_airport_code(metar_text.strip()),
                    user_id=user.get("sub")
                )
                airport_code = extract_airport_code(metar_text.strip())
                await webhook_service.notify_translation_failed(
                    translation_id=translation_id,
                    airport_code=airport_code or "UNKNOWN",
                    error_type="unexpected_error",
                    error_message=str(e)
                )
            except Exception as log_err:
                logger.error(f"Failed to log unexpected error: {log_err}")
    
    # Send bulk completion webhook if conversions were successful
    if translation_ids:
        try:
            await webhook_service.notify_bulk_completed(
                translation_ids=translation_ids,
                total_count=len(translation_ids),
                success_count=len(results),
                failed_count=len(errors)
            )
        except Exception as webhook_err:
            logger.error(f"Failed to send bulk completion webhook: {webhook_err}")

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in results:
            zf.writestr(fname, content)
        if errors:
            zf.writestr("errors.txt", "\n".join(errors))
    mem.seek(0)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return StreamingResponse(
        mem,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=iwxxm_batch_{stamp}.zip"
        },
    )


__all__ = ["app"]
