"""TC-EV025-010 - Combined WMO + iwxxm-us catalog validate smoke (S032 M6 / F2/F13).

Lane A structured REMARKS XML must validate under ``profile=iwxxm_us`` (combined
catalogs). Schematron soft skips are allowed (S02.L1); blocking XSD errors are not.
"""

from __future__ import annotations

from tac2iwxxm import convert

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"

# Representative Lane A encodes (#810 Variable RVR + #811 Lightning + WindShift).
_CASES = (
    (
        "var_rvr",
        "METAR KJFK 231751Z 18008KT 1/2SM R04L/1100V2300FT FG OVC002 15/14 A2992 RMK AO2=",
    ),
    (
        "lightning",
        "METAR KJFK 231751Z 18008KT 10SM TS FEW040 15/07 A3005 RMK AO2 LTG DSNT NE=",
    ),
    (
        "wind_shift",
        "METAR KJFK 231751Z 18008KT 10SM FEW040 15/07 A3005 RMK AO2 WSHFT 30 FROPA=",
    ),
)


def test_tc_ev025_010_combined_catalog_validate_smoke() -> None:
    from iwxxm_validate import validate

    for case_id, tac in _CASES:
        result = convert(
            tac,
            product="METAR",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert result.ok is True, f"{case_id}: convert failed: {result.issues!r}"
        assert result.xml
        assert "xmlns:iwxxm-us=" in result.xml or "iwxxm-us:" in result.xml
        report = validate(
            result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"{case_id}: blocking validate issues: {[(i.code, i.message) for i in blocking]}"
