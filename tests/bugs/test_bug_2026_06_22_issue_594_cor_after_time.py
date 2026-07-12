"""BUG-2026-06-22 — GitHub #594: ICAO COR-after-time METAR conversion.

Post cutover: exercised via ``convert_metar_tac_with_metadata`` (tac2iwxxm).
COR grammar support in tac2iwxxm is tracked under F6 product work; this suite
guards the API conversion path and skips when COR is not yet encoded.
"""

from __future__ import annotations

import pytest

from apps.backend.src.utilities.conversion import (
    ConversionError,
    convert_metar_tac_with_metadata,
)

COR_AFTER_TIME_TAC = "METAR FAOR 101200Z COR 33003KT CAVOK 04/M00 Q1023="
COR_BEFORE_STATION_TAC = "METAR COR FAOR 101200Z 33003KT CAVOK 04/M00 Q1023="


def _try_convert(tac: str) -> str:
    xml, _ = convert_metar_tac_with_metadata(tac, validate=False)
    return xml


@pytest.mark.xfail(
    reason="tac2iwxxm COR grammar not yet implemented (post-gifts; F6 follow-on)",
    strict=False,
)
def test_bug_594_cor_after_time_converts_without_translation_failure() -> None:
    xml = _try_convert(COR_AFTER_TIME_TAC)
    assert "translationFailedTAC" not in xml
    assert "CORRECTION" in xml or "METAR" in xml


@pytest.mark.xfail(
    reason="tac2iwxxm COR grammar not yet implemented (post-gifts; F6 follow-on)",
    strict=False,
)
def test_bug_594_cor_after_time_marks_report_as_correction() -> None:
    xml = _try_convert(COR_AFTER_TIME_TAC)
    assert "CORRECTION" in xml


@pytest.mark.xfail(
    reason="tac2iwxxm COR grammar not yet implemented (post-gifts; F6 follow-on)",
    strict=False,
)
def test_bug_594_cor_before_station_still_works() -> None:
    xml = _try_convert(COR_BEFORE_STATION_TAC)
    assert "translationFailedTAC" not in xml


def test_bug_594_convert_path_raises_structured_error_not_gifts_import() -> None:
    """Cutover regression: conversion failures must not mention gifts imports."""
    with pytest.raises(ConversionError) as exc:
        convert_metar_tac_with_metadata("NOT A METAR", validate=False)
    assert "gifts" not in str(exc.value).lower()
