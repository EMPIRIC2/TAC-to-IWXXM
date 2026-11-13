"""Public station health dashboard API (F39)."""

from __future__ import annotations

from typing import cast

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


def _as_str(value: object, default: str = "") -> str:
    """
    Coerce an object to ``str``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    default : object
        Argument ``default``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _as_str("x")
    'x'
    """
    if value is None:
        return default
    return str(value)


def _as_float(value: object, default: float = 0.0) -> float:
    """
    Coerce an object to ``float``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    default : object
        Argument ``default``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _as_float(1.5)
    1.5
    """
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _as_int(value: object, default: int = 0) -> int:
    """
    Coerce an object to ``int``.

    Parameters
    ----------
    value : object
        Argument ``value``.
    default : object
        Argument ``default``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _as_int(3)
    3
    """
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _as_optional_str(value: object) -> str | None:
    """
    Coerce an object to ``str | None``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _as_optional_str(None) is None
    True
    """
    if value is None:
        return None
    return str(value)


def _product_dict(value: object) -> dict[str, object] | None:
    """
    Narrow one product payload to ``dict[str, object]``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _product_dict({"product": "METAR"})["product"]
    'METAR'
    """
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _product_models(
    raw_products: list[dict[str, object]],
) -> list[StationProductGradeModel]:
    """
    Internal helper ``_product_models``.

    Parameters
    ----------
    raw_products : object
        Argument ``raw_products``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _product_models([])
    []
    """
    models: list[StationProductGradeModel] = []
    for item in raw_products:
        models.append(
            StationProductGradeModel(
                product=_as_str(item.get("product")),
                grade=_as_str(item.get("grade")),
                overall_score=_as_float(item.get("overall_score")),
                availability_score=_as_float(item.get("availability_score")),
                actual_count=_as_int(item.get("actual_count")),
                expected_count=_as_int(item.get("expected_count")),
                solidus_rate=_as_float(item.get("solidus_rate")),
                missing_digit_rate=_as_float(item.get("missing_digit_rate")),
                lint_severity_score=_as_float(
                    item.get("lint_severity_score"), 100.0
                ),
                lint_error_count=_as_int(item.get("lint_error_count")),
            )
        )
    return models


def _products_from_raw(raw: object) -> list[dict[str, object]]:
    """
    Collect product dicts from a list-shaped payload.

    Parameters
    ----------
    raw : object
        Argument ``raw``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> _products_from_raw([{"product": "METAR"}])[0]["product"]
    'METAR'
    """
    if not isinstance(raw, list):
        return []
    products: list[dict[str, object]] = []
    for entry in cast(list[object], raw):
        product = _product_dict(entry)
        if product is not None:
            products.append(product)
    return products


@router.get(
    "/station-health/metrics",
    response_model=StationHealthMetricsResponse,
    summary="List station health metric definitions",
)
def list_station_health_metrics() -> StationHealthMetricsResponse:
    """
    Serve the extensible metrics registry for dashboard cards.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_station_health_metrics)
    2
    """
    rows = get_station_health_store().list_metrics()
    metrics: list[StationMetricDefinitionModel] = []
    for row_raw in rows:
        row = cast(dict[str, object], row_raw)
        metrics.append(
            StationMetricDefinitionModel(
                id=_as_str(row.get("id")),
                label=_as_str(row.get("label")),
                description=_as_str(row.get("description")),
                unit=_as_optional_str(row.get("unit")),
                higher_is_better=bool(row.get("higher_is_better", True)),
            )
        )
    return StationHealthMetricsResponse(metrics=metrics)


@router.get(
    "/station-health",
    response_model=StationHealthListResponse,
    summary="List station health grades",
    responses={400: {"description": "Invalid window"}},
)
def list_station_health(
    window: str = Query(default="6h", description="Time window: 6h, 1d, or 30d"),
    product: str | None = Query(default=None, description="Optional product filter"),
    grade: str | None = Query(default=None, description="Optional letter grade filter"),
    limit: int = Query(default=100, ge=1, le=500, description="Max stations to return"),
) -> StationHealthListResponse:
    """
    Serve station report cards for one availability window.

    Parameters
    ----------
    window : object
        Argument ``window``.
    product : object
        Argument ``product``.
    grade : object
        Argument ``grade``.
    limit : object
        Argument ``limit``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (list_station_health)
    2
    """
    window_key = window.strip().lower()
    if window_key not in WINDOW_SECONDS:
        raise HTTPException(status_code=400, detail="Window must be 6h, 1d, or 30d")
    payload = cast(
        dict[str, object],
        get_station_health_store().list_stations(
            window_key=window_key,
            product=product,
            grade=grade,
            limit=limit,
        ),
    )
    stations_raw = payload.get("stations")
    stations: list[StationListItemModel] = []
    if isinstance(stations_raw, list):
        for item_raw in cast(list[object], stations_raw):
            if not isinstance(item_raw, dict):
                continue
            item = cast(dict[str, object], item_raw)
            stations.append(
                StationListItemModel(
                    icao=_as_str(item.get("icao")),
                    name=_as_optional_str(item.get("name")),
                    overall_grade=_as_str(item.get("overall_grade")),
                    overall_score=_as_float(item.get("overall_score")),
                    products=_product_models(
                        _products_from_raw(item.get("products"))
                    ),
                )
            )
    summary_candidate = payload.get("summary")
    summary_raw: dict[str, object] = (
        cast(dict[str, object], summary_candidate)
        if isinstance(summary_candidate, dict)
        else {}
    )
    grade_candidate = summary_raw.get("grade_counts")
    grade_counts: dict[str, int] = {}
    if isinstance(grade_candidate, dict):
        typed_grades = cast(dict[object, object], grade_candidate)
        grade_counts = {
            _as_str(key): _as_int(value) for key, value in typed_grades.items()
        }
    return StationHealthListResponse(
        window=_as_str(payload.get("window")),
        computed_at=_as_str(payload.get("computed_at")),
        stations=stations,
        summary=StationHealthSummaryModel(
            station_count=_as_int(summary_raw.get("station_count")),
            grade_counts=grade_counts,
        ),
    )


@router.get(
    "/station-health/{icao}",
    response_model=StationHealthDetailResponse,
    summary="Station health detail",
    responses={404: {"description": "Unknown station"}},
)
def get_station_health(icao: str) -> StationHealthDetailResponse:
    """
    Serve one station report card across windows and products.

    Parameters
    ----------
    icao : object
        Argument ``icao``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_station_health)
    2
    """
    detail_raw = get_station_health_store().get_station(icao)
    if detail_raw is None:
        raise HTTPException(status_code=404, detail="Unknown station")
    detail = cast(dict[str, object], detail_raw)
    windows_candidate = detail.get("windows")
    windows: dict[str, StationWindowModel] = {}
    if isinstance(windows_candidate, dict):
        for key, block in cast(dict[object, object], windows_candidate).items():
            if not isinstance(block, dict):
                continue
            typed_block = cast(dict[str, object], block)
            windows[_as_str(key)] = StationWindowModel(
                overall_grade=_as_str(typed_block.get("overall_grade")),
                overall_score=_as_float(typed_block.get("overall_score")),
                products=_product_models(
                    _products_from_raw(typed_block.get("products"))
                ),
            )
    return StationHealthDetailResponse(
        icao=_as_str(detail.get("icao")),
        name=_as_optional_str(detail.get("name")),
        windows=windows,
        record_count=_as_int(detail.get("record_count")),
    )
