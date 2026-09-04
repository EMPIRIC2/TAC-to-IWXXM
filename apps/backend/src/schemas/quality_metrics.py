"""OpenAPI / response models for public quality-metrics routes (F7.q / EV-054)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QualityMetricsSummaryModel(BaseModel):
    """Per-product aggregate counts for the corpus browser."""

    product: str
    match_pass: int = 0
    match_fail: int = 0
    residual_nonempty: int = 0
    lint_fail: int = 0
    validate_fail: int = 0
    deferred_gaps: int = 0


class QualityMetricsFileRowModel(BaseModel):
    """Slim inventory row for the corpus file list."""

    stem: str
    product: str
    tier: str
    match_status: str
    residual_count: int = 0
    lint_error_count: int = 0
    validate_error_count: int = 0
    deferred: bool = False


class QualityMetricsListResponse(BaseModel):
    """Response for GET /api/v1/quality-metrics."""

    generated_at: str
    iwxxm_pin: str
    summaries: list[QualityMetricsSummaryModel] = Field(default_factory=list)
    files: list[QualityMetricsFileRowModel] = Field(default_factory=list)


class QualityMetricsDetailResponse(BaseModel):
    """Response for GET /api/v1/quality-metrics/{stem}."""

    stem: str
    product: str
    tier: str
    deferred: bool = False
    deferral_reason: str | None = None
    tac: str = ""
    official_xml: str = ""
    converted_xml: str = ""
    match_status: str
    residuals: list[dict[str, Any]] = Field(default_factory=list)
    residuals_propagated_to_remarks: bool = False
    lint_issues: list[dict[str, Any]] = Field(default_factory=list)
    validate_issues: list[dict[str, Any]] = Field(default_factory=list)
