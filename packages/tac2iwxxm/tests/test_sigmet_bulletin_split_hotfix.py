"""SIGMET bulletin split hotfix — multi-FIR, WST convective, glued AHL.

Package-local suite so pytest-gremlins ``TARGET=tac2iwxxm`` covers the hotfix
paths in ``bulletin.py`` / convective WST parsing.

[Corpus: product §F6] [Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.bulletin import (
    _find_sigmet_reports,
    _is_kept_sigmet_report,
    _span_overlaps_prior,
    _unglue_sigmet_ahl,
)
from tac2iwxxm.slot_builders.sigmet_airmet import _parse_convective_sigmet

from tac2iwxxm import BulletinSplitError, split_bulletin

_OCEANIC = """\
WSNT04 KKCI 260210
KZWY KZMA SIGMET DELTA 10 VALID 260210/260610 KKCI-
NEW YORK OCEANIC FIR MIAMI OCEANIC FIR FRQ TS OBS AT 0210Z WI
N2617 W07254 - N2617 W06818 - N2319 W06726 - N2029 W07026 - N2032
W07256 - N1958 W07328 - N2034 W07356 - N2617 W07254. TOP FL530.
MOV ENE 15KT. INTSF.
"""

_WST_CONVECTIVE = """\
WSUS31 KKCI 261655
MKCE WST 261655

CONVECTIVE SIGMET 8E
VALID UNTIL 1855Z
FL AND CSTL WTRS
FROM 140E PBI-180ESE MIA-150SE MIA-40S EYW-20ESE MIA-140E PBI
AREA TS MOV FROM 06025KT. TOPS TO FL330.
"""

_GLUED = "AREA TS MOV FROM 06025KT. TOPS TO FL330.WSUS32 KKCI 261355\nMKCC WST 261355\n"

_OPERATOR = """\
WSNT04 KKCI 260210
KZWY KZMA SIGMET DELTA 10 VALID 260210/260610 KKCI-
NEW YORK OCEANIC FIR MIAMI OCEANIC FIR FRQ TS OBS AT 0210Z WI
N2617 W07254 - N2617 W06818 - N2319 W06726 - N2029 W07026 - N2032
W07256 - N1958 W07328 - N2034 W07356 - N2617 W07254. TOP FL530.
MOV ENE 15KT. INTSF.

WSUS31 KKCI 261655
MKCE WST 261655

CONVECTIVE SIGMET 8E
VALID UNTIL 1855Z
FL AND CSTL WTRS
FROM 140E PBI-180ESE MIA-150SE MIA-40S EYW-20ESE MIA-140E PBI
AREA TS MOV FROM 06025KT. TOPS TO FL330.WSUS32 KKCI 261355
MKCC WST 261355

CONVECTIVE SIGMET 41C
VALID UNTIL 1555Z
TX NM
FROM 50NNE TCC-30NNW AMA-50WNW ABI-60SE FST-40NNE MRF-50NNE TCC
AREA TS MOV FROM 21030KT. TOPS TO FL320.WSUS32 KKCI 262155
MKCC WST 262155

CONVECTIVE SIGMET 59C
VALID UNTIL 2355Z
TX NM
FROM 60NNE ABI-20ESE SJT-40W MRF-70SE ELP-60NNE ABI
AREA TS MOV FROM 20020KT. TOPS TO FL450.
WSUS32 KKCI 262155
MKCC WST 262155

CONVECTIVE SIGMET 60C
VALID UNTIL 2355Z
NM
FROM 20NW CME-30E CME-40S CME-50WSW CME-20NW CME
INTSF AREA SEV TS MOV FROM 23010KT. TOPS ABV FL450.
HAIL TO 1 IN...WIND GUSTS TO 50KT POSS.
"""

_TRAILER = """\
WSUS32 KKCI 262155
MKCC WST 262155

CONVECTIVE SIGMET 60C
VALID UNTIL 2355Z
NM
FROM 20NW CME-30E CME-40S CME-50WSW CME-20NW CME
INTSF AREA SEV TS MOV FROM 23010KT. TOPS ABV FL450.
HAIL TO 1 IN...WIND GUSTS TO 50KT POSS.
"""


def test_span_overlaps_prior_exclusive_end_keeps_abutting() -> None:
    """Abutting reports (start == last_end) are kept; interior starts are skipped."""
    assert _span_overlaps_prior(0, -1) is False
    assert _span_overlaps_prior(5, 10) is True
    assert _span_overlaps_prior(9, 10) is True
    assert _span_overlaps_prior(10, 10) is False
    assert _span_overlaps_prior(11, 10) is False


def test_is_kept_sigmet_report_fir_and_convective() -> None:
    assert _is_kept_sigmet_report("KZWY KZMA SIGMET DELTA 10 VALID 260210/260610 KKCI-") is True
    assert _is_kept_sigmet_report("YUDD SIGMET 2 VALID 101200/101600 YUSO-") is True
    assert _is_kept_sigmet_report("MKCE WST 261655\n\nCONVECTIVE SIGMET 8E\nVALID UNTIL 1855Z\nFL") is True
    assert _is_kept_sigmet_report("CONVECTIVE SIGMET 60C\nVALID UNTIL 2355Z\nNM") is True
    assert _is_kept_sigmet_report("VA ADVISORY\nDTG: 20261026/1200Z") is False
    assert _is_kept_sigmet_report("TC ADVISORY\nDTG: 20261026/1200Z") is False
    assert _is_kept_sigmet_report("") is False


def test_unglue_sigmet_ahl_inserts_newline_before_wsus() -> None:
    out = _unglue_sigmet_ahl(_GLUED)
    assert "FL330.\nWSUS32 KKCI 261355" in out
    assert "FL330.WSUS32" not in out
    assert _unglue_sigmet_ahl(_GLUED) != _GLUED
    assert isinstance(_unglue_sigmet_ahl(_GLUED), str)
    assert len(_unglue_sigmet_ahl(_GLUED)) == len(_GLUED) + 1


def test_unglue_sigmet_ahl_leaves_newline_ahl_unchanged() -> None:
    text = "TOPS TO FL330.\nWSUS32 KKCI 261355\n"
    assert _unglue_sigmet_ahl(text) == text


def test_find_sigmet_reports_dual_fir_oceanic() -> None:
    body = (
        "\nKZWY KZMA SIGMET DELTA 10 VALID 260210/260610 KKCI-\n"
        "NEW YORK OCEANIC FIR MIAMI OCEANIC FIR FRQ TS OBS AT 0210Z WI "
        "N2617 W07254. TOP FL530. MOV ENE 15KT. INTSF.\n"
    )
    reports = _find_sigmet_reports(body)
    assert len(reports) == 1
    assert reports[0].startswith("KZWY KZMA SIGMET")


def test_find_sigmet_reports_convective_with_wst_preamble() -> None:
    body = (
        "\nMKCE WST 261655\n\nCONVECTIVE SIGMET 8E\nVALID UNTIL 1855Z\n"
        "FL AND CSTL WTRS\nFROM 140E PBI\nAREA TS MOV FROM 06025KT. TOPS TO FL330.\n"
    )
    reports = _find_sigmet_reports(body)
    assert len(reports) == 1
    assert "CONVECTIVE SIGMET 8E" in reports[0].upper()
    assert "MKCE WST 261655" in reports[0]


def test_find_sigmet_reports_glued_ahl_yields_two() -> None:
    body = (
        "\nMKCE WST 261655\n\nCONVECTIVE SIGMET 8E\nVALID UNTIL 1855Z\n"
        "FL\nFROM 140E PBI\nAREA TS MOV FROM 06025KT. TOPS TO FL330.WSUS32 KKCI 261355\n"
        "MKCC WST 261355\n\nCONVECTIVE SIGMET 41C\nVALID UNTIL 1555Z\n"
        "TX\nFROM 50NNE TCC\nAREA TS MOV FROM 21030KT. TOPS TO FL320.\n"
    )
    reports = _find_sigmet_reports(body)
    assert len(reports) == 2
    assert "8E" in reports[0].upper()
    assert "41C" in reports[1].upper()
    assert "WSUS32 KKCI 261355" not in reports[0]


def test_split_oceanic_multi_fir_product_and_ahl() -> None:
    result = split_bulletin(_OCEANIC, product="SIGMET")
    assert result.meta.tt == "WS"
    assert result.meta.aa == "NT"
    assert result.meta.cccc == "KKCI"
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("KZWY KZMA SIGMET DELTA 10")


def test_split_us_convective_wst_single() -> None:
    result = split_bulletin(_WST_CONVECTIVE, product="SIGMET")
    assert result.meta.tt == "WS"
    assert result.meta.report_count == 1
    assert "CONVECTIVE SIGMET 8E" in result.reports[0].upper()


def test_split_operator_paste_five_reports_ordered() -> None:
    result = split_bulletin(_OPERATOR, product="SIGMET")
    assert result.meta.report_count == 5
    assert result.reports[0].startswith("KZWY KZMA SIGMET")
    tags = [r.upper() for r in result.reports[1:]]
    assert any("CONVECTIVE SIGMET 8E" in t for t in tags)
    assert any("CONVECTIVE SIGMET 41C" in t for t in tags)
    assert any("CONVECTIVE SIGMET 59C" in t for t in tags)
    assert any("CONVECTIVE SIGMET 60C" in t for t in tags)


def test_split_convective_trailer_keeps_hazard_lines() -> None:
    result = split_bulletin(_TRAILER, product="SIGMET")
    assert result.meta.report_count == 1
    upper = result.reports[0].upper()
    for token in ("INTSF", "SEV", "HAIL", "WIND GUSTS"):
        assert token in upper


def test_split_rejects_vaa_under_sigmet_product() -> None:
    text = "WSUS31 KKCI 261655\nVA ADVISORY\nDTG: 20261026/1200Z=\n"
    with pytest.raises(BulletinSplitError) as exc_info:
        split_bulletin(text, product="SIGMET")
    assert exc_info.value.code == "empty_bulletin"


def test_parse_convective_sigmet_accepts_wst_preamble_line() -> None:
    """WST YYGGgg between unit and CONVECTIVE must still parse (slot builder)."""
    tac = (
        "MKCE WST 261655 CONVECTIVE SIGMET 8E VALID UNTIL 1855Z "
        "FL AND CSTL WTRS FROM 140E PBI-20ESE MIA "
        "AREA TS MOV FROM 06025KT. TOPS TO FL330."
    )
    parsed = _parse_convective_sigmet(tac)
    assert parsed is not None
    assert parsed["convective"] is True
    assert parsed["convective_tag"] == "8E"
    assert parsed["fir"] == "MKCE"
