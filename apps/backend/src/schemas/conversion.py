"""Pydantic schemas for METAR conversion API responses."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ConversionIssueSeverity(str, Enum):
    """Severity level for conversion and validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ConversionIssue(BaseModel):
    """Structured issue for a single conversion input item."""

    source: str = Field(
        ...,
        description="Input source identifier (e.g., 'manual_input' or filename)",
        examples=["manual_input", "EGLL_231750Z.txt"],
    )
    message: str = Field(..., description="Human-readable issue message", min_length=1)
    hint: Optional[str] = Field(
        None,
        description="Concise suggested fix for the user",
        examples=["Start the report with METAR or SPECI and a valid ICAO code"],
    )
    code: Optional[str] = Field(
        None,
        description="Machine-readable issue code",
        examples=["MISSING_KEYWORD", "INVALID_ICAO_FORMAT"],
    )
    severity: ConversionIssueSeverity = Field(
        default=ConversionIssueSeverity.ERROR,
        description="Issue severity",
    )
    layer: Optional[str] = Field(
        None,
        description="Validation layer associated with the issue",
        examples=["airport_icao", "tac_syntax"],
    )
    location: Optional[str] = Field(
        None,
        description="Optional location context from parser/validator",
        examples=["line 1, column 12"],
    )


class ConversionResult(BaseModel):
    """Individual conversion result for a single METAR input."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "KJFK_231751Z.txt",
                "content": "<?xml version='1.0' encoding='utf-8'?>\n<iwxxm:METAR gml:id='METAR_KJFK_231751Z'>\n  <iwxxm:issueTime>\n    <gml:TimeInstant gml:id='TP1'>\n      <gml:timePosition>2023-09-23T17:51:00Z</gml:timePosition>\n    </gml:TimeInstant>\n  </iwxxm:issueTime>\n</iwxxm:METAR>",
                "source": "file",
                "size_bytes": 1452,
            }
        }
    )

    name: str = Field(
        ..., description="Output filename for this conversion", examples=["manual_input.txt", "KJFK_231751Z.txt"]
    )
    content: str = Field(
        ...,
        description="Complete IWXXM XML document as UTF-8 text",
        min_length=1,
    )
    source: str = Field(
        ...,
        description="Source of input: 'manual' for text input, filename for uploads",
        examples=["manual", "KJFK.txt"],
    )
    size_bytes: int = Field(..., description="Output XML document size in bytes", ge=0, examples=[1452, 2048])


class ConversionResponse(BaseModel):
    """Response from conversion endpoint with results and errors."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "name": "manual_input.txt",
                        "content": "<?xml version='1.0' encoding='utf-8'?>...",
                        "source": "manual",
                        "size_bytes": 1452,
                    },
                    {
                        "name": "EGLL_231750Z.txt",
                        "content": "<?xml version='1.0' encoding='utf-8'?>...",
                        "source": "EGLL.txt",
                        "size_bytes": 1389,
                    },
                ],
                "errors": [],
                "issues": [],
                "total_processed": 2,
                "successful": 2,
                "failed": 0,
            }
        }
    )

    results: List[ConversionResult] = Field(
        default_factory=list, description="Successfully converted IWXXM XML documents"
    )
    errors: List[str] = Field(default_factory=list, description="Error messages for failed conversions")
    issues: List[ConversionIssue] = Field(
        default_factory=list,
        description="Structured issues (errors/warnings/info) for failed or partial conversions",
    )
    total_processed: int = Field(
        ..., ge=0, description="Total number of inputs processed (manual_text + files)", examples=[2, 5]
    )
    successful: int = Field(..., ge=0, description="Number of successful conversions", examples=[2, 4])
    failed: int = Field(..., ge=0, description="Number of failed conversions", examples=[0, 1])
    metadata: dict = Field(
        default_factory=dict,
        description="Echoed request metadata such as bulletin_id, issuing_center, and validation options",
    )


class ErrorDetail(BaseModel):
    """Detailed error response."""

    message: str
    errors: List[str] = Field(default_factory=list)
    issues: List[ConversionIssue] = Field(default_factory=list)
    total_errors: int = Field(..., ge=0)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    gifts_available: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service: str = Field(default="metar-to-iwxxm")


class ConversionRequest(BaseModel):
    """Request for METAR to IWXXM conversion via JSON body."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metars": [
                    "KJFK 121853Z 24008KT 10SM FEW250 M04/M17 A3034 RMK AO2 SLP279 T10441172",
                    "EGLL 121850Z 09012KT 9999 FEW040 05/M01 Q1023 NOSIG",
                ],
                "version": "2025-2",
                "validation_level": "comprehensive",
                "stop_on_error": False,
            }
        }
    )

    metars: List[str] = Field(
        default_factory=list,
        description="Optional list of METAR message strings to convert",
        max_length=1000,
        examples=[["KJFK 121853Z 24008KT 10SM FEW250 M04/M17 A3034"]],
    )
    version: str = Field(
        default="2025-2", description="Target IWXXM version", pattern=r"^\d{4}-\d+$", examples=["2025-2", "2023-1"]
    )
    validation_level: Optional[str] = Field(
        default="basic",
        description="Validation depth: 'basic', 'schema', 'schematron', 'icao_opmet', 'comprehensive'",
        examples=["basic", "comprehensive"],
    )
    stop_on_error: bool = Field(default=False, description="Stop processing on first error")
    bulletin_id: Optional[str] = Field(
        default=None,
        description="Optional bulletin identifier to associate with the request",
        examples=["SAAA00"],
    )
    issuing_center: Optional[str] = Field(
        default=None,
        description="Optional issuing centre ICAO location indicator",
        examples=["KWBC"],
    )
