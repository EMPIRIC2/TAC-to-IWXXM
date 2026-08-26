"""Health check route (EV-037 TD-3b)."""

from __future__ import annotations

from fastapi import APIRouter

from src import api as api_surface
from src.schemas.conversion import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Check API health and conversion availability."""
    try:
        test_metar = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005="
        _ = api_surface.convert_metar_tac_with_metadata(test_metar, validate=False)
        tac2iwxxm_available = True
        status = "healthy"
    except Exception:
        tac2iwxxm_available = False
        status = "degraded"
    return HealthResponse(status=status, version="0.1.0", tac2iwxxm_available=tac2iwxxm_available)
