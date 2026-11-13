"""OpenAPI models for public station-health routes (F39)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StationProductGradeModel(BaseModel):
    """One product grade inside a station window."""

    product: str
    grade: str
    overall_score: float = 0.0
    availability_score: float = 0.0
    actual_count: int = 0
    expected_count: int = 0
    solidus_rate: float = 0.0
    missing_digit_rate: float = 0.0
    lint_severity_score: float = 100.0
    lint_error_count: int = 0


class StationListItemModel(BaseModel):
    """One station row on the dashboard list."""

    icao: str
    name: str | None = None
    overall_grade: str
    overall_score: float = 0.0
    products: list[StationProductGradeModel] = Field(default_factory=list)


class StationHealthSummaryModel(BaseModel):
    """Rollup counts for the list response."""

    station_count: int = 0
    grade_counts: dict[str, int] = Field(default_factory=dict)


class StationHealthListResponse(BaseModel):
    """Response for GET /api/v1/station-health."""

    window: str
    computed_at: str
    stations: list[StationListItemModel] = Field(default_factory=list)
    summary: StationHealthSummaryModel = Field(default_factory=StationHealthSummaryModel)


class StationWindowModel(BaseModel):
    """One window block on the station detail page."""

    overall_grade: str
    overall_score: float = 0.0
    products: list[StationProductGradeModel] = Field(default_factory=list)


class StationHealthDetailResponse(BaseModel):
    """Response for GET /api/v1/station-health/{icao}."""

    icao: str
    name: str | None = None
    windows: dict[str, StationWindowModel] = Field(default_factory=dict)
    record_count: int = 0


class StationMetricDefinitionModel(BaseModel):
    """One extensible dashboard metric card."""

    id: str
    label: str
    description: str
    unit: str | None = None
    higher_is_better: bool = True


class StationHealthMetricsResponse(BaseModel):
    """Response for GET /api/v1/station-health/metrics."""

    metrics: list[StationMetricDefinitionModel] = Field(default_factory=list)
