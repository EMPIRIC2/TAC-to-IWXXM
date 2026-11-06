"""BUG-2026-10-07 — SIGMET bulletin without trailing = must still split.

Live-map SIGMETs often keep the WMO heading and omit the report terminator.
Convert switches to AHL bulletin mode and must not return empty_bulletin.
"""

from __future__ import annotations

import pytest

from tac2iwxxm import BulletinSplitError, split_bulletin

_AWC_SIGMET = (
    "WSNT02 KKCI 050930\n"
    "KZWY SIGMET BRAVO 2 VALID 050930/051330 KKCI-\n"
    "NEW YORK OCEANIC FIR EMBD TS OBS AT 0930Z WI N4405 W05758 - "
    "N4038 W05803 - N3127 W07517 - N3225 W07629 - N3507 W07240 - "
    "N3723 W07240 - N3905 W06658 - N4201 W06701 - N4405 W05758. "
    "TOP FL440. MOV ENE 30KT. NC."
)

_AWC_AIRMET = (
    "WAUS01 KKCI 061200\n"
    "BOSZ AIRMET SIERRA 1 VALID 061200/061800 KKCI-\n"
    "AIRMET IFR FOR CIG AND/OR VIS BLO 010."
)


def test_bug_2026_10_07_sigmet_bulletin_without_equals_splits() -> None:
    result = split_bulletin(_AWC_SIGMET, product="SIGMET")
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("KZWY SIGMET")
    assert not result.reports[0].rstrip().endswith("=")


def test_bug_2026_10_07_airmet_bulletin_without_equals_splits() -> None:
    result = split_bulletin(_AWC_AIRMET, product="AIRMET")
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("BOSZ AIRMET")


def test_bug_2026_10_07_heading_only_still_empty_bulletin() -> None:
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin("WSNT02 KKCI 050930\n", product="SIGMET")
    assert exc_info.value.code == "empty_bulletin"
