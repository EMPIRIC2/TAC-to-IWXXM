"""Facade for ``tac_quality.py`` (line-cap split)."""

from src.routers.tac_quality_part_1 import (
    _advisory_explanation,
    _DecodedResidual,
    _DecodedRow,
    _enrich_advisory_decode,
    _ensure_airport_location_resolver,
    _location_resolver_ready,
    decode_tac_endpoint,
    lint_issue_catalog,
    router,
)
from src.routers.tac_quality_part_2 import (
    lint_tac,
    station_point,
)

__all__ = [
    "_DecodedResidual",
    "_DecodedRow",
    "_advisory_explanation",
    "_enrich_advisory_decode",
    "_ensure_airport_location_resolver",
    "_location_resolver_ready",
    "decode_tac_endpoint",
    "lint_issue_catalog",
    "lint_tac",
    "router",
    "station_point",
]
