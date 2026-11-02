"""Package coverage for SIGMET/AIRMET fail-closed H1-H4 paths.

Mirrors ``tests/bugs/tac/test_bug_2026_11_02_sigmet_*`` so the tac2iwxxm
coverage gate sees the new branches (bug-repro tree is outside this package).

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.heading_paste import reports_for_convert
from tac2iwxxm.slot_builders.sigmet_airmet import parse_airmet, parse_sigmet

from tac2iwxxm import convert


def test_heading_paste_keeps_wc_ahl_for_tc_cnl() -> None:
    tac = "WCUK31 YUDO 251800\nYUCC SIGMET 4 VALID 251800/252200 YUDO-\nYUCC AMSWELL FIR CNL SIGMET 3 251600/252200="
    pasted = reports_for_convert(tac, "SIGMET")
    assert pasted is not None
    report = pasted.reports[0][0]
    assert report.startswith("WCUK31 YUDO 251800\n")
    ir = parse_sigmet(report)
    assert ir.get("iwxxm_root") == "TropicalCycloneSIGMET"


def test_empty_sigmet_and_airmet_fail_closed() -> None:
    empty_sig = convert(
        "YUDD SIGMET 2 VALID 101200/101600 YUSO-=",
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert empty_sig.ok is False
    assert any(i.code == "PARSE_ERROR" for i in empty_sig.issues)

    empty_air = convert(
        "YUDD AIRMET 1 VALID 151520/151800 YUSO-=",
        product="AIRMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert empty_air.ok is False


def test_incomplete_cnl_and_out_of_range_coords_fail() -> None:
    with pytest.raises(ValueError, match="incomplete CNL"):
        parse_sigmet("YUDD SIGMET 3 VALID 101345/101600 YUSO-\nYUDD SHANLON FIR/UIR CNL SIGMET 2=")
    with pytest.raises(ValueError, match="coordinate out of range"):
        parse_sigmet(
            "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
            "YUDD SHANLON FIR/UIR SEV ICE FCST WI N9500 E01000 - N9600 E01200 - "
            "N9500 E01400 - N9500 E01000 FL100/200 STNR NC="
        )


def test_inverted_valid_period_fails_and_quarantine_nils() -> None:
    with pytest.raises(ValueError, match="valid period end must be after begin"):
        parse_sigmet(
            "YUDD SIGMET 2 VALID 101600/101200 YUSO-\n"
            "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
        )
    hard = convert(
        "YUDD SIGMET 2 VALID 101200/101200 YUSO-\n"
        "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=",
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert hard.ok is False

    shell = convert(
        "YUDD SIGMET 1 VALID 101600/101200 YUSO INVALID",
        product="SIGMET",
        profile="annex3",
        iwxxm_version="2025-2",
    )
    assert shell.ok is True
    assert shell.xml is not None
    assert "nilReason" in shell.xml
    assert "<gml:beginPosition>" not in shell.xml


def test_airmet_outlook_without_phenomenon_fails() -> None:
    with pytest.raises(ValueError, match="missing phenomenon"):
        parse_airmet(
            "YUDD AIRMET 1 VALID 151400/152100 YUSO-\n"
            "YUDD SHANLON FIR=\n"
            "OTLK VALID 1800-2000Z...AREA BOUNDED BY BAE-BVT"
        )


def test_airmet_area_without_phenomenon_token() -> None:
    from tac2iwxxm.slot_builders.sigmet_airmet import _airmet_area_ir

    area = _airmet_area_ir("YUDD SHANLON FIR OBS STNR NC")
    assert "phenomenon" not in area
