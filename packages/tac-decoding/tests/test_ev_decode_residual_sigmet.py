"""Decode regressions for SIGMET non-RMK residual conventions (F9).

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.decode import _explain_sigmet_airmet, decode_tac


def _codes(tac: str) -> dict[str, str]:
    return {s.code: s.explanation for s in decode_tac(tac, product="SIGMET").segments}


def _residual(tac: str) -> list[str]:
    return [r.text for r in decode_tac(tac, product="SIGMET").residuals]


def test_line_width_nm_wide() -> None:
    tac = (
        "WSUS32 KKCI 031255\nMKCC WST 031255\nCONVECTIVE SIGMET 55C\n"
        "VALID UNTIL 1455Z\nKS\nFROM 50E SLN-50ENE ICT\n"
        "LINE TS 15 NM WIDE MOV FROM 24020KT. TOPS TO FL400."
    )
    codes = _codes(tac)
    assert codes["LINE"] == "Line of coordinates"
    assert "width 15" in codes["15"].lower()
    assert codes["NM"] == "Nautical miles"
    assert codes["WIDE"] == "Wide"
    assert "15" not in _residual(tac)


def test_hail_inch_and_spaced_fl_and_wind_range() -> None:
    hail = (
        "WSUS32 KKCI 030355\nMKCC WST 030355\nCONVECTIVE SIGMET 17C\n"
        "VALID UNTIL 0555Z\nMO\nFROM 40ENE PWE-30SW IRK\n"
        "AREA SEV TS MOV FROM 21040KT. TOPS ABV FL450.\n"
        "HAIL TO 1 IN...WIND GUSTS TO 50KT POSS."
    )
    assert "inch hail" in _codes(hail)["1"].lower()
    fl = (
        "WSGR31 LGAT 030350\nLGGG SIGMET T04 VALID 030350/030600 LGAT-\n"
        "LGGG ATHINAI FIR/UIR EMBD TS OBS WI N4106 E02212 TOP FL 380 STNR NC="
    )
    codes = _codes(fl)
    assert codes["FL"] == "Flight level"
    assert "380" in codes["380"]
    assert "380" not in _residual(fl)
    wind = (
        "WSCA31 MHTG 031237\nMHTG SIGMET H4 VALID 031237/031637 MHTG-\n"
        "MHCC CENTRAL AMERICAN FIR EMBD TS OBS AT 1230Z "
        "WI N1143 W08854 TOP FL540 MOV NW 05-10KT INTSF="
    )
    assert "05-10KT" in _codes(wind)
    assert "05-10KT" not in _residual(wind)


def test_trailing_ellipsis_and_edges() -> None:
    tac = (
        "WSUS05 KKCI 030721\nSLCV WS 030721\nSIGMET VICTOR 1 VALID UNTIL 031121\n"
        "ID MT\nFROM 50ESE DLN TO 20SW BOY\nOCNL SEV TURB BTN FL330 AND FL400. ...."
    )
    assert any("Truncated" in (_codes(tac).get(k) or "") for k in _codes(tac))
    seen: dict[str, int] = {"fl_expect": 1}
    assert "Flight level 500" in (_explain_sigmet_airmet("500", product="SIGMET", seen=seen) or "")
    seen = {"line": 1}
    assert "width" in (_explain_sigmet_airmet("60", product="SIGMET", seen=seen) or "").lower()
    assert "Truncated" in (_explain_sigmet_airmet("....", product="SIGMET", seen={}) or "")
    seen = {"hail_size": 1}
    assert _explain_sigmet_airmet("IN", product="SIGMET", seen=seen) == "Inches"
    assert _explain_sigmet_airmet("TO", product="SIGMET", seen=seen) == "To"
