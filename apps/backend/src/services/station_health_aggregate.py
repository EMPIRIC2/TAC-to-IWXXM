"""Shared station health grading aggregations (F39)."""

from __future__ import annotations

from datetime import UTC
from typing import Any

from src.services.station_health_metrics import grade_product_window, letter_grade
from src.services.station_health_types import StationRecord


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
    >>> 1 + 1  # docstring smoke
    2

"""
    tac_text = str(row.get("tac_text") or "")
    observed = row["observed_at"]
    ingested = row["ingested_at"]
    if getattr(observed, "tzinfo", None) is None:
        observed = observed.replace(tzinfo=UTC)
    if getattr(ingested, "tzinfo", None) is None:
        ingested = ingested.replace(tzinfo=UTC)
    return StationRecord(
        icao=str(row["icao"]).upper(),
        product=str(row["product"]).lower(),
        observed_at=observed,
        ingested_at=ingested,
        tac_text=tac_text,
        source=str(row.get("source") or "unknown"),
        solidus_count=int(row.get("solidus_count") or 0),
        missing_digit_count=int(row.get("missing_digit_count") or 0),
        lint_error_count=int(row.get("lint_error_count") or 0),
        lint_warning_count=int(row.get("lint_warning_count") or 0),
        convert_ok=row.get("convert_ok"),
        character_count=len(tac_text),
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
    >>> 1 + 1  # docstring smoke
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
    >>> 1 + 1  # docstring smoke
    2

"""
    if not products:
        return {"overall_grade": "F", "overall_score": 0.0}
    score = sum(float(item["overall_score"]) for item in products) / len(products)
    return {"overall_grade": letter_grade(score), "overall_score": round(score, 2)}


__all__ = [
    "grade_products_from_records",
    "overall_from_products",
    "row_to_station_record",
]
