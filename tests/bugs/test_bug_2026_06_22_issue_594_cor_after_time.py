"""BUG-2026-06-22 — GitHub #594: ICAO COR-after-time METAR fails conversion.

Reporter: correction bulletins produce translationFailedTAC. Root cause: GIFTs
metarDecoder grammar accepts COR only before station ID, not after ddHHmmZ.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from apps.backend.src.utilities.gifts_adapter import convert_tac_to_iwxxm

# ICAO-style COR after issuance time (FAOR sample from context repro)
COR_AFTER_TIME_TAC = "METAR FAOR 101200Z COR 33003KT CAVOK 04/M00 Q1023="

# COR before station — already supported; regression guard
COR_BEFORE_STATION_TAC = "METAR COR FAOR 101200Z 33003KT CAVOK 04/M00 Q1023="


def _xml_has_translation_failure(root: ET.Element) -> bool:
    xml = ET.tostring(root, encoding="unicode")
    return "translationFailedTAC" in xml


def _xml_has_correction_status(root: ET.Element) -> bool:
    xml = ET.tostring(root, encoding="unicode")
    return "CORRECTION" in xml


def test_bug_594_cor_after_time_converts_without_translation_failure() -> None:
    """ICAO METAR STID ddHHmmZ COR ... must not emit translationFailedTAC."""
    root = convert_tac_to_iwxxm(COR_AFTER_TIME_TAC)
    assert not _xml_has_translation_failure(root), (
        "COR-after-time METAR should convert; got translationFailedTAC (GitHub #594)"
    )


def test_bug_594_cor_after_time_marks_report_as_correction() -> None:
    """COR-after-time must set reportStatus CORRECTION in IWXXM output."""
    root = convert_tac_to_iwxxm(COR_AFTER_TIME_TAC)
    assert _xml_has_correction_status(root), (
        "Expected reportStatus CORRECTION for COR-after-time METAR (GitHub #594)"
    )


def test_bug_594_cor_before_station_still_works() -> None:
    """Regression: METAR COR STID ddHHmmZ pattern must remain supported."""
    root = convert_tac_to_iwxxm(COR_BEFORE_STATION_TAC)
    assert not _xml_has_translation_failure(root)
    assert _xml_has_correction_status(root)
