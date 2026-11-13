"""TC-SH-003 / TC-SH-004 — solidus counters and grade rules."""

from __future__ import annotations

import pytest
from src.services.station_health_metrics import (
    availability_score,
    count_solidus_signals,
    expected_count_for_window,
    grade_product_window,
    letter_grade,
)


@pytest.mark.parametrize(
    ("tac", "solidus", "missing"),
    [
        ("METAR KJFK 010000Z 18008KT 10SM FEW040 15/07 A3005=", 1, 0),
        ("METAR KJFK 010000Z ////KT 10SM FEW040 15/07 A3005=", 5, 1),
        ("METAR KJFK 010000Z ////// 10SM FEW040 ///// A3005=", 11, 2),
        ("", 0, 0),
    ],
)
def test_tc_sh_003_solidus_and_missing_digit_counters(tac: str, solidus: int, missing: int) -> None:
    signals = count_solidus_signals(tac)
    assert signals.solidus_count == solidus
    assert signals.missing_digit_count == missing


@pytest.mark.parametrize(
    ("score", "grade"),
    [(90, "A"), (89.9, "B"), (80, "B"), (70, "C"), (60, "D"), (59.9, "F")],
)
def test_tc_sh_004_letter_grade_thresholds(score: float, grade: str) -> None:
    assert letter_grade(score) == grade


def test_tc_sh_004_availability_and_expected_counts() -> None:
    assert expected_count_for_window("metar", "6h") == 6
    assert expected_count_for_window("taf", "1d") == 4
    assert expected_count_for_window("speci", "6h") == 0
    assert availability_score(6, 6, irregular=False) == 100.0
    assert availability_score(3, 6, irregular=False) == 50.0
    assert availability_score(1, 0, irregular=True) == 70.0


def test_tc_sh_004_perfect_metar_window_is_grade_a() -> None:
    grade = grade_product_window(
        product="metar",
        window_key="6h",
        actual_count=6,
        solidus_count=0,
        character_count=600,
        missing_digit_count=0,
        lint_error_count=0,
        lint_warning_count=0,
    )
    assert grade.overall_grade == "A"
    assert grade.expected_count == 6
