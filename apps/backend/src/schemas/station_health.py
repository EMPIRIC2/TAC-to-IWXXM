"""OpenAPI models for public station-health routes (F39)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StationProductGradeModel(BaseModel):
    """
    One product grade inside a station window.

    Attributes
    ----------
    product : object
        Field ``product``.
    grade : object
        Field ``grade``.
    overall_score : object
        Field ``overall_score``.
    availability_score : object
        Field ``availability_score``.
    actual_count : object
        Field ``actual_count``.
    expected_count : object
        Field ``expected_count``.
    solidus_rate : object
        Field ``solidus_rate``.
    missing_digit_rate : object
        Field ``missing_digit_rate``.
    lint_severity_score : object
        Field ``lint_severity_score``.
    lint_error_count : object
        Field ``lint_error_count``.
    """

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
    """
    One station row on the dashboard list.

    Attributes
    ----------
    icao : object
        Field ``icao``.
    name : object
        Field ``name``.
    overall_grade : object
        Field ``overall_grade``.
    overall_score : object
        Field ``overall_score``.
    products : object
        Field ``products``.
    """

    icao: str
    name: str | None = None
    overall_grade: str
    overall_score: float = 0.0
    products: list[StationProductGradeModel] = Field(default_factory=list)


class StationHealthSummaryModel(BaseModel):
    """
    Rollup counts for the list response.

    Attributes
    ----------
    station_count : object
        Field ``station_count``.
    grade_counts : object
        Field ``grade_counts``.
    """

    station_count: int = 0
    grade_counts: dict[str, int] = Field(default_factory=dict)


class StationHealthListResponse(BaseModel):
    """
    Response for GET /api/v1/station-health.

    Attributes
    ----------
    window : object
        Field ``window``.
    computed_at : object
        Field ``computed_at``.
    stations : object
        Field ``stations``.
    summary : object
        Field ``summary``.
    """

    window: str
    computed_at: str
    stations: list[StationListItemModel] = Field(default_factory=list)
    summary: StationHealthSummaryModel = Field(default_factory=StationHealthSummaryModel)


class StationWindowModel(BaseModel):
    """
    One window block on the station detail page.

    Attributes
    ----------
    overall_grade : object
        Field ``overall_grade``.
    overall_score : object
        Field ``overall_score``.
    products : object
        Field ``products``.
    """

    overall_grade: str
    overall_score: float = 0.0
    products: list[StationProductGradeModel] = Field(default_factory=list)


class StationHealthDetailResponse(BaseModel):
    """
    Response for GET /api/v1/station-health/{icao}.

    Attributes
    ----------
    icao : object
        Field ``icao``.
    name : object
        Field ``name``.
    windows : object
        Field ``windows``.
    record_count : object
        Field ``record_count``.
    """

    icao: str
    name: str | None = None
    windows: dict[str, StationWindowModel] = Field(default_factory=dict)
    record_count: int = 0


class StationMetricDefinitionModel(BaseModel):
    """
    One extensible dashboard metric card.

    Attributes
    ----------
    id : object
        Field ``id``.
    label : object
        Field ``label``.
    description : object
        Field ``description``.
    unit : object
        Field ``unit``.
    higher_is_better : object
        Field ``higher_is_better``.
    """

    id: str
    label: str
    description: str
    unit: str | None = None
    higher_is_better: bool = True


class StationHealthMetricsResponse(BaseModel):
    """
    Response for GET /api/v1/station-health/metrics.

    Attributes
    ----------
    metrics : object
        Field ``metrics``.
    """

    metrics: list[StationMetricDefinitionModel] = Field(default_factory=list)
