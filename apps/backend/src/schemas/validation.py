"""Pydantic schemas for validation results and requests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ValidationLevel(StrEnum):
    """Severity level for validation issues."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Alias for compatibility with validation modules
ValidationSeverity = ValidationLevel


class ValidationLayer(StrEnum):
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
    location: str | None = Field(default=None, description="Location in document")
    code: str | None = Field(default=None, description="Machine-readable error code")
    suggestion: str | None = Field(default=None, description="Suggested fix")


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
    issues: list[ValidationIssue] = Field(default_factory=list, description="List of issues")
    execution_time_ms: float | None = Field(default=None, description="Execution time in ms", ge=0)
    validated_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    metadata: dict[str, Any] | None = Field(default=None, description="Layer-specific metadata")

    def add_issue(
        self,
        level: ValidationLevel,
        message: str,
        location: str | None = None,
        code: str | None = None,
        suggestion: str | None = None,
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


@dataclass
class XSDValidationResult:
    """Result of XSD schema validation (layer 4)."""

    is_valid: bool
    issues: list[ValidationIssue]
    schema_version: str


@dataclass
class SchematronValidationResult:
    """Result of Schematron validation (layer 5)."""

    is_valid: bool
    issues: list[ValidationIssue]
    schema_version: str
    rules_evaluated: int = 0


@dataclass
class GMLValidationResult:
    """Result of GML reference validation (layer 6)."""

    is_valid: bool
    issues: list[ValidationIssue]
    total_ids: int = 0
    total_references: int = 0
    broken_references: int = 0


@dataclass
class CodelistValidationResult:
    """Result of WMO codelist validation (layer 7)."""

    is_valid: bool
    issues: list[ValidationIssue]
    total_references: int = 0
    invalid_references: int = 0


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
                "validated_at": "2026-02-10T14:30:45.123456",
            }
        }
    )

    passed: bool = Field(..., description="Whether all layers passed")
    layers_validated: list[ValidationLayer] = Field(..., description="Layers validated")
    total_issues: int = Field(0, description="Total issues", ge=0)
    results: list[ValidationResult] = Field(default_factory=list)
    execution_time_ms: float = Field(0, ge=0)
    validated_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    @classmethod
    def from_results(cls, results: list[ValidationResult]) -> AggregatedValidationResult:
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


class TaskStatus(StrEnum):
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
    result: AggregatedValidationResult | None = Field(None)
    error: str | None = Field(None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    completed_at: datetime | None = Field(None)
    expires_at: datetime | None = Field(None)


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
        examples=["METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005 RMK AO2"],
    )
    content_type: str = Field(
        "tac", description="Content type: 'tac' (METAR TAC) or 'xml' (IWXXM XML)", examples=["tac", "xml"]
    )
    layers: list[ValidationLayer] | None = Field(None, description="Specific layers to validate (None = all layers)")
    iwxxm_version: str | None = Field(None, description="IWXXM version for validation context", examples=["3.0.1"])


class ValidateRequest(BaseModel):
    """Request for IWXXM validation via JSON body."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "iwxxm_xml": "<?xml version='1.0'?><iwxxm:METAR>...</iwxxm:METAR>",
                "version": "2025-2",
                "validation_level": "comprehensive",
                "stop_on_error": False,
            }
        }
    )

    iwxxm_xml: str = Field(
        ...,
        description="IWXXM XML content to validate",
        min_length=1,
        examples=["<?xml version='1.0'?><iwxxm:METAR>...</iwxxm:METAR>"],
    )
    version: str = Field(
        default="2025-2", description="Target IWXXM version", pattern=r"^\d{4}-\d+$", examples=["2025-2", "2023-1"]
    )
    validation_level: str | None = Field(
        default="comprehensive",
        description="Validation depth: 'basic', 'schema', 'schematron', 'icao_opmet', 'comprehensive'",
        examples=["basic", "comprehensive"],
    )
    stop_on_error: bool = Field(default=False, description="Stop processing on first error")
    profile: str = Field(
        default="",
        description="Deprecated - use semantic_profile (legacy alias: annex3 or iwxxm_us)",
        examples=["annex3", "iwxxm_us"],
    )
    semantic_profile: str | None = Field(
        default=None,
        description="Semantic profile id (e.g. ICAO_2025, US_FAA_NWS, or CA_ECCC)",
        examples=["ICAO_2025", "US_FAA_NWS", "CA_ECCC"],
    )
    exchange_profile: str | None = Field(
        default=None,
        description="Exchange packaging profile (e.g. GLOBAL_AFS)",
        examples=["GLOBAL_AFS"],
    )
    extensions: list[str] | None = Field(
        default=None,
        description="Optional national extension tokens (e.g. IWXXM_CA for full Canadian validate stack)",
        examples=[["IWXXM_CA"]],
    )
    product: str | None = Field(
        default=None,
        description="TAC product for Canadian extension XSD selection when extensions include IWXXM_CA",
        examples=["METAR", "TAF"],
    )


class LintIssueModel(BaseModel):
    """HTTP DTO for a tac-validate issue (msgspec → pydantic)."""

    severity: str
    code: str
    message: str
    location: str | None = None
    start: int | None = Field(default=None, description="Inclusive character offset")
    end: int | None = Field(default=None, description="Exclusive character offset")


class LintFixModel(BaseModel):
    """HTTP DTO for an optional tac-validate fix suggestion."""

    code: str
    message: str
    replacement: str


class LintTacResponse(BaseModel):
    """Response for POST /api/v1/lint-tac."""

    ok: bool
    issues: list[LintIssueModel] = Field(default_factory=list)
    fixes: list[LintFixModel] = Field(default_factory=list)
    product: str | None = None


class LintIssueCatalogEntryModel(BaseModel):
    """One registry row exported by GET /api/v1/lint-issue-catalog."""

    code: str
    severity: str
    message_template: str
    product: str | None = None
    tags: list[str] = Field(default_factory=list)
    source_id: str | None = None
    source_url: str | None = None
    source_attribution: str | None = None
    # Additive EV-061 / #1014 (optional; older clients ignore).
    family: str | None = Field(
        default=None,
        description="lint (TAC registry) or iwxxm (validation checks)",
    )
    source_type: str | None = Field(
        default=None,
        description="tier1, tier2, or tier3 source policy",
    )
    status: str | None = Field(
        default=None,
        description="verified, legacy_alias, or semantic_only",
    )
    semantic_identifier: str | None = Field(
        default=None,
        description="Vocabulary concept path when href is a verified landing",
    )
    last_verified: str | None = Field(
        default=None,
        description="ISO date of last HTTP check for operator source_url",
    )
    replacement_url: str | None = Field(
        default=None,
        description="Verified landing when source_url is a legacy alias",
    )
    # Additive EV-062 / #1017 (optional; older clients ignore).
    issue_type: str | None = Field(
        default=None,
        description="Closed vocabulary: presence, structure, content, consistency, iwxxm_schema, other",
    )
    source_locator: str | None = Field(
        default=None,
        description="Section/table/page locator for the cited source",
    )
    source_access: str | None = Field(
        default=None,
        description="Operator access tier: public, paywall, login, semantic_only",
    )


class LintIssueCatalogResponse(BaseModel):
    """Response for GET /api/v1/lint-issue-catalog."""

    issues: list[LintIssueCatalogEntryModel] = Field(default_factory=list)


class DecodeSegmentModel(BaseModel):
    """HTTP DTO for one TAC decode/annotate segment."""

    start: int
    end: int
    code: str
    explanation: str


class DecodeResidualModel(BaseModel):
    """HTTP DTO for an undecoded TAC span (explicit residuals - G4)."""

    start: int
    end: int
    text: str


class DecodeTacResponse(BaseModel):
    """Response for POST /api/v1/decode-tac."""

    product: str
    segments: list[DecodeSegmentModel] = Field(default_factory=list)
    residuals: list[DecodeResidualModel] = Field(default_factory=list)
    summary: str = Field(
        default="",
        description="Deterministic plain-language paragraph of the report",
    )


class PackageIssueModel(BaseModel):
    """HTTP DTO for an iwxxm-validate package finding (additive on /validate)."""

    layer: str
    severity: str
    message: str
    location: str | None = None
    code: str | None = None
    start: int | None = Field(default=None, description="Inclusive offset when known")
    end: int | None = Field(default=None, description="Exclusive offset when known")


class PackageStageModel(BaseModel):
    """Per-stage CA_ECCC validation outcome (additive on /validate)."""

    stage: str
    label: str
    ok: bool
    issues: list[PackageIssueModel] = Field(default_factory=list)


class ValidateIssueModel(BaseModel):
    """HTTP DTO for a validation orchestrator finding on /validate."""

    layer: str
    level: str
    message: str
    location: str | None = None
    code: str | None = None
    start: int | None = Field(default=None, description="Inclusive offset when known")
    end: int | None = Field(default=None, description="Exclusive offset when known")


class ValidateLayerIssueModel(BaseModel):
    """Per-layer issue entry nested under ``issues_by_layer``."""

    level: str
    message: str
    location: str | None = None
    code: str | None = None


class ValidateResponse(BaseModel):
    """Response for POST /api/v1/validate (validation layers + package_* extras)."""

    is_valid: bool
    version: str
    profile: str = "annex3"
    layers_run: list[str] = Field(default_factory=list)
    layers_passed: list[str] = Field(default_factory=list)
    layers_failed: list[str] = Field(default_factory=list)
    total_issues: int = 0
    issues: list[ValidateIssueModel] = Field(default_factory=list)
    issues_by_layer: dict[str, list[ValidateLayerIssueModel]] = Field(default_factory=dict)
    stopped_at_layer: str | None = None
    package_ok: bool = True
    package_issues: list[PackageIssueModel] = Field(default_factory=list)
    package_stages: list[PackageStageModel] | None = Field(
        default=None,
        description=(
            "Optional per-stage breakdown from iwxxm-validate when profile=ca_eccc and extensions include IWXXM_CA"
        ),
    )
    extensions: list[str] | None = Field(
        default=None,
        description="Resolved national extension tokens from the request (when supplied)",
    )
    segments: list[DecodeSegmentModel] | None = Field(
        default=None,
        description=(
            "Optional item-by-item decode rows (code and explanation) when a readable decode exists. "
            "Omitted when there is no decode."
        ),
    )
    summary: str | None = Field(
        default=None,
        description=(
            "Optional plain-language paragraph of the decoded report when a readable decode exists. "
            "Omitted when there is no decode."
        ),
    )


class BulletinMetaModel(BaseModel):
    """HTTP DTO for WMO AHL metadata on convert-bulletin (api-contract Q6/Q7)."""

    ahl: str
    report_count: int
    tt: str
    aa: str
    cccc: str
    yygggg: str
    bbb: str | None = None
    report_status: str | None = None


class BulletinReportResultModel(BaseModel):
    """Per-report convert-bulletin result (partial success allowed)."""

    report_index: int
    ok: bool
    tac_input: str
    xml: str | None = None
    issues: list[LintIssueModel] = Field(default_factory=list)
    fixes: list[LintFixModel] = Field(default_factory=list)


class ConvertBulletinResponse(BaseModel):
    """Response for POST /api/v1/convert-bulletin."""

    bulletin_meta: BulletinMetaModel
    exchange_profile: str | None = Field(
        default=None,
        description="Resolved exchange packaging profile (default GLOBAL_AFS on this route)",
    )
    results: list[BulletinReportResultModel] = Field(default_factory=list)
