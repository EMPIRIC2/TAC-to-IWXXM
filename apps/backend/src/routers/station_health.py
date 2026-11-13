"""Public station health dashboard API (F39)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.schemas.station_health import (
    StationHealthDetailResponse,
    StationHealthListResponse,
    StationHealthMetricsResponse,
    StationHealthSummaryModel,
    StationListItemModel,
    StationMetricDefinitionModel,
    StationProductGradeModel,
    StationWindowModel,
)
from src.services.station_health_metrics import WINDOW_SECONDS
from src.services.station_health_store import get_station_health_store

router = APIRouter(prefix="/api/v1", tags=["Station health"])


def _product_models(raw_products: list[dict]) -> list[StationProductGradeModel]:
    return [StationProductGradeModel(**item) for item in raw_products]


@router.get(
    "/station-health/metrics",
    response_model=StationHealthMetricsResponse,
    summary="List station health metric definitions",
)
def list_station_health_metrics() -> StationHealthMetricsResponse:
    """Serve the extensible metrics registry for dashboard cards."""
    rows = get_station_health_store().list_metrics()
    metrics = [
        StationMetricDefinitionModel(
            id=str(row["id"]),
            label=str(row["label"]),
            description=str(row["description"]),
            unit=row.get("unit"),
            higher_is_better=bool(row.get("higher_is_better", True)),
        )
        for row in rows
    ]
    return StationHealthMetricsResponse(metrics=metrics)


@router.get(
    "/station-health",
    response_model=StationHealthListResponse,
    summary="List station health grades",
)
def list_station_health(
    window: str = Query(default="6h", description="Time window: 6h, 1d, or 30d"),
    product: str | None = Query(default=None, description="Optional product filter"),
    grade: str | None = Query(default=None, description="Optional letter grade filter"),
    limit: int = Query(default=100, ge=1, le=500, description="Max stations to return"),
) -> StationHealthListResponse:
    """Serve station report cards for one availability window."""
    window_key = window.strip().lower()
    if window_key not in WINDOW_SECONDS:
        raise HTTPException(status_code=400, detail="Window must be 6h, 1d, or 30d")
    payload = get_station_health_store().list_stations(
        window_key=window_key,
        product=product,
        grade=grade,
        limit=limit,
    )
    stations = [
        StationListItemModel(
            icao=item["icao"],
            name=item.get("name"),
            overall_grade=item["overall_grade"],
            overall_score=float(item["overall_score"]),
            products=_product_models(list(item.get("products") or [])),
        )
        for item in payload["stations"]
    ]
    summary_raw = payload.get("summary") or {}
    return StationHealthListResponse(
        window=str(payload["window"]),
        computed_at=str(payload["computed_at"]),
        stations=stations,
        summary=StationHealthSummaryModel(
            station_count=int(summary_raw.get("station_count") or 0),
            grade_counts=dict(summary_raw.get("grade_counts") or {}),
        ),
    )


@router.get(
    "/station-health/{icao}",
    response_model=StationHealthDetailResponse,
    summary="Station health detail",
)
def get_station_health(icao: str) -> StationHealthDetailResponse:
    """Serve one station report card across windows and products."""
    detail = get_station_health_store().get_station(icao)
    if detail is None:
        raise HTTPException(status_code=404, detail="Unknown station")
    windows = {
        key: StationWindowModel(
            overall_grade=block["overall_grade"],
            overall_score=float(block["overall_score"]),
            products=_product_models(list(block.get("products") or [])),
        )
        for key, block in (detail.get("windows") or {}).items()
    }
    return StationHealthDetailResponse(
        icao=str(detail["icao"]),
        name=detail.get("name"),
        windows=windows,
        record_count=int(detail.get("record_count") or 0),
    )
