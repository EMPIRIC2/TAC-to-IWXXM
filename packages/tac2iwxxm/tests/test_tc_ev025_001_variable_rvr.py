"""TC-EV025-001 / #810 — Variable RVR + meanRVR withheld (UJ-040).

T1.1: red assertions for ``iwxxm-us:AerodromeVariableRVR`` and withheld meanRVR.
"""

from __future__ import annotations

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# US body group: Rwy / min V max FT (FMH-1 / iwxxm-us AerodromeVariableRVR samples).
_TAC_VAR_RVR = "METAR KJFK 231751Z 18008KT 1/2SM R04L/1100V2300FT FG OVC002 15/14 A2992 RMK AO2="


def test_tc_ev025_001_variable_rvr_emits_aerodrome_variable_rvr() -> None:
    """Convert iwxxm_us must emit AerodromeVariableRVR with min/max (PDF sample shape)."""
    result = convert(
        _TAC_VAR_RVR,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"parse/convert failed: {result.issues!r}"
    assert result.xml
    xml = result.xml
    assert "iwxxm-us:AerodromeVariableRVR" in xml
    assert "iwxxm-us:minimumRVR" in xml
    assert "iwxxm-us:maximumRVR" in xml
    # PDF: mean RVR withheld → nilReason withheld + xsi:nil
    assert 'nilReason="http://codes.wmo.int/common/nil/withheld"' in xml or 'nilReason="withheld"' in xml
    assert "meanRVR" in xml
    assert 'xsi:nil="true"' in xml
