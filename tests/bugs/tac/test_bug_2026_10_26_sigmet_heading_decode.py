"""BUG-2026-10-26 — Multi-bulletin SIGMET paste must not empty_bulletin.

Oceanic multi-FIR SIGMET plus US CONVECTIVE SIGMET (WST/WSUS) pastes, including
glued next-AHL boundaries like ``FL330.WSUS32``, must split into reports so
heading paste / live decode do not return empty_bulletin.

[Corpus: product §F6] [Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.heading_paste import (
    EMPTY_HEADING,
    HeadingPasteError,
    reports_for_convert,
)

from tac2iwxxm import BulletinSplitError, split_bulletin

# Operator paste (newlines preserved; glued FL330.WSUS32 / FL320.WSUS32 kept).
_OPERATOR_PASTE = """\
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

_OCEANIC_MULTI_FIR = """\
WSNT04 KKCI 260210
KZWY KZMA SIGMET DELTA 10 VALID 260210/260610 KKCI-
NEW YORK OCEANIC FIR MIAMI OCEANIC FIR FRQ TS OBS AT 0210Z WI
N2617 W07254 - N2617 W06818 - N2319 W06726 - N2029 W07026 - N2032
W07256 - N1958 W07328 - N2034 W07356 - N2617 W07254. TOP FL530.
MOV ENE 15KT. INTSF.
"""

_US_CONVECTIVE_WST = """\
WSUS31 KKCI 261655
MKCE WST 261655

CONVECTIVE SIGMET 8E
VALID UNTIL 1855Z
FL AND CSTL WTRS
FROM 140E PBI-180ESE MIA-150SE MIA-40S EYW-20ESE MIA-140E PBI
AREA TS MOV FROM 06025KT. TOPS TO FL330.
"""

_GLUED_AHL_TWO_BULLETINS = """\
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
AREA TS MOV FROM 21030KT. TOPS TO FL320.
"""

_CONVECTIVE_INTSF_TRAILER = """\
WSUS32 KKCI 262155
MKCC WST 262155

CONVECTIVE SIGMET 60C
VALID UNTIL 2355Z
NM
FROM 20NW CME-30E CME-40S CME-50WSW CME-20NW CME
INTSF AREA SEV TS MOV FROM 23010KT. TOPS ABV FL450.
HAIL TO 1 IN...WIND GUSTS TO 50KT POSS.
"""


def _assert_not_empty_bulletin(text: str) -> None:
    result = split_bulletin(text, product="SIGMET")
    assert result.meta.report_count >= 1
    assert result.reports
    pasted = reports_for_convert(text, "SIGMET")
    assert pasted is not None
    assert len(pasted.reports) >= 1


def test_bug_2026_10_26_oceanic_multi_fir_splits() -> None:
    """Profile 1: dual-FIR oceanic SIGMET after WSNT AHL."""
    result = split_bulletin(_OCEANIC_MULTI_FIR, product="SIGMET")
    assert result.meta.ahl == "WSNT04 KKCI 260210"
    assert result.meta.tt == "WS"
    assert result.meta.report_count == 1
    assert result.reports[0].startswith("KZWY KZMA SIGMET")
    assert "DELTA 10" in result.reports[0]
    assert "NEW YORK OCEANIC FIR" in result.reports[0]
    assert "MIAMI OCEANIC FIR" in result.reports[0]
    _assert_not_empty_bulletin(_OCEANIC_MULTI_FIR)


def test_bug_2026_10_26_us_convective_wst_splits() -> None:
    """Profile 2: CCCC WST YYGGgg preamble then CONVECTIVE SIGMET body."""
    result = split_bulletin(_US_CONVECTIVE_WST, product="SIGMET")
    assert result.meta.ahl.startswith("WSUS31")
    assert result.meta.report_count == 1
    report = result.reports[0]
    assert "MKCE WST 261655" in report
    assert "CONVECTIVE SIGMET 8E" in report.upper()
    assert "VALID UNTIL 1855Z" in report.upper()
    assert not report.startswith("KZWY")
    _assert_not_empty_bulletin(_US_CONVECTIVE_WST)


def test_bug_2026_10_26_glued_ahl_unglues_next_bulletin() -> None:
    """Profile 3: FL330.WSUS32 with no newline still yields two reports."""
    result = split_bulletin(_GLUED_AHL_TWO_BULLETINS, product="SIGMET")
    assert result.meta.report_count == 2
    first, second = result.reports
    assert "CONVECTIVE SIGMET 8E" in first.upper()
    assert "FL330" in first.upper()
    assert "WSUS32" not in first.split("FL330", 1)[-1][:20].replace(".", "")
    assert "CONVECTIVE SIGMET 41C" in second.upper()
    assert "MKCC WST 261355" in second
    # Glued token must not leave the next AHL stuck inside the first report body.
    assert "WSUS32 KKCI 261355" not in first
    assert "WSUS32 KKCI 261355" not in _GLUED_AHL_TWO_BULLETINS.split("FL330.", 1)[0]
    _assert_not_empty_bulletin(_GLUED_AHL_TWO_BULLETINS)


def test_bug_2026_10_26_operator_paste_splits_all_reports() -> None:
    """Profile 4: mixed oceanic + several convective WST reports in one paste."""
    result = split_bulletin(_OPERATOR_PASTE, product="SIGMET")
    assert result.meta.ahl == "WSNT04 KKCI 260210"
    assert result.meta.report_count == 5
    assert len(result.reports) == 5
    oceanic = [r for r in result.reports if r.startswith("KZWY KZMA SIGMET")]
    assert len(oceanic) == 1
    convective = [r for r in result.reports if "CONVECTIVE SIGMET" in r.upper()]
    assert len(convective) == 4
    tags = " ".join(convective).upper()
    for tag in ("8E", "41C", "59C", "60C"):
        assert f"CONVECTIVE SIGMET {tag}" in tags
    # Glued boundaries must not swallow later convective reports.
    assert any("CONVECTIVE SIGMET 41C" in r.upper() for r in result.reports)
    assert any("CONVECTIVE SIGMET 59C" in r.upper() for r in result.reports)


def test_bug_2026_10_26_convective_intsf_sev_hail_gusts_trailer() -> None:
    """Profile 5: CONVECTIVE with INTSF / SEV / HAIL / WIND GUSTS trailer lines."""
    result = split_bulletin(_CONVECTIVE_INTSF_TRAILER, product="SIGMET")
    assert result.meta.report_count == 1
    report = result.reports[0].upper()
    assert "CONVECTIVE SIGMET 60C" in report
    assert "INTSF" in report
    assert "SEV" in report
    assert "HAIL" in report
    assert "WIND GUSTS" in report
    _assert_not_empty_bulletin(_CONVECTIVE_INTSF_TRAILER)


def test_bug_2026_10_26_heading_paste_not_empty_bulletin() -> None:
    pasted = reports_for_convert(_OPERATOR_PASTE, "SIGMET")
    assert pasted is not None
    assert len(pasted.reports) == 5
    first = pasted.reports[0]
    first_text = first[0] if isinstance(first, tuple) else first
    assert str(first_text).startswith("KZWY KZMA SIGMET")


def test_bug_2026_10_26_heading_only_still_empty() -> None:
    with pytest.raises(BulletinSplitError) as split_exc:
        split_bulletin("WSNT04 KKCI 260210\n", product="SIGMET")
    assert split_exc.value.code == "empty_bulletin"
    assert "No TAC reports found" in split_exc.value.message

    with pytest.raises(HeadingPasteError) as paste_exc:
        reports_for_convert("WSNT04 KKCI 260210\n", "SIGMET")
    assert paste_exc.value.code == "empty_bulletin"
    assert paste_exc.value.message == EMPTY_HEADING
