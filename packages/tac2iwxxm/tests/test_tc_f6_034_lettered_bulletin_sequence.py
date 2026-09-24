"""TC-F6-034: lettered SIGMET and AIRMET bulletin sequence.

The single-report parser already accepts a letter plus digits and a word plus
digits. Bulletin split must accept the same forms. Digits-only sequences stay.

[Corpus: product §F6] [Corpus: tests §TC-F6-034]
"""

from __future__ import annotations

from pathlib import Path

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "sigmet"

_SIGMET_A02 = """\
WSAU01 YMMC 121200
YMMM SIGMET A02 VALID 101200/101600 YUSO-
YMMM SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
"""

_AIRMET_A02 = """\
WAAU01 YMMC 121200
YMMM AIRMET A02 VALID 151520/151800 YUSO-
YMMM SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN=
"""

_SIGMET_ALPHA = """\
WSAU01 YMMC 121200
YMMM SIGMET ALPHA 02 VALID 101200/101600 YUSO-
YMMM SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
"""

_SIGMET_DIGITS = """\
WSUK31 EGRR 121200
YUDD SIGMET 3 VALID 101200/101600 YUSO-
YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN=
"""


def _convert(report: str, product: str):
    from tac2iwxxm import convert

    return convert(
        report,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )


def test_ymmm_sigmet_a02_splits_and_converts() -> None:
    """A letter-plus-digits SIGMET bulletin is one report and converts."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_SIGMET_A02, product="SIGMET")
    assert split.meta.report_count == 1
    assert split.reports[0].startswith("YMMM SIGMET A02 ")
    result = _convert(split.reports[0], "SIGMET")
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert "iwxxm:SIGMET" in result.xml


def test_ymmm_airmet_a02_splits_and_converts() -> None:
    """The same letter-plus-digits shape splits and converts as AIRMET."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_AIRMET_A02, product="AIRMET")
    assert split.meta.report_count == 1
    assert split.reports[0].startswith("YMMM AIRMET A02 ")
    result = _convert(split.reports[0], "AIRMET")
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert "iwxxm:AIRMET" in result.xml


def test_sigmet_alpha_02_splits() -> None:
    """A word-plus-digits sequence splits into one SIGMET report."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_SIGMET_ALPHA, product="SIGMET")
    assert split.meta.report_count == 1
    assert "SIGMET ALPHA 02 " in split.reports[0]


def test_sigmet_3_still_splits() -> None:
    """A digits-only sequence keeps the current split."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_SIGMET_DIGITS, product="SIGMET")
    assert split.meta.report_count == 1
    assert split.reports[0].startswith("YUDD SIGMET 3 ")

    multi = (FIXTURES / "sigmet_multi_ahl.txt").read_text(encoding="utf-8")
    reports = split_bulletin(multi, product="SIGMET").reports
    assert len(reports) == 2
    assert any(report.startswith("YUDD SIGMET 3 ") for report in reports)
