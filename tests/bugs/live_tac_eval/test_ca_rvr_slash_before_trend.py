"""Canadian MANOBS RVR may put a slash before the U/D/N trend (…FT/N).

Live 30d SPECI at CYQT/CYSB fired INVALID_RVR on tokens like R07/3000V4500FT/N.
Product-rule-fix: accept optional '/' before trend (not a severity soften).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint
from tac_validate.api import lint_with_profile

# Live-map SPECI snippets (no secrets).
_CYQT_SPECI = (
    "SPECI CYQT 021154Z 05004KT 1 1/2SM R07/3000V4500FT/N BR OVC002 "
    "08/08 A3005 RMK ST8 SLP185"
)
_CYSB_SPECI = (
    "SPECI CYSB 020310Z 23005KT 3SM R22/3000V5500FT/D BR BKN001 BKN060 "
    "08/08 A3024 RMK SC4SC2 SLP253"
)
_ICAO_TENDENCY = "METAR KJFK 011200Z 18008KT 1/2SM R04/P2000N VV005 10/10 A2992="
_BAD_RVR = "METAR KJFK 011200Z 18008KT 1/2SM R04/ABC VV005 10/10 A2992="


def test_cyqt_rvr_ft_slash_n_not_invalid() -> None:
    report = lint_with_profile(
        _CYQT_SPECI, product="SPECI", profile="annex3", icao="CYQT"
    )
    assert "INVALID_RVR" not in {i.code for i in report.issues}


def test_cysb_rvr_ft_slash_d_not_invalid() -> None:
    report = lint_with_profile(
        _CYSB_SPECI, product="SPECI", profile="annex3", icao="CYSB"
    )
    assert "INVALID_RVR" not in {i.code for i in report.issues}


def test_cyqt_bare_lint_also_accepts_slash_before_trend() -> None:
    report = lint(_CYQT_SPECI, product="SPECI")
    assert "INVALID_RVR" not in {i.code for i in report.issues}


def test_icao_tendency_without_slash_still_ok() -> None:
    report = lint(_ICAO_TENDENCY, product="METAR")
    assert "INVALID_RVR" not in {i.code for i in report.issues}


def test_true_malformed_rvr_still_invalid() -> None:
    report = lint(_BAD_RVR, product="METAR")
    assert any(i.code == "INVALID_RVR" for i in report.issues)
