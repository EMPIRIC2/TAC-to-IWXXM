"""TC-EV025-006 / TC-EV025-007 — US REMARKS diagnostics + humanReadableText (S032 M6).

Deepens UJ-010 / UJ-026 for Lane A structured remarks mixed with garbage / free text.
"""

from __future__ import annotations

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# Valid Variable RVR + malformed AO/SLP tokens in the same REMARKS group.
_TAC_MIXED_MALFORMED = "METAR KJFK 231751Z 18008KT 1/2SM R04L/1100V2300FT FG OVC002 15/14 A2992 RMK AOX SLPZZZ RAB20="

# Structured WindShift + free-text remainder that must survive in humanReadableText.
_TAC_MIXED_FREE = "METAR KJFK 231751Z 18008KT 10SM FEW040 15/07 A3005 RMK AO2 WSHFT 30 FROPA EXTRA FREE TEXT="


def test_tc_ev025_006_malformed_us_remarks_with_structured() -> None:
    """Malformed tokens alongside structured REMARKS → diagnostics (no silent drop)."""
    result = convert(
        _TAC_MIXED_MALFORMED,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.issues, f"expected diagnostics, got empty issues; ok={result.ok}"
    blob = " ".join(f"{i.code} {i.message}" for i in result.issues).lower()
    assert "malformed" in blob or "remark" in blob or "aox" in blob or "slp" in blob
    # Structured Variable RVR path must still encode when present.
    if result.ok and result.xml:
        assert "iwxxm-us:AerodromeVariableRVR" in result.xml


def test_tc_ev025_007_unparsed_remarks_in_human_readable_text() -> None:
    """Structured encode + remainder retained in iwxxm-us:humanReadableText."""
    result = convert(
        _TAC_MIXED_FREE,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:AerodromeWindShift" in xml or "WSHFT" in xml
    assert "iwxxm-us:humanReadableText" in xml
    # Free-text remainder (not fully structured) must not be silently dropped.
    assert "EXTRA" in xml or "FREE" in xml or "FROPA" in xml
