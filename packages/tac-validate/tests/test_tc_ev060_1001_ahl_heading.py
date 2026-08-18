"""TC-EV060-1001 / UJ-059: AHL heading is COM; contained TAC reports lint as product.

Spec: docs/test-plan.md TC-EV060-1001-001..002; [Corpus: product §F6] [Corpus: tests].
"""

from __future__ import annotations

from pathlib import Path

from tac_validate import lint
from tac_validate.ahl import _ahl_heading_ok

REPO = Path(__file__).resolve().parents[3]
AHL_MULTI = REPO / "apps" / "frontend" / "src" / "fixtures" / "examples" / "bodies" / "metar_multi_ahl.txt"
VAA_A7_2 = REPO / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden" / "vaa_a7_2.tac"

WELL_FORMED_AHL_METAR = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
"""

AHL_WITH_BAD_WIND = """\
SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z ZZZ00KT 10SM SCT040 21/13 A3010=
"""

MALFORMED_AHL = """\
QQUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
"""

HEADING_ONLY = "SAUS31 KZNY 121200\n"


def _heading_end(text: str) -> int:
    first = text.splitlines()[0]
    return text.find(first) + len(first)


def test_ahl_multi_metar_heading_not_product_syntax_flood() -> None:
    """TC-EV060-1001-001: well-formed AHL does not score heading as METAR syntax."""
    text = AHL_MULTI.read_text(encoding="utf-8")
    report = lint(text, product="METAR")
    codes = [i.code for i in report.issues]
    assert "MULTI_REPORT_BULLETIN" not in codes
    heading_end = _heading_end(text)
    heading_errors = [
        i
        for i in report.issues
        if i.severity == "error"
        and i.start is not None
        and i.end is not None
        and i.start < heading_end
        and i.end <= heading_end
    ]
    assert heading_errors == []
    assert not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in report.issues)


def test_ahl_contained_invalid_metar_still_linted() -> None:
    """TC-EV060-1001-001: contained METARs are still checked after split."""
    report = lint(AHL_WITH_BAD_WIND, product="METAR")
    codes = [i.code for i in report.issues]
    assert "INVALID_WIND" in codes
    heading_end = _heading_end(AHL_WITH_BAD_WIND)
    wind = next(i for i in report.issues if i.code == "INVALID_WIND")
    assert wind.start is None or wind.start >= heading_end


def test_malformed_ahl_one_bulletin_error() -> None:
    """TC-EV060-1001-002: malformed AHL yields one bulletin-level error; still splits."""
    report = lint(MALFORMED_AHL, product="METAR")
    bulletin_errors = [i for i in report.issues if i.location == "bulletin" and i.severity == "error"]
    assert len(bulletin_errors) == 1
    assert bulletin_errors[0].code == "INVALID_AHL"
    assert report.ok is False
    # Contained METAR still linted (no flood of heading-as-METAR errors).
    assert not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in report.issues)


def test_heading_only_ahl_not_metar_keyword_error() -> None:
    """Heading-only AHL is COM, not a missing METAR keyword."""
    report = lint(HEADING_ONLY, product="METAR")
    assert not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in report.issues)
    assert any(i.location == "bulletin" for i in report.issues)


def test_heading_only_without_newline_is_empty_bulletin() -> None:
    report = lint("SAUS31 KZNY 121200", product="METAR")
    assert any(i.code == "INVALID_AHL" and i.location == "bulletin" for i in report.issues)
    assert not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in report.issues)


def test_ahl_heading_ok_rejects_non_ahl() -> None:
    assert _ahl_heading_ok("not an AHL heading") is False


def test_invalid_ahl_bbb_is_bulletin_error() -> None:
    text = "SAUS31 KZNY 121200 AAZ\nMETAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\n"
    report = lint(text, product="METAR")
    assert any(i.code == "INVALID_AHL" and i.location == "bulletin" for i in report.issues)


def test_crlf_ahl_splits_without_heading_flood() -> None:
    text = "SAUS31 KZNY 121200\r\nMETAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=\r\n"
    report = lint(text, product="METAR")
    assert "MISSING_PRODUCT_KEYWORD" not in [i.code for i in report.issues]
    assert "MULTI_REPORT_BULLETIN" not in [i.code for i in report.issues]


def test_vaa_ahl_without_equals_lints_body() -> None:
    """VAA AHL may omit '=' (convert-bulletin keep-whole); not empty-bulletin INVALID_AHL."""
    text = VAA_A7_2.read_text(encoding="utf-8")
    report = lint(text, product="VAA")
    empty_body = [i for i in report.issues if i.code == "INVALID_AHL" and "no TAC reports" in i.message]
    assert empty_body == []
    assert report.ok is True
