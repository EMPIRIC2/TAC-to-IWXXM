"""Selectable profiles for formats the four legacy names do not represent.

[Corpus: product §F6] [Corpus: product §F7] [Corpus: tests]
"""

from __future__ import annotations

from iwxxm_validate import validate
from tac_validate import lint

from tac2iwxxm import convert

_CONV = """\
WSUS32 KKCI 231555
SIGC
CONVECTIVE SIGMET 75C
VALID UNTIL 1755Z
TX OK KS CO NM
FROM 30SW GCK-60SSE MMB-40SE CDS-40W TCC-20NNW TBE-30SW GCK
AREA TS MOV FROM 21030KT. TOPS TO FL320.
"""

_INTL = """\
YUDD SIGMET 2 VALID 101200/101600 YUSO-
YUDD SHANLON FIR/UIR SEV TURB OBS AT 1200Z WI N4230 E02115 - N4315 E02145 - N4245 E02200 - N4230 E02115 FL250 MOV E 20KT INTSF=
"""


def test_convective_profile_converts_and_lints() -> None:
    result = convert(_CONV, product="SIGMET", profile="US_NWS_CONVECTIVE_SIGMET")
    assert result.ok, result.issues
    assert result.xml is not None
    assert "AreaTS" in result.xml
    report = lint(_CONV, product="SIGMET", profile="US_NWS_CONVECTIVE_SIGMET")
    assert report.ok


def test_convective_profile_rejects_an_international_sigmet() -> None:
    result = convert(_INTL, product="SIGMET", profile="us_nws_convective_sigmet", iwxxm_version="2025-2")
    assert result.ok is False
    assert any(issue.code == "NOT_CONVECTIVE_SIGMET" for issue in result.issues)
    report = lint(_INTL, product="SIGMET", profile="US_NWS_CONVECTIVE_SIGMET")
    assert report.ok is False
    assert any(issue.code == "NOT_CONVECTIVE_SIGMET" for issue in report.issues)


def test_annex3_international_sigmet_is_unchanged() -> None:
    selected = convert(_INTL, product="SIGMET", profile="US_NWS_CONVECTIVE_SIGMET", iwxxm_version="2025-2")
    annex = convert(_INTL, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    assert selected.ok is False
    assert annex.ok, annex.issues
    assert annex.xml is not None
    assert "SIGMET" in annex.xml
    assert "NOT_CONVECTIVE_SIGMET" not in annex.xml


def test_waiting_profiles_refuse_convert_and_lint() -> None:
    cases = (
        ("US_NWS_G_AIRMET", "AIRMET", "AIRMET ZULU"),
        ("US_NWS_VONA", "VONA", "VONA"),
        ("CA_MSC_SIGMET", "SIGMET", "CZQX SIGMET"),
    )
    for profile, product, tac in cases:
        result = convert(tac, product=product, profile=profile)
        assert result.ok is False, profile
        assert any(issue.code == "SOURCE_UNAVAILABLE" for issue in result.issues), profile
        report = lint(tac, product=product, profile=profile)
        assert report.ok is False
        assert any(issue.code == "SOURCE_UNAVAILABLE" for issue in report.issues)


def test_canadian_sigmet_profile_checks_a_published_file() -> None:
    source = """\
WSNT01 CWAO 231522
CZQX SIGMET F2 VALID 231520/231920 CWUL-
CZQX GANDER OCEANIC FIR/CTA SEV TURB OBS AT 1509Z WI 180NM WID LINE BTN N5630 W03900 - N6130 W03200 FL310/360 MOV WNW 10KT WKN=
"""
    built = convert(source, product="SIGMET", profile="ca_eccc")
    assert built.ok, built.issues
    assert built.xml is not None
    report = validate(built.xml, iwxxm_version="3.0.0", profile="ca_msc_sigmet", product="SIGMET", levels=["xsd"])
    assert report.profile == "ca_msc_sigmet"
    blocking = [issue for issue in report.issues if issue.severity == "error"]
    assert not blocking, [(issue.code, issue.message) for issue in blocking]
