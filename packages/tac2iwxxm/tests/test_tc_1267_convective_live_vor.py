"""Live NWS convective SIGMET FROM-chains resolve under the US profile.

[Corpus: product §F36] [Corpus: tests] NOAA aviationweather.gov convective SIGMET
retrieved 2026-09-23. Annex 3 output is unchanged when this profile is not selected.
"""

from __future__ import annotations

from iwxxm_validate import validate

from tac2iwxxm import convert

# WSUS32 KKCI 231555 SIGC — CONVECTIVE SIGMET 75C, outlook omitted.
_LIVE_75C = """\
WSUS32 KKCI 231555
SIGC
CONVECTIVE SIGMET 75C
VALID UNTIL 1755Z
TX OK KS CO NM
FROM 30SW GCK-60SSE MMB-40SE CDS-40W TCC-20NNW TBE-30SW GCK
AREA TS MOV FROM 21030KT. TOPS TO FL320.
"""

# Same bulletin family, CONVECTIVE SIGMET 76C.
_LIVE_76C = """\
WSUS32 KKCI 231555
SIGC
CONVECTIVE SIGMET 76C
VALID UNTIL 1755Z
NM
FROM 40SSW FTI-40ENE CME-50SSW CME-50S ABQ-40SSW FTI
AREA TS MOV FROM 17030KT. TOPS TO FL280.
"""

# Eastern area uses "CSTL WTRS" rather than a two-letter state list.
_LIVE_04E = """\
WSUS31 KKCI 231555
SIGE
CONVECTIVE SIGMET 04E
VALID UNTIL 1755Z
FL AND CSTL WTRS
FROM 70E PBI-140SE MIA-60ESE EYW-40NE EYW-70E PBI
AREA EMBD TS MOV FROM 16010KT. TOPS TO FL410.
"""


def test_tc_1267_live_convective_sigmet_converts_and_validates() -> None:
    for tac in (_LIVE_75C, _LIVE_76C, _LIVE_04E):
        result = convert(tac, product="SIGMET", profile="iwxxm_us", iwxxm_version="2025-2")
        assert result.ok, result.issues
        assert "AreaTS" in result.xml
        report = validate(result.xml, iwxxm_version="2025-2", profile="iwxxm_us", levels=["xsd"])
        blocking = [issue for issue in report.issues if issue.severity == "error"]
        assert not blocking, [(issue.code, issue.message) for issue in blocking]


def test_tc_1267_unknown_vor_is_parse_error() -> None:
    tac = """\
MKCC CONVECTIVE SIGMET 1C VALID UNTIL 1755Z
TX
FROM 10N ZZZ-10S ZZZ
AREA TS MOV FROM 21010KT. TOPS TO FL300.
"""
    result = convert(tac, product="SIGMET", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok is False
    assert any(issue.code == "PARSE_ERROR" and "ZZZ" in issue.message for issue in result.issues)
