"""Public precomputed quality-metrics API (F7.q / EV-054 / #836)."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ..msgspec_http import msgspec_json_response
from ..quality_metrics_store import (
    QualityMetricsArtifactMissing,
    get_detail,
    list_file_rows,
    load_corpus_metrics,
)
from ..schemas.quality_metrics import (
    QualityMetricsDetailResponse,
    QualityMetricsFileRowModel,
    QualityMetricsListResponse,
    QualityMetricsSummaryModel,
)

router = APIRouter(prefix="/api/v1", tags=["Quality metrics"])


def _load_doc() -> dict[str, Any]:
    try:
        return load_corpus_metrics()
    except QualityMetricsArtifactMissing as exc:
        raise HTTPException(
            status_code=503,
            detail="Quality metrics are temporarily unavailable",
        ) from exc


@router.get(
    "/quality-metrics",
    response_model=QualityMetricsListResponse,
    summary="List corpus quality metrics",
)
async def list_quality_metrics(
    product: str | None = Query(
        default=None,
        description="Optional product filter (e.g. metar, taf, sigmet)",
    ),
) -> Response:
    """Serve product summaries and file inventory from the precomputed artifact."""
    doc = _load_doc()
    files = list_file_rows(doc, product=product)
    summaries_raw = cast(list[dict[str, Any]], doc.get("summaries") or [])
    if product:
        key = product.strip().lower()
        summaries_raw = [s for s in summaries_raw if str(s.get("product", "")).lower() == key]
    body = QualityMetricsListResponse(
        generated_at=str(doc.get("generated_at", "")),
        iwxxm_pin=str(doc.get("iwxxm_pin", "")),
        summaries=[QualityMetricsSummaryModel(**s) for s in summaries_raw],
        files=[QualityMetricsFileRowModel(**f) for f in files],
    )
    return msgspec_json_response(body)


@router.get(
    "/quality-metrics/{stem}",
    response_model=QualityMetricsDetailResponse,
    summary="Corpus quality metrics for one stem",
)
async def get_quality_metrics_detail(stem: str) -> Response:
    """Serve per-stem TAC / XML / match / residual / lint / validate detail."""
    doc = _load_doc()
    detail = get_detail(doc, stem)
    if detail is None:
        raise HTTPException(status_code=404, detail="Unknown quality metrics stem")
    body = QualityMetricsDetailResponse(
        stem=str(detail.get("stem", stem)),
        product=str(detail.get("product", "")),
        tier=str(detail.get("tier", "")),
        deferred=bool(detail.get("deferred", False)),
        deferral_reason=detail.get("deferral_reason"),
        tac=str(detail.get("tac", "")),
        official_xml=str(detail.get("official_xml", "")),
        converted_xml=str(detail.get("converted_xml", "")),
        match_status=str(detail.get("match_status", "")),
        residuals=list(detail.get("residuals") or []),
        lint_issues=list(detail.get("lint_issues") or []),
        validate_issues=list(detail.get("validate_issues") or []),
    )
    return msgspec_json_response(body)
