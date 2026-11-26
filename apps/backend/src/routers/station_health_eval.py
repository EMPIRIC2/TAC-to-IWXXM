"""Station health eval-benchmark route (FR-047 / FR-072)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.schemas.station_health import StationHealthEvalBenchmarkResponse
from src.services.station_health_eval import build_eval_benchmark, normalize_icao_filter

router = APIRouter(prefix="/api/v1", tags=["Station health"])


@router.get(
    "/station-health/eval-benchmark",
    response_model=StationHealthEvalBenchmarkResponse,
    summary="Live eval benchmark for Station health",
    responses={400: {"description": "Invalid icao filter"}},
)
def get_station_health_eval_benchmark(
    icao: str | None = Query(
        default=None,
        description="Optional four-letter ICAO; filters failure_locations by place_key",
    ),
) -> StationHealthEvalBenchmarkResponse:
    """Serve the latest FR-045 live-map eval snapshot for Station health.

    Parameters
    ----------
    icao :
        Optional station filter for failure locations.

    Returns
    -------
    StationHealthEvalBenchmarkResponse
        Snapshot counts, top codes, product failure breakdown, and failures.
    """
    try:
        icao_key = normalize_icao_filter(icao)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StationHealthEvalBenchmarkResponse.model_validate(build_eval_benchmark(icao=icao_key))
