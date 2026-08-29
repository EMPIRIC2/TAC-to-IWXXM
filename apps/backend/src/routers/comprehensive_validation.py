"""Comprehensive IWXXM validation route POST /api/v1/validate (EV-037 TD-3b)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Form, HTTPException

from src import api as api_surface
from src.schemas.validation import ValidateRequest, ValidateResponse, ValidationLayer
from src.utilities.conversion import ConversionError
from src.utilities.iwxxm_readable_decode import decode_for_validate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Validation"])


@router.post(
    "/validate",
    tags=["Validation"],
    response_model=ValidateResponse,
    responses={},
)
async def validate_comprehensive(
    request_body: ValidateRequest | None = None,
    manual_text: str = Form(default="", description="METAR TAC text to validate"),
    xml_content: str = Form(
        default="", description="Optional XML to validate (if omitted, TAC will be converted first)"
    ),
    iwxxm_version: str = Form(default="2025-2", description="Target IWXXM version"),
    layers: list[str] = Form(
        default=["ALL"],
        description="Validation layers to run (ALL, or specific: AIRPORT_ICAO, TAC_SYNTAX, XML_WELLFORMED, XML_SCHEMA, SCHEMATRON, GML_REFERENCES, WMO_CODELISTS)",
    ),
    stop_on_error: bool = Form(default=True, description="Stop at first blocking layer failure"),
    profile: str = Form(default="", description="Deprecated - use semantic_profile (legacy alias: annex3 or iwxxm_us)"),
    semantic_profile: str = Form(
        default="",
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, CA_ECCC, AU_BOM, or NZ_CAA_MET; aliases annex3 / iwxxm_us accepted)",
    ),
    exchange_profile: str = Form(
        default="",
        description="Exchange packaging profile (e.g. GLOBAL_AFS); ignored on validate-only paths",
    ),
    extensions: list[str] = Form(
        default=[],
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
    ),
    product: str = Form(
        default="METAR",
        description="TAC product for Canadian extension XSD when extensions include IWXXM_CA",
    ),
) -> object:
    """Perform comprehensive 7-layer IWXXM validation.

    Validates METAR TAC input through all 7 validation layers:

    1. **Layer 1 (AIRPORT_ICAO)**: Validates ICAO airport code against database
    2. **Layer 2 (TAC_SYNTAX)**: Validates TAC/METAR syntax basics
    3. **Layer 3 (XML_WELLFORMED)**: Checks XML is well-formed
    4. **Layer 4 (XML_SCHEMA)**: Validates against official IWXXM XSD schemas
    5. **Layer 5 (SCHEMATRON)**: Validates business rules from official Schematron
    6. **Layer 6 (GML_REFERENCES)**: Validates GML internal references
    7. **Layer 7 (WMO_CODELISTS)**: Validates against official WMO RDF codelists

    **Authentication**: Public (no login required)

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
        json_profile = None
        json_semantic = None
        json_exchange = None
        json_extensions = None
        json_product = None
        extensions = api_surface._coerce_form_list(extensions)
        product = api_surface._coerce_form_str(product, "METAR")
        # Handle JSON request body
        if request_body is not None:
            xml_content = request_body.iwxxm_xml
            iwxxm_version = request_body.version
            validation_level = request_body.validation_level or "comprehensive"
            json_profile = request_body.profile
            json_semantic = getattr(request_body, "semantic_profile", None)
            json_exchange = getattr(request_body, "exchange_profile", None)
            json_extensions = getattr(request_body, "extensions", None)
            json_product = getattr(request_body, "product", None)
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

        wire = api_surface._resolve_request_profiles(
            route="/api/v1/validate",
            profile=profile,
            semantic_profile=semantic_profile,
            exchange_profile=exchange_profile,
            json_profile=json_profile,
            json_semantic_profile=json_semantic,
            json_exchange_profile=json_exchange,
        )
        profile = wire.emit_key

        resolved_extensions = api_surface._resolve_request_extensions(extensions, json_extensions)
        validate_product = api_surface.normalize_api_product(
            json_product if json_product is not None else product,
            default="METAR",
        )

        # Normalize version
        try:
            from src.config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version
        except ImportError:
            from config.iwxxm_versions import get_version_config_for_emit_profile, normalize_version

        iwxxm_version = normalize_version(iwxxm_version)

        # Validate version is supported
        try:
            get_version_config_for_emit_profile(iwxxm_version, profile)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        # Convert TAC to XML if not provided (forward profile; validate afterward)
        if not xml_content:
            try:
                xml_content, _ = api_surface.convert_metar_tac_with_metadata(
                    manual_text,
                    iwxxm_version=iwxxm_version,
                    validate=False,
                    profile=profile or "annex3",
                )
            except ConversionError as e:
                raise HTTPException(status_code=400, detail=f"Failed to convert TAC to XML: {e!s}") from e

        # Thin wrapper: always invoke packages/iwxxm-validate (TC-F6-033 / ADR-015)
        validation_level_name = ""
        if request_body is not None:
            validation_level_name = request_body.validation_level or "comprehensive"
        if validation_level_name == "schematron" or layers == ["SCHEMATRON"]:
            pkg_levels: tuple[str, ...] = ("schematron",)
        elif validation_level_name == "schema" or layers == ["XML_WELLFORMED", "XML_SCHEMA"]:
            pkg_levels = ("xsd",)
        else:
            pkg_levels = ("xsd", "schematron")

        pkg_report = api_surface._call_iwxxm_validate(
            xml_content,
            iwxxm_version=iwxxm_version,
            profile=profile or "annex3",
            levels=pkg_levels,
            emit_key=profile or "annex3",
            extensions=resolved_extensions,
            product=validate_product,
        )

        # Parse layer selection
        selected_layers: list[Any] = []
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
                        f"Valid options: {[l.name for l in ValidationLayer]}",
                    ) from KeyError

        # F11.4 / T3.8: skip orchestrator XSD+Schematron when the package SDK already ran them.
        skip_heavy: set[ValidationLayer] = set()
        if "xsd" in pkg_levels:
            skip_heavy.add(ValidationLayer.XML_SCHEMA)
        if "schematron" in pkg_levels:
            skip_heavy.add(ValidationLayer.SCHEMATRON)
        orch_layers = [layer for layer in selected_layers if layer not in skip_heavy]

        # Run remaining (non-duplicated) orchestrator layers
        orchestrator = api_surface.get_validation_orchestrator()
        result = orchestrator.validate_complete(
            tac_text=manual_text,
            xml_content=xml_content,
            version=iwxxm_version,
            layers=orch_layers,
            stop_on_error=stop_on_error,
        )

        # Format response (HTTP shape unchanged; package metadata additive)
        payload: dict[str, Any] = {
            "is_valid": result.is_valid,
            "version": result.version,
            "profile": profile or "annex3",
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
                    "code": issue.code,
                }
                for issue in result.all_issues
            ],
            "issues_by_layer": {
                layer.name: [
                    {
                        "level": issue.level.name,
                        "message": issue.message,
                        "location": issue.location,
                        "code": issue.code,
                    }
                    for issue in issues
                ]
                for layer, issues in result.issues_by_layer.items()
            },
            "stopped_at_layer": result.stopped_at_layer.name if result.stopped_at_layer else None,
            "package_ok": pkg_report.ok,
            "package_issues": [api_surface._package_issue_payload(issue) for issue in pkg_report.issues],
        }
        package_stages = api_surface._package_stages_payload(pkg_report)
        if package_stages is not None:
            payload["package_stages"] = package_stages
        if resolved_extensions:
            payload["extensions"] = resolved_extensions
        decoded = decode_for_validate(xml_content=xml_content, manual_text=manual_text)
        if decoded.segments:
            payload["segments"] = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "code": seg.code,
                    "explanation": seg.explanation,
                }
                for seg in decoded.segments
            ]
            if decoded.summary:
                payload["summary"] = decoded.summary
        return api_surface.msgspec_json_response(payload)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {e!s}") from e
