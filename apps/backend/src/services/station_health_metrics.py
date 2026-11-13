"""Pure solidus counters and station health grading rules (F39)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Final

WINDOW_SECONDS: Final[dict[str, int]] = {
    "6h": 6 * 3600,
    "1d": 24 * 3600,
    "30d": 30 * 24 * 3600,
}

EXPECTED_PER_HOUR: Final[dict[str, float]] = {
    "metar": 1.0,
    "taf": 1.0 / 6.0,
}

_MISSING_DIGIT_RE = re.compile(r"/{2,}")
_GRADE_THRESHOLDS: Final[tuple[tuple[float, str], ...]] = (
    (90.0, "A"),
    (80.0, "B"),
    (70.0, "C"),
    (60.0, "D"),
)


@dataclass(frozen=True, slots=True)
class TacQualitySignals:
    """
    Solidus and missing-digit counters for one TAC body.

    Attributes
    ----------
    solidus_count : object
        Field ``solidus_count``.
    missing_digit_count : object
        Field ``missing_digit_count``.
    character_count : object
        Field ``character_count``.
    """

    solidus_count: int
    missing_digit_count: int
    character_count: int


@dataclass(frozen=True, slots=True)
class ProductWindowGrade:
    """
    Graded availability and quality for one station product window.

    Attributes
    ----------
    product : object
        Field ``product``.
    window_key : object
        Field ``window_key``.
    actual_count : object
        Field ``actual_count``.
    expected_count : object
        Field ``expected_count``.
    availability_score : object
        Field ``availability_score``.
    solidus_rate : object
        Field ``solidus_rate``.
    missing_digit_rate : object
        Field ``missing_digit_rate``.
    lint_severity_score : object
        Field ``lint_severity_score``.
    overall_score : object
        Field ``overall_score``.
    overall_grade : object
        Field ``overall_grade``.
    """

    product: str
    window_key: str
    actual_count: int
    expected_count: int
    availability_score: float
    solidus_rate: float
    missing_digit_rate: float
    lint_severity_score: float
    overall_score: float
    overall_grade: str


def count_solidus_signals(tac_text: str) -> TacQualitySignals:
    """
    Count solidus characters and missing-digit runs in TAC text.

    Parameters
    ----------
    tac_text : object
        Argument ``tac_text``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (count_solidus_signals)
    2
    """
    text = tac_text or ""
    solidus_count = text.count("/")
    missing_digit_count = sum(1 for _ in _MISSING_DIGIT_RE.finditer(text))
    return TacQualitySignals(
        solidus_count=solidus_count,
        missing_digit_count=missing_digit_count,
        character_count=len(text),
    )


def expected_count_for_window(product: str, window_key: str) -> int:
    """
    Return expected report count for a product and window.

    Parameters
    ----------
    product : object
        Argument ``product``.
    window_key : object
        Argument ``window_key``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (expected_count_for_window)
    2
    """
    seconds = WINDOW_SECONDS.get(window_key)
    if seconds is None:
        return 0
    rate = EXPECTED_PER_HOUR.get(product.strip().lower())
    if rate is None or rate <= 0:
        return 0
    hours = seconds / 3600.0
    return max(0, round(rate * hours))


def availability_score(actual_count: int, expected_count: int, *, irregular: bool) -> float:
    """
    Score availability from actual versus expected counts.

    Parameters
    ----------
    actual_count : object
        Argument ``actual_count``.
    expected_count : object
        Argument ``expected_count``.
    irregular : object
        Argument ``irregular``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (availability_score)
    2
    """
    if irregular:
        if actual_count <= 0:
            return 0.0
        if actual_count == 1:
            return 70.0
        if actual_count == 2:
            return 85.0
        return 100.0
    if expected_count <= 0:
        return 0.0 if actual_count <= 0 else 100.0
    return min(100.0, 100.0 * (actual_count / expected_count))


def solidus_quality_score(solidus_rate: float) -> float:
    """
    Map solidus rate to a quality score (higher is better).

    Parameters
    ----------
    solidus_rate : object
        Argument ``solidus_rate``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (solidus_quality_score)
    2
    """
    penalty = min(100.0, max(0.0, solidus_rate) * 500.0)
    return max(0.0, 100.0 - penalty)


def missing_digit_quality_score(missing_digit_rate: float) -> float:
    """
    Map missing-digit rate to a quality score (higher is better).

    Parameters
    ----------
    missing_digit_rate : object
        Argument ``missing_digit_rate``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (missing_digit_quality_score)
    2
    """
    penalty = min(100.0, max(0.0, missing_digit_rate) * 25.0)
    return max(0.0, 100.0 - penalty)


def lint_severity_score(error_count: int, warning_count: int, actual_count: int) -> float:
    """
    Score lint severity from stored issue counts.

    Parameters
    ----------
    error_count : object
        Argument ``error_count``.
    warning_count : object
        Argument ``warning_count``.
    actual_count : object
        Argument ``actual_count``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lint_severity_score)
    2
    """
    if actual_count <= 0:
        return 100.0
    weighted = (error_count * 3.0 + warning_count) / actual_count
    penalty = min(100.0, weighted * 10.0)
    return max(0.0, 100.0 - penalty)


def letter_grade(score: float) -> str:
    """
    Map an overall score to a letter grade.

    Parameters
    ----------
    score : object
        Argument ``score``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (letter_grade)
    2
    """
    for threshold, grade in _GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def overall_score(
    availability: float,
    solidus_quality: float,
    missing_digit_quality: float,
    lint_quality: float,
) -> float:
    """
    Blend availability and quality into one overall score.

    Parameters
    ----------
    availability : object
        Argument ``availability``.
    solidus_quality : object
        Argument ``solidus_quality``.
    missing_digit_quality : object
        Argument ``missing_digit_quality``.
    lint_quality : object
        Argument ``lint_quality``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (overall_score)
    2
    """
    return 0.50 * availability + 0.25 * solidus_quality + 0.15 * missing_digit_quality + 0.10 * lint_quality


def grade_product_window(
    *,
    product: str,
    window_key: str,
    actual_count: int,
    solidus_count: int,
    character_count: int,
    missing_digit_count: int,
    lint_error_count: int,
    lint_warning_count: int,
) -> ProductWindowGrade:
    """
    Compute one product-window grade from aggregate counters.

    Parameters
    ----------
    product : object
        Argument ``product``.
    window_key : object
        Argument ``window_key``.
    actual_count : object
        Argument ``actual_count``.
    solidus_count : object
        Argument ``solidus_count``.
    character_count : object
        Argument ``character_count``.
    missing_digit_count : object
        Argument ``missing_digit_count``.
    lint_error_count : object
        Argument ``lint_error_count``.
    lint_warning_count : object
        Argument ``lint_warning_count``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (grade_product_window)
    2
    """
    product_l = product.strip().lower() or "unknown"
    expected = expected_count_for_window(product_l, window_key)
    irregular = expected == 0
    avail = availability_score(actual_count, expected, irregular=irregular)
    solidus_rate = (solidus_count / character_count) if character_count > 0 else 0.0
    missing_rate = (missing_digit_count / actual_count) if actual_count > 0 else 0.0
    solidus_q = solidus_quality_score(solidus_rate)
    missing_q = missing_digit_quality_score(missing_rate)
    lint_q = lint_severity_score(lint_error_count, lint_warning_count, actual_count)
    score = overall_score(avail, solidus_q, missing_q, lint_q)
    return ProductWindowGrade(
        product=product_l,
        window_key=window_key,
        actual_count=actual_count,
        expected_count=expected,
        availability_score=round(avail, 2),
        solidus_rate=round(solidus_rate, 5),
        missing_digit_rate=round(missing_rate, 5),
        lint_severity_score=round(lint_q, 2),
        overall_score=round(score, 2),
        overall_grade=letter_grade(score),
    )


def window_timedelta(window_key: str) -> timedelta:
    """
    Return the timedelta for a window key.

    Parameters
    ----------
    window_key : object
        Argument ``window_key``.

    Returns
    -------
    object
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (window_timedelta)
    2
    """
    seconds = WINDOW_SECONDS.get(window_key)
    if seconds is None:
        msg = f"unknown window key: {window_key}"
        raise ValueError(msg)
    return timedelta(seconds=seconds)


__all__ = [
    "EXPECTED_PER_HOUR",
    "WINDOW_SECONDS",
    "ProductWindowGrade",
    "TacQualitySignals",
    "availability_score",
    "count_solidus_signals",
    "expected_count_for_window",
    "grade_product_window",
    "letter_grade",
    "lint_severity_score",
    "missing_digit_quality_score",
    "overall_score",
    "solidus_quality_score",
    "window_timedelta",
]
