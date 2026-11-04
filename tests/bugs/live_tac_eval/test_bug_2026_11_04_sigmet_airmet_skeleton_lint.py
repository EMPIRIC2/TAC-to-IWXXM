"""Lint minimum SIGMET/AIRMET skeleton (CCCC + product + VALID) (#1564).

Annex 3 identity is ``CCCC SIGMET|AIRMET … VALID YYGGgg/YYGGgg``. Stripped or
malformed headers must error before convert. Valid US WST convective forms
(convert-fail cohort from live-30d, tracked in #1552 for VOR seeding) must stay
skeleton-clean under prefer-lint ``annex3``.

[Corpus: product §F15] [Corpus: product §F23] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import lint_with_profile

# Skeleton identity / validity codes for the Annex 3 header gate.
_SKELETON_CODES = frozenset(
    {
        "MISSING_CCCC",
        "MISSING_PRODUCT_KEYWORD",
        "MISSING_VALID",
    }
)

# Live-map convert-fail sample (lint was clean; convert PARSE_ERROR is #1552).
_WST_LIVE_IND = """\
WSUS32 KKCI 040755
MKCC WST 040755
CONVECTIVE SIGMET 21C
VALID UNTIL 0955Z
TN KY IN AL IL
FROM 40NNE IND-40WNW LOZ-60W GQO-30SSE DYR-60WNW PXV-40NNE IND
AREA EMBD TS MOV FROM 23030KT. TOPS TO FL370.
"""

_WST_LIVE_LSU = """\
WSUS32 KKCI 040555
MKCC WST 040555
CONVECTIVE SIGMET 15C
VALID UNTIL 0755Z
TN AL MS LA
FROM 30NE MEM-40NNW MSL-20SE IGB-10E LSU-40SE LCH-30NE MEM
AREA EMBD TS MOV FROM 24040KT. TOPS TO FL450.
"""

_INTL_OK = (
    "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
    "YUDD FIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN="
)

_AIRMET_OK = (
    "YUDD AIRMET 1 VALID 151520/151800 YUSO-\n"
    "YUDD SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN="
)


def _error_codes(tac: str, *, product: str) -> set[str]:
    report = lint_with_profile(tac, product=product, profile="annex3")
    return {i.code for i in report.issues if i.severity == "error"}


def test_intl_sigmet_skeleton_ok_is_clean() -> None:
    assert not (_error_codes(_INTL_OK, product="SIGMET") & _SKELETON_CODES)


def test_intl_airmet_skeleton_ok_is_clean() -> None:
    assert not (_error_codes(_AIRMET_OK, product="AIRMET") & _SKELETON_CODES)


def test_sigmet_missing_valid_window_is_error() -> None:
    tac = "YUDD SIGMET 2 YUSO-\nYUDD FIR OBSC TS FCST="
    codes = _error_codes(tac, product="SIGMET")
    assert "MISSING_VALID" in codes


def test_airmet_missing_valid_window_is_error() -> None:
    tac = "YUDD AIRMET 1 YUSO-\nYUDD SHANLON FIR ISOL TS OBS="
    codes = _error_codes(tac, product="AIRMET")
    assert "MISSING_VALID" in codes


def test_sigmet_stripped_product_identity_is_error() -> None:
    """Body-only paste without SIGMET keyword."""
    codes = _error_codes("YUDD FIR OBSC TS FCST=", product="SIGMET")
    assert "MISSING_PRODUCT_KEYWORD" in codes


def test_sigmet_missing_cccc_before_product_is_error() -> None:
    """VALID present but no CCCC before SIGMET — incomplete A6 skeleton."""
    tac = "SIGMET 2 VALID 101200/101600 YUSO-\nYUDD FIR OBSC TS FCST="
    codes = _error_codes(tac, product="SIGMET")
    assert "MISSING_CCCC" in codes


def test_airmet_missing_cccc_before_product_is_error() -> None:
    tac = "AIRMET 1 VALID 151520/151800 YUSO-\nYUDD SHANLON FIR ISOL TS OBS="
    codes = _error_codes(tac, product="AIRMET")
    assert "MISSING_CCCC" in codes


def test_malformed_valid_token_is_missing_valid() -> None:
    tac = "YUDD SIGMET 2 VALID 1012/1016 YUSO-\nYUDD FIR OBSC TS FCST="
    codes = _error_codes(tac, product="SIGMET")
    assert "MISSING_VALID" in codes


def test_live_wst_convective_skeleton_stays_clean() -> None:
    """#1552 convert-fail cohort must not false-positive on skeleton codes."""
    for tac in (_WST_LIVE_IND, _WST_LIVE_LSU):
        codes = _error_codes(tac, product="SIGMET")
        assert not (codes & _SKELETON_CODES)


def test_wst_convective_without_valid_until_is_missing_valid() -> None:
    tac = (
        "WSUS32 KKCI 040755\nMKCC WST 040755\nCONVECTIVE SIGMET 21C\n"
        "TN KY IN AL IL\nFROM 40NNE IND-40WNW LOZ\nAREA TS MOV FROM 23030KT.\n"
    )
    codes = _error_codes(tac, product="SIGMET")
    assert "MISSING_VALID" in codes
    assert "MISSING_CCCC" not in codes
