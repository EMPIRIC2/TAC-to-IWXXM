"""
ICAO OPMET Data Exchange Guidelines (Section 7) - Translation Statistics Schemas.

Implements data models for tracking translation centre statistics as per
ICAO Doc 10003 - Manual on the Digital Exchange of Aeronautical Meteorological Information.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ICAORegion(str, Enum):
    """ICAO Regional Offices as per user decision 3."""
    AFI = "AFI"  # Africa-Indian Ocean
    APAC = "APAC"  # Asia Pacific
    ESAF = "ESAF"  # Eastern and Southern African
    EUR = "EUR"  # European
    MID = "MID"  # Middle East
    NAM = "NAM"  # North American
    NAT = "NAT"  # North Atlantic
    SAM = "SAM"  # South American
    WAFR = "WAFR"  # West African


class TranslationStatus(str, Enum):
    """Status of TAC to IWXXM translation."""
    SUCCESS = "success"
    PARTIAL = "partial"  # Translation completed with warnings
    FAILED = "failed"
    VALIDATION_ERROR = "validation_error"


class ValidationLayer(str, Enum):
    """7-layer IWXXM validation stages."""
    AIRPORT_ICAO = "AIRPORT_ICAO"
    TAC_SYNTAX = "TAC_SYNTAX"
    XML_WELLFORMED = "XML_WELLFORMED"
    XML_SCHEMA = "XML_SCHEMA"
    SCHEMATRON = "SCHEMATRON"
    GML_REFERENCES = "GML_REFERENCES"
    WMO_CODELISTS = "WMO_CODELISTS"


class TranslationRecord(BaseModel):
    """
    Individual translation record for ICAO OPMET statistics.

    Captures metadata about each TAC→IWXXM translation performed by the centre.
    Supports indefinite retention as per user decision 1.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "translation_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-02-13T10:30:00Z",
                "icao_airport_code": "KJFK",
                "icao_region": "NAM",
                "tac_message": "METAR KJFK 131051Z 31008KT 10SM FEW250 M04/M17 A3034",
                "iwxxm_version": "2025-2",
                "translation_status": "success",
                "validation_layers_passed": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA"],
                "translation_duration_ms": 245,
                "user_id": "auth-user-123",
            }
        }
    )

    # Primary identifiers
    translation_id: str = Field(
        ...,
        description="Unique UUID for this translation"
    )
    timestamp: datetime = Field(
        ...,
        description="Translation completion timestamp (ISO 8601)"
    )

    # Airport and region
    icao_airport_code: str = Field(
        ...,
        description="ICAO 4-letter airport identifier",
        min_length=4,
        max_length=4
    )
    icao_region: ICAORegion = Field(
        ...,
        description="ICAO regional office jurisdiction"
    )

    # Input/Output
    tac_message: str = Field(
        ...,
        description="Original TAC METAR message"
    )
    iwxxm_version: str = Field(
        ...,
        description="Target IWXXM version (2025-2 or 2023-1)"
    )
    iwxxm_output: Optional[str] = Field(
        default=None,
        description="Generated IWXXM XML (null if translation failed)"
    )

    # Translation result
    translation_status: TranslationStatus = Field(
        ...,
        description="Overall translation outcome"
    )
    validation_layers_passed: List[ValidationLayer] = Field(
        default_factory=list,
        description="Validation layers successfully passed"
    )
    validation_errors: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Validation errors by layer (if any)"
    )

    # Performance metrics
    translation_duration_ms: int = Field(
        ...,
        description="Translation processing time in milliseconds",
        ge=0
    )

    # User context
    user_id: Optional[str] = Field(
        default=None,
        description="Authenticated user ID (Supabase UUID)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="User session identifier"
    )

    # Translation Centre metadata
    translation_centre_designator: str = Field(
        default="NOAA-MDL",
        description="Translation centre designator (ICAO location indicator)"
    )
    bulletin_reception_time: Optional[datetime] = Field(
        default=None,
        description="Original bulletin reception time (if applicable)"
    )
    bulletin_id: Optional[str] = Field(
        default=None,
        description="WMO bulletin identifier (if applicable)"
    )


class TranslationStatistics(BaseModel):
    """
    Aggregated translation statistics for ICAO OPMET compliance.

    Provides summary metrics for a given time period and optional filters.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period_start": "2026-02-13T00:00:00Z",
                "period_end": "2026-02-13T23:59:59Z",
                "total_translations": 1547,
                "successful_translations": 1523,
                "failed_translations": 24,
                "success_rate": 98.45,
                "average_duration_ms": 237,
                "translations_by_region": {
                    "NAM": 892,
                    "EUR": 421,
                    "APAC": 234
                },
                "translations_by_version": {
                    "2025-2": 1501,
                    "2023-1": 46
                }
            }
        }
    )

    # Time period
    period_start: datetime = Field(
        ...,
        description="Statistics period start (ISO 8601)"
    )
    period_end: datetime = Field(
        ...,
        description="Statistics period end (ISO 8601)"
    )

    # Overall counts
    total_translations: int = Field(
        ...,
        description="Total number of translations in period",
        ge=0
    )
    successful_translations: int = Field(
        ...,
        description="Successfully completed translations",
        ge=0
    )
    failed_translations: int = Field(
        ...,
        description="Failed translations",
        ge=0
    )
    partial_translations: int = Field(
        default=0,
        description="Translations completed with warnings",
        ge=0
    )

    # Success metrics
    success_rate: float = Field(
        ...,
        description="Translation success rate (percentage)",
        ge=0,
        le=100
    )
    average_duration_ms: float = Field(
        ...,
        description="Average translation duration (milliseconds)",
        ge=0
    )
    median_duration_ms: Optional[float] = Field(
        default=None,
        description="Median translation duration (milliseconds)",
        ge=0
    )

    # Distribution breakdowns
    translations_by_region: Dict[ICAORegion, int] = Field(
        default_factory=dict,
        description="Translation count by ICAO region"
    )
    translations_by_version: Dict[str, int] = Field(
        default_factory=dict,
        description="Translation count by IWXXM version"
    )
    translations_by_airport: Optional[Dict[str, int]] = Field(
        default=None,
        description="Top airports by translation volume (optional)"
    )

    # Validation metrics
    validation_layer_success_rates: Dict[ValidationLayer, float] = Field(
        default_factory=dict,
        description="Success rate per validation layer (percentage)"
    )
    common_validation_errors: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Most frequent validation errors (optional)"
    )


class TranslationStatisticsRequest(BaseModel):
    """Request parameters for translation statistics query."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2026-02-01T00:00:00Z",
                "end_date": "2026-02-13T23:59:59Z",
                "icao_region": "NAM",
                "iwxxm_version": "2025-2",
                "include_airport_breakdown": True
            }
        }
    )

    start_date: datetime = Field(
        ...,
        description="Statistics period start (ISO 8601)"
    )
    end_date: datetime = Field(
        ...,
        description="Statistics period end (ISO 8601)"
    )
    icao_region: Optional[ICAORegion] = Field(
        default=None,
        description="Filter by ICAO region (optional)"
    )
    iwxxm_version: Optional[str] = Field(
        default=None,
        description="Filter by IWXXM version (optional)"
    )
    airport_code: Optional[str] = Field(
        default=None,
        description="Filter by specific airport (optional)",
        min_length=4,
        max_length=4
    )
    include_airport_breakdown: bool = Field(
        default=False,
        description="Include per-airport statistics"
    )
    include_error_details: bool = Field(
        default=False,
        description="Include detailed error analysis"
    )


class TranslationCentreInfo(BaseModel):
    """Translation Centre identification metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "centre_name": "NOAA Meteorological Development Laboratory",
                "centre_designator": "NOAA-MDL",
                "icao_location_indicator": "KWBC",
                "supported_iwxxm_versions": ["2025-2", "2023-1"],
                "supported_products": ["METAR", "SPECI"],
                "online_since": "2024-01-15T00:00:00Z"
            }
        }
    )

    centre_name: Optional[str] = Field(
        default=None,
        description="Full name of translation centre"
    )
    centre_designator: Optional[str] = Field(
        default=None,
        description="Short designator for translation centre"
    )
    icao_location_indicator: Optional[str] = Field(
        default=None,
        description="ICAO location indicator (CCCC)",
        min_length=4,
        max_length=4
    )
    supported_iwxxm_versions: List[str] = Field(
        ...,
        description="Supported IWXXM versions"
    )
    supported_products: List[str] = Field(
        default=["METAR", "SPECI"],
        description="Supported aviation product types"
    )
    online_since: Optional[datetime] = Field(
        default=None,
        description="Service start date (ISO 8601)"
    )
    contact_email: Optional[str] = Field(
        default=None,
        description="Technical contact email"
    )
