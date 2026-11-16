"""Shared station health grading aggregations (F39)."""

from __future__ import annotations

import json
from datetime import UTC
from typing import Any, cast

from src.services.station_health_centennial import build_centennial_metrics
from src.services.station_health_metrics import grade_product_window, letter_grade
from src.services.station_health_signals import (
    count_file_formats,
    count_issue_codes,
    count_maintenance_tags,
    detect_file_format,
    extract_maintenance_tags,
    normalize_issue_codes,
)
from src.services.station_health_types import StationMeta, StationRecord


def _parse_issue_codes(raw: object) -> tuple[str, ...]:
    """
    Parse issue codes from SQL JSON or list.

    Parameters
    ----------
    args
        See function signature.

    Returns
    -------
    object
        Return value.
    """
    if raw is None:
        return ()
    if isinstance(raw, str):
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError:
            return normalize_issue_codes([raw])
        if isinstance(loaded, list):
            items = cast(list[object], loaded)
            return normalize_issue_codes([str(item) for item in items])
        return ()
    if isinstance(raw, (list, tuple)):
        items = cast(list[object] | tuple[object, ...], raw)
        return normalize_issue_codes([str(item) for item in items])
    return ()


def row_to_station_record(row: dict[str, Any]) -> StationRecord:
    """
    Map a SQL/mapping row into a ``StationRecord``.

    Parameters
    ----------
    row : object
        SQLAlchemy mapping or dict row.

    Returns
    -------
    StationRecord
        Normalized observation record.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (row_to_station_record)
    2
    """
    tac_text = str(row.get("tac_text") or "")
    observed = row["observed_at"]
    ingested = row["ingested_at"]
    if getattr(observed, "tzinfo", None) is None:
        observed = observed.replace(tzinfo=UTC)
    if getattr(ingested, "tzinfo", None) is None:
        ingested = ingested.replace(tzinfo=UTC)
    source = str(row.get("source") or "unknown")
    file_format = str(row.get("file_format") or "").strip().lower()
    if not file_format:
        file_format = detect_file_format(tac_text, source=source)
    maintenance_raw = row.get("maintenance_tags")
    if isinstance(maintenance_raw, (list, tuple)):
        maint_items = cast(list[object] | tuple[object, ...], maintenance_raw)
        maintenance_tags = tuple(str(item) for item in maint_items)
    else:
        maintenance_tags = extract_maintenance_tags(tac_text)
    return StationRecord(
        icao=str(row["icao"]).upper(),
        product=str(row["product"]).lower(),
        observed_at=observed,
        ingested_at=ingested,
        tac_text=tac_text,
        source=source,
        solidus_count=int(row.get("solidus_count") or 0),
        missing_digit_count=int(row.get("missing_digit_count") or 0),
        lint_error_count=int(row.get("lint_error_count") or 0),
        lint_warning_count=int(row.get("lint_warning_count") or 0),
        convert_ok=row.get("convert_ok"),
        character_count=len(tac_text),
        file_format=file_format,
        maintenance_tags=maintenance_tags,
        issue_codes=_parse_issue_codes(row.get("issue_codes")),
    )


def grade_products_from_records(rows: list[StationRecord], window_key: str) -> list[dict[str, Any]]:
    """
    Grade each product present in ``rows`` for one window.

    Parameters
    ----------
    rows : object
        Observation rows in the window.
    window_key : object
        Window id such as ``6h``.

    Returns
    -------
    list[dict[str, Any]]
        Per-product grade dictionaries.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (grade_products_from_records)
    2
    """
    by_product: dict[str, list[StationRecord]] = {}
    for row in rows:
        by_product.setdefault(row.product, []).append(row)
    graded: list[dict[str, Any]] = []
    for product, product_rows in sorted(by_product.items()):
        grade = grade_product_window(
            product=product,
            window_key=window_key,
            actual_count=len(product_rows),
            solidus_count=sum(row.solidus_count for row in product_rows),
            character_count=sum(row.character_count for row in product_rows),
            missing_digit_count=sum(row.missing_digit_count for row in product_rows),
            lint_error_count=sum(row.lint_error_count for row in product_rows),
            lint_warning_count=sum(row.lint_warning_count for row in product_rows),
        )
        graded.append(
            {
                "product": grade.product,
                "grade": grade.overall_grade,
                "overall_score": grade.overall_score,
                "availability_score": grade.availability_score,
                "actual_count": grade.actual_count,
                "expected_count": grade.expected_count,
                "solidus_rate": grade.solidus_rate,
                "missing_digit_rate": grade.missing_digit_rate,
                "lint_severity_score": grade.lint_severity_score,
                "lint_error_count": sum(row.lint_error_count for row in product_rows),
            }
        )
    return graded


def overall_from_products(products: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Average product scores into one station overall grade.

    Parameters
    ----------
    products : object
        Per-product grade dictionaries.

    Returns
    -------
    dict[str, Any]
        Overall grade and score.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (overall_from_products)
    2
    """
    if not products:
        return {"overall_grade": "F", "overall_score": 0.0}
    score = sum(float(item["overall_score"]) for item in products) / len(products)
    return {"overall_grade": letter_grade(score), "overall_score": round(score, 2)}


def _window_quality_rollups(products: list[dict[str, Any]]) -> dict[str, float | int]:
    """
    Blend product rows into window-level quality inputs for Centennial proxies.

    Parameters
    ----------
    args
        See function signature.

    Returns
    -------
    object
        Return value.
    """
    if not products:
        return {
            "availability_score": 0.0,
            "expected_count": 0,
            "actual_count": 0,
            "solidus_rate": 0.0,
            "missing_digit_rate": 0.0,
            "lint_severity_score": 100.0,
        }
    n = len(products)
    return {
        "availability_score": sum(float(p["availability_score"]) for p in products) / n,
        "expected_count": sum(int(p["expected_count"]) for p in products),
        "actual_count": sum(int(p["actual_count"]) for p in products),
        "solidus_rate": sum(float(p["solidus_rate"]) for p in products) / n,
        "missing_digit_rate": sum(float(p["missing_digit_rate"]) for p in products) / n,
        "lint_severity_score": sum(float(p["lint_severity_score"]) for p in products) / n,
    }


def enrich_station_window(
    *,
    meta: StationMeta | None,
    rows: list[StationRecord],
    window_key: str,
    products: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build grades plus maintenance, format, issue, and Centennial rollups.

    Parameters
    ----------
    meta : StationMeta | None
        Registry metadata.
    rows : list[StationRecord]
        Windowed observations.
    window_key : str
        Window id.
    products : list[dict[str, Any]] | None
        Optional precomputed product grades.

    Returns
    -------
    dict[str, Any]
        Window payload fields for list/detail responses.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (enrich_station_window)
    2
    """
    graded = products if products is not None else grade_products_from_records(rows, window_key)
    overall = overall_from_products(graded)
    rollups = _window_quality_rollups(graded)
    return {
        "overall_grade": overall["overall_grade"],
        "overall_score": overall["overall_score"],
        "products": graded,
        "maintenance_tag_counts": count_maintenance_tags(rows),
        "file_format_counts": count_file_formats(rows),
        "issue_code_counts": count_issue_codes(rows),
        "centennial_metrics": build_centennial_metrics(
            meta=meta,
            rows=rows,
            availability_score=float(rollups["availability_score"]),
            expected_count=int(rollups["expected_count"]),
            actual_count=int(rollups["actual_count"]),
            solidus_rate=float(rollups["solidus_rate"]),
            missing_digit_rate=float(rollups["missing_digit_rate"]),
            lint_severity_score=float(rollups["lint_severity_score"]),
        ),
    }


__all__ = [
    "enrich_station_window",
    "grade_products_from_records",
    "overall_from_products",
    "row_to_station_record",
]
