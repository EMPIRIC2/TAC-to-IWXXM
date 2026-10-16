"""TC-F6-054: a pasted abbreviated heading converts with the reports under it."""

from __future__ import annotations

import pytest
from tac2iwxxm.heading_paste import (
    EMPTY_HEADING,
    MALFORMED_HEADING,
    HeadingPasteError,
    _classify_opening,
    _has_leading_blank,
    _opening_line,
    http_status_for_heading_error,
    reports_for_convert,
)

from tac2iwxxm import convert

_METAR = "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013="
_SPECI = "SPECI TNCM 081200Z 14006KT 9999 -SHRA FEW020 28/24 Q1013 RESHRA="
_TAF = "TAF TNCM 081200Z 0812/0912 12010KT 9999 FEW020\nBECMG 0814/0816 14012KT="
_SIGMET = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
)
_SECOND = "METAR TKPK 081200Z 12008KT 9999 FEW018 27/23 Q1014="
_DATE = "2026-10-08"


def test_st_maarten_heading_converts_the_metar() -> None:
    text = f"SAXX31 TNCM 081200\n{_METAR}"
    peeled = reports_for_convert(text, "METAR")
    assert peeled is not None
    assert peeled.heading_start == 0
    assert peeled.leading_blank is False
    assert peeled.reports == ((_METAR, text.find(_METAR)),)
    result = convert(peeled.reports[0][0], product="METAR", bulletin_date=_DATE)
    assert result.ok is True
    assert result.xml is not None
    assert "TNCM" in result.xml
    assert "METAR" in result.xml


def test_speci_taf_and_sigmet_headings_convert() -> None:
    speci = reports_for_convert(f"SPXX31 TNCM 081200\n{_SPECI}", "SPECI")
    assert speci is not None
    speci_xml = convert(speci.reports[0][0], product="SPECI", bulletin_date=_DATE)
    assert speci_xml.ok is True
    assert speci_xml.xml is not None
    assert "SPECI" in speci_xml.xml

    taf = reports_for_convert(f"FTXX31 TNCM 081200\n{_TAF}", "TAF")
    assert taf is not None
    assert "BECMG" in taf.reports[0][0]
    taf_xml = convert(taf.reports[0][0], product="TAF", bulletin_date=_DATE)
    assert taf_xml.ok is True
    assert taf_xml.xml is not None
    assert taf_xml.xml.count("<iwxxm:TAF") == 1

    sigmet = reports_for_convert(f"WSXX01 YUSO 101200\n{_SIGMET}", "SIGMET")
    assert sigmet is not None
    assert sigmet.reports[0][0].startswith("YUDD SIGMET")
    sigmet_xml = convert(sigmet.reports[0][0], product="SIGMET", bulletin_date=_DATE)
    assert sigmet_xml.ok is True
    assert sigmet_xml.xml is not None


def test_two_reports_keep_distinct_offsets() -> None:
    text = f"SAXX31 TNCM 081200\n{_METAR}\n{_SECOND}"
    peeled = reports_for_convert(text, "METAR")
    assert peeled is not None
    assert peeled.reports[0] == (_METAR, text.find(_METAR))
    assert peeled.reports[1] == (_SECOND, text.find(_SECOND))
    assert peeled.reports[1][1] > peeled.reports[0][1]


def test_indented_heading_after_a_blank_line() -> None:
    text = f"\n  SAXX31 TNCM 081200\n{_METAR}"
    peeled = reports_for_convert(text, "METAR")
    assert peeled is not None
    assert peeled.heading_start == 3
    assert peeled.leading_blank is True
    assert peeled.reports[0][0] == _METAR
    assert _opening_line(text) == ("SAXX31 TNCM 081200", 3)
    assert _opening_line("\n") == ("", 1)
    assert _opening_line("") == ("", 0)
    assert _has_leading_blank("\n\nSAXX31 TNCM 081200") is True
    assert _has_leading_blank("SAXX31 TNCM 081200") is False
    assert _has_leading_blank("") is False


def test_plain_paste_and_empty_buffer_stay_unsplit() -> None:
    assert reports_for_convert(_METAR, "METAR") is None
    assert reports_for_convert("", "METAR") is None
    assert reports_for_convert("  \n", "METAR") is None
    assert _classify_opening("METAR TNCM 081200Z") == "plain"
    assert _classify_opening("SAXX31 TNCM 081200") == "heading"


def test_heading_without_a_report_names_the_empty_bulletin() -> None:
    with pytest.raises(HeadingPasteError) as caught:
        reports_for_convert("SAXX31 TNCM 081200", "METAR")
    assert caught.value.code == "empty_bulletin"
    assert caught.value.message == EMPTY_HEADING
    assert http_status_for_heading_error(caught.value.code) == 400


def test_malformed_heading_names_the_heading() -> None:
    with pytest.raises(HeadingPasteError) as unsupported:
        reports_for_convert(f"QQXX31 TNCM 081200\n{_METAR}", "METAR")
    assert unsupported.value.code == "INVALID_AHL"
    assert unsupported.value.message == MALFORMED_HEADING
    assert http_status_for_heading_error("INVALID_AHL") == 422

    with pytest.raises(HeadingPasteError) as bad_bbb:
        _classify_opening("SAXX31 TNCM 081200 AAZ")
    assert bad_bbb.value.code == "INVALID_AHL"

    with pytest.raises(HeadingPasteError) as empty_line:
        _classify_opening("")
    assert empty_line.value.code == "INVALID_AHL"

    with pytest.raises(HeadingPasteError) as mismatch:
        reports_for_convert(f"SAXX31 TNCM 081200\n{_METAR}", "SPECI")
    assert mismatch.value.code == "INVALID_AHL"
    assert mismatch.value.message == MALFORMED_HEADING
