"""TC-F6-037 — test and exercise bulletins are non-operational.

[Corpus: product §F6] [Corpus: tests §TC-F6-037]
"""

from __future__ import annotations

import re

from tac2iwxxm import convert

_SWX = """SWX ADVISORY
DTG: 20201108/0100Z
SWXC: DONLON
SWX EFFECT: HF COM
ADVISORY NR: 2020/1
OBS SWX: 08/0100Z SEV MNH EQN EQS MSH DAYSIDE MOD NIGHTSIDE
FCST SWX +6 HR: 08/0700Z NO SWX EXP
FCST SWX +12 HR: 08/1300Z NO SWX EXP
FCST SWX +18 HR: 08/1900Z NO SWX EXP
FCST SWX +24 HR: 09/0100Z NO SWX EXP
NXT ADVISORY: WILL BE ISSUED BY 20201108/0700Z
"""
_REMARK = "TEST TEST TEST. THIS IS A TEST SPACE WEATHER ADVISORY. PLEASE DISREGARD."
_SIGMET = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN EXERCISE=\n"
)
_METAR = "METAR KJFK 121151Z 18012KT 9999 FEW020 15/07 Q1013="
_FAILED = "STATUS: TEST\nMETAR KJFK 121151Z INVALID 18012KT 9999 FEW020 15/07 Q1013=\n"


def _attr(xml: str, name: str) -> str | None:
    match = re.search(rf'{name}="([^"]*)"', xml)
    return match.group(1) if match else None


def test_tc_f6_037_status_test_space_weather_is_non_operational() -> None:
    """A STATUS: TEST advisory uses reason TEST and the remark as the note."""
    tac = _SWX.replace(
        "NXT ADVISORY:",
        f"STATUS: TEST\nRMK: {_REMARK}\nNXT ADVISORY:",
    )
    result = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsage") == "NON-OPERATIONAL"
    assert _attr(xml, "permissibleUsageReason") == "TEST"
    assert _attr(xml, "permissibleUsageSupplementary") == _REMARK


def test_tc_f6_037_remark_test_without_status_is_non_operational() -> None:
    """A remark that says this is a test is enough when STATUS is absent."""
    tac = _SWX.replace(
        "NXT ADVISORY:",
        "RMK: THIS IS A TEST\nMESSAGE.\n\nNXT ADVISORY:",
    )
    result = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsage") == "NON-OPERATIONAL"
    assert _attr(xml, "permissibleUsageReason") == "TEST"
    assert _attr(xml, "permissibleUsageSupplementary") == "THIS IS A TEST MESSAGE."


def test_tc_f6_037_status_test_without_a_remark_uses_the_short_note() -> None:
    """STATUS: TEST with no RMK field uses the short fallback note."""
    result = convert(
        _SWX.replace("NXT ADVISORY:", "STATUS: TEST\nNXT ADVISORY:"),
        product="SWXA",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsageReason") == "TEST"
    assert _attr(xml, "permissibleUsageSupplementary") == "Test bulletin"


def test_tc_f6_037_ordinary_metar_stays_operational() -> None:
    """An ordinary report omits the reason and the supplementary note."""
    result = convert(_METAR, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsage") == "OPERATIONAL"
    assert "permissibleUsageReason" not in xml
    assert "permissibleUsageSupplementary" not in xml


def test_tc_f6_037_exercise_sigmet_uses_exercise_reason() -> None:
    """The word EXERCISE sets reason EXERCISE and the short fallback note."""
    result = convert(_SIGMET, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsage") == "NON-OPERATIONAL"
    assert _attr(xml, "permissibleUsageReason") == "EXERCISE"
    assert _attr(xml, "permissibleUsageSupplementary") == "Exercise bulletin"


def test_tc_f6_037_exercise_wins_when_a_test_marker_is_also_present() -> None:
    """An exercise marker wins, and the remark is the supplementary text."""
    tac = _SWX.replace(
        "NXT ADVISORY:",
        "STATUS: TEST\nRMK: THIS IS AN EXERCISE.\nNXT ADVISORY:",
    )
    result = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsageReason") == "EXERCISE"
    assert _attr(xml, "permissibleUsageSupplementary") == "THIS IS AN EXERCISE."


def test_tc_f6_037_va_test_source_text_stays_operational() -> None:
    """Source text VA TEST is not an explicit test marker."""
    tac = _SWX.replace("NXT ADVISORY:", "RMK: VA TEST\nNXT ADVISORY:")
    result = convert(tac, product="SWXA", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert _attr(xml, "permissibleUsage") == "OPERATIONAL"
    assert "permissibleUsageReason" not in xml


def test_tc_f6_037_failed_translation_stays_operational() -> None:
    """A failed translation stays operational even when the TAC says TEST."""
    result = convert(_FAILED, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok is True, result.issues
    xml = result.xml or ""
    assert "translationFailedTAC" in xml
    assert _attr(xml, "permissibleUsage") == "OPERATIONAL"
    assert "permissibleUsageReason" not in xml
