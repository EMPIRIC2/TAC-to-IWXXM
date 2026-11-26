"""Domain/OpenAPI models for public station-health routes (F39)."""

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


class StationCentennialMetricModel(BaseModel):
    """
    One Centennial recognition-criteria proxy or insufficient-data row.

    Attributes
    ----------
    id : object
        Field ``id``.
    label : object
        Field ``label``.
    status : object
        Field ``status``.
    score : object
        Field ``score``.
    detail : object
        Field ``detail``.
    """

    id: str
    label: str
    status: str = Field(description="available or insufficient_data")
    score: float | None = None
    detail: str = ""


class StationListItemModel(BaseModel):
    """
    One station row on the dashboard list.

    Attributes
    ----------
    icao : object
        Field ``icao``.
    name : object
        Field ``name``.
    wmo_region : object
        Field ``wmo_region``.
    overall_grade : object
        Field ``overall_grade``.
    overall_score : object
        Field ``overall_score``.
    products : object
        Field ``products``.
    """

    icao: str
    name: str | None = None
    wmo_region: str = Field(
        default="unknown",
        description="WMO Regional Association id (I-VI) or unknown",
    )
    overall_grade: str
    overall_score: float = 0.0
    products: list[StationProductGradeModel] = Field(default_factory=list)
    maintenance_tag_counts: dict[str, int] = Field(default_factory=dict)
    file_format_counts: dict[str, int] = Field(default_factory=dict)
    issue_code_counts: dict[str, int] = Field(default_factory=dict)
    centennial_metrics: list[StationCentennialMetricModel] = Field(default_factory=list)


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
    maintenance_tag_counts: dict[str, int] = Field(default_factory=dict)
    file_format_counts: dict[str, int] = Field(default_factory=dict)
    issue_code_counts: dict[str, int] = Field(default_factory=dict)
    centennial_metrics: list[StationCentennialMetricModel] = Field(default_factory=list)


class StationHealthDetailResponse(BaseModel):
    """
    Response for GET /api/v1/station-health/{icao}.

    Attributes
    ----------
    icao : object
        Field ``icao``.
    name : object
        Field ``name``.
    wmo_region : object
        Field ``wmo_region``.
    windows : object
        Field ``windows``.
    record_count : object
        Field ``record_count``.
    """

    icao: str
    name: str | None = None
    wmo_region: str = Field(
        default="unknown",
        description="WMO Regional Association id (I-VI) or unknown",
    )
    windows: dict[str, StationWindowModel] = Field(default_factory=dict)
    record_count: int = 0
    maintenance_tag_counts: dict[str, int] = Field(default_factory=dict)
    file_format_counts: dict[str, int] = Field(default_factory=dict)
    issue_code_counts: dict[str, int] = Field(default_factory=dict)
    centennial_metrics: list[StationCentennialMetricModel] = Field(default_factory=list)


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


class StationEvalLintCodeModel(BaseModel):
    """
    One top lint code from the FR-045 live-eval snapshot.

    Attributes
    ----------
    code : str
        Lint or issue code.
    count : int
        Occurrences in the snapshot window.
    """

    code: str
    count: int = 0


class StationEvalFailureModel(BaseModel):
    """
    One failure location from the FR-045 live-eval snapshot.

    Attributes
    ----------
    place_key : str
        Station ICAO or place id.
    product : str
        Map product id.
    stage : str
        Failure stage (lint, convert, …).
    code : str
        Issue or failure code.
    """

    place_key: str
    product: str
    stage: str
    code: str


class StationEvalProductBreakdownModel(BaseModel):
    """
    Failure counts for one product in the eval-benchmark panel.

    Attributes
    ----------
    product : str
        Product id.
    failure_count : int
        Number of failure_locations rows for that product.
    """

    product: str
    failure_count: int = 0


class StationEvalIwxxmModel(BaseModel):
    """
    IWXXM validation rollup from the FR-045 snapshot.

    Attributes
    ----------
    pass_ : int
        Reports with IWXXM present (serialized as ``pass``).
    fail : int
        Convert or validation failures.
    skip : int
        Partial-decode / skipped counts.
    """

    pass_: int = Field(default=0, alias="pass")
    fail: int = 0
    skip: int = 0

    model_config = {"populate_by_name": True}


class StationHealthEvalBenchmarkResponse(BaseModel):
    """
    Response for GET /api/v1/station-health/eval-benchmark (FR-047 / FR-072).

    Surfaces the latest live-map evaluation snapshot for Station health, with
    optional ICAO-filtered failure locations and a product failure breakdown.

    Attributes
    ----------
    computed_at : str
        Snapshot timestamp (ISO-8601 Z).
    window_hours : int
        Eval window length in hours.
    products : list[str]
        Products present in the snapshot.
    partial_decode_count : int
        Partial-decode count.
    lint_count : int
        Lint issue count.
    top_lint_codes : list[StationEvalLintCodeModel]
        Top lint codes.
    convert_failure_count : int
        Convert failure count.
    iwxxm_validation : StationEvalIwxxmModel
        IWXXM pass/fail/skip rollup.
    failure_locations : list[StationEvalFailureModel]
        Failure rows (optionally ICAO-filtered).
    product_breakdown : list[StationEvalProductBreakdownModel]
        Failure counts by product.
    icao_filter : str | None
        Applied ICAO filter, if any.
    """

    computed_at: str
    window_hours: int = 24
    products: list[str] = Field(default_factory=list)
    partial_decode_count: int = 0
    lint_count: int = 0
    top_lint_codes: list[StationEvalLintCodeModel] = Field(default_factory=list)
    convert_failure_count: int = 0
    iwxxm_validation: StationEvalIwxxmModel = Field(default_factory=StationEvalIwxxmModel)
    failure_locations: list[StationEvalFailureModel] = Field(default_factory=list)
    product_breakdown: list[StationEvalProductBreakdownModel] = Field(default_factory=list)
    icao_filter: str | None = None
