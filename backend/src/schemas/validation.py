"""Pydantic schemas for validation results and requests."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ValidationLevel(str, Enum):
    """Severity level for validation issues."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Alias for compatibility with validation modules
ValidationSeverity = ValidationLevel


class ValidationLayer(str, Enum):
    """Validation layer identifiers."""

    AIRPORT_ICAO = "airport_icao"
    TAC_SYNTAX = "tac_syntax"
    XML_WELLFORMED = "xml_wellformed"
    XML_SCHEMA = "xml_schema"
    SCHEMATRON = "schematron"
    GML_REFERENCES = "gml_references"
    WMO_CODELISTS = "wmo_codelists"


class ValidationIssue(BaseModel):
    """Single validation issue with context."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "layer": "airport_icao",
                "level": "error",
                "message": "Unknown ICAO code: ZZZZ",
                "location": "line 1, column 12",
                "code": "INVALID_ICAO",
            }
        }
    )

    layer: ValidationLayer = Field(..., description="Validation layer that found this issue")
    level: ValidationLevel = Field(..., description="Severity level")
    message: str = Field(..., description="Human-readable error message", min_length=1)
    location: Optional[str] = Field(None, description="Location in document")
    code: Optional[str] = Field(None, description="Machine-readable error code")
    suggestion: Optional[str] = Field(None, description="Suggested fix")


class ValidationResult(BaseModel):
    """Result from a validation operation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "passed": True,
                "layer": "airport_icao",
                "issues": [],
                "execution_time_ms": 12.5,
            }
        }
    )

    passed: bool = Field(..., description="Whether validation passed")
    layer: ValidationLayer = Field(..., description="Validation layer")
    issues: List[ValidationIssue] = Field(default_factory=list, description="List of issues")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in ms", ge=0)
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(None, description="Layer-specific metadata")

    def add_issue(
        self,
        level: ValidationLevel,
        message: str,
        location: Optional[str] = None,
        code: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add a validation issue."""
        issue = ValidationIssue(
            layer=self.layer,
            level=level,
            message=message,
            location=location,
            code=code,
            suggestion=suggestion,
        )
        self.issues.append(issue)
        if level in (ValidationLevel.CRITICAL, ValidationLevel.ERROR):
            self.passed = False


class AggregatedValidationResult(BaseModel):
    """Combined results from multiple validation layers."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "passed": False,
                "layers_validated": ["airport_icao", "tac_syntax", "xml_wellformed"],
                "total_issues": 2,
                "results": [
                    {
                        "passed": True,
                        "layer": "airport_icao",
                        "issues": [],
                        "execution_time_ms": 5.2,
                    },
                    {
                        "passed": False,
                        "layer": "tac_syntax",
                        "issues": [
                            {
                                "layer": "tac_syntax",
                                "level": "error",
                                "message": "Invalid TAC format: missing wind speed",
                                "location": "line 1, column 18",
                                "code": "INVALID_TAC_FORMAT",
                                "suggestion": "Check wind speed component",
                            }
                        ],
                        "execution_time_ms": 8.3,
                    },
                ],
                "execution_time_ms": 13.5,
                "validated_at": "2026-02-10T14:30:45.123456"
            }
        }
    )

    passed: bool = Field(..., description="Whether all layers passed")
    layers_validated: List[ValidationLayer] = Field(..., description="Layers validated")
    total_issues: int = Field(0, description="Total issues", ge=0)
    results: List[ValidationResult] = Field(default_factory=list)
    execution_time_ms: float = Field(0, ge=0)
    validated_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_results(cls, results: List[ValidationResult]) -> AggregatedValidationResult:
        """Create aggregated result from individual layer results."""
        passed = all(r.passed for r in results)
        total_issues = sum(len(r.issues) for r in results)
        layers = [r.layer for r in results]
        total_time = sum(r.execution_time_ms or 0 for r in results)
        
        return cls(
            passed=passed,
            layers_validated=layers,
            total_issues=total_issues,
            results=results,
            execution_time_ms=total_time,
        )


class TaskStatus(str, Enum):
    """Status of async validation task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ValidationTask(BaseModel):
    """Async validation task tracking."""

    task_id: str = Field(..., description="Unique task ID")
    status: TaskStatus = Field(..., description="Current status")
    result: Optional[AggregatedValidationResult] = Field(None)
    error: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    expires_at: Optional[datetime] = Field(None)


class ValidationRequest(BaseModel):
    """Request for validation operation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2",
                "content_type": "tac",
                "layers": ["airport_icao", "tac_syntax"],
                "iwxxm_version": "3.0.1",
            }
        }
    )

    content: str = Field(
        ...,
        description="Content to validate (METAR TAC or IWXXM XML)",
        min_length=1,
        examples=["METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2"]
    )
    content_type: str = Field(
        "tac",
        description="Content type: 'tac' (METAR TAC) or 'xml' (IWXXM XML)",
        examples=["tac", "xml"]
    )
    layers: Optional[List[ValidationLayer]] = Field(
        None,
        description="Specific layers to validate (None = all layers)"
    )
    iwxxm_version: Optional[str] = Field(
        None,
        description="IWXXM version for validation context",
        examples=["3.0.1"]
    )


class ValidateRequest(BaseModel):
    """Request for IWXXM validation via JSON body."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "iwxxm_xml": "<?xml version='1.0'?><iwxxm:METAR>...</iwxxm:METAR>",
                "version": "2025-2",
                "validation_level": "comprehensive",
                "stop_on_error": False
            }
        }
    )

    iwxxm_xml: str = Field(
        ...,
        description="IWXXM XML content to validate",
        min_length=1,
        examples=["<?xml version='1.0'?><iwxxm:METAR>...</iwxxm:METAR>"]
    )
    version: str = Field(
        default="2025-2",
        description="Target IWXXM version",
        pattern=r"^\d{4}-\d+$",
        examples=["2025-2", "2023-1"]
    )
    validation_level: Optional[str] = Field(
        default="comprehensive",
        description="Validation depth: 'basic', 'schema', 'schematron', 'icao_opmet', 'comprehensive'",
        examples=["basic", "comprehensive"]
    )
    stop_on_error: bool = Field(
        default=False,
        description="Stop processing on first error"
    )
