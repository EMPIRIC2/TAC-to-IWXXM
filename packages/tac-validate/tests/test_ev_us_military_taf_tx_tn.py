"""EV-us-military-taf-tx-tn — end-of-TAF TX/TN under us_military.

KBIX-style military TAF places TX/TN after BECMG/TEMPO. Annex3 keeps
INVALID_TX_TN; us_military accepts as TX_TN_PRESENT.
[Corpus: product §F20] [Corpus: product §F36] [Corpus: tests §TC-EV-USMIL-TX-TN-001]
"""

from __future__ import annotations

from tac_validate import lint

# Live campaign sample (HF-live-map-warn-error-campaign / KBIX).
_KBIX_END_TX_TN = (
    "TAF KBIX 301800Z 3018/3124 11012KT 9999 FEW050 SCT180 BKN250 QNH3003INS "
    "BECMG 3100/3101 07009KT 9999 SCT050 BKN180 OVC250 QNH3004INS "
    "BECMG 3116/3117 12012G18KT 9999 VCSH BKN030 BKN120 BKN180 QNH3001INS "
    "TEMPO 3118/3124 8000 -SHRA VCTS BKN025CB OVC080 TX26/3018Z TN18/3111Z"
)

_BASE_TX_TN = "TAF LFPG 301700Z 3018/3124 27010KT CAVOK TX17/3114Z TN02/3104Z BECMG 3021/3023 4000 BR="


def test_kbix_end_tx_tn_errors_under_annex3() -> None:
    report = lint(_KBIX_END_TX_TN, product="TAF", profile="annex3")
    codes = {i.code for i in report.issues}
    assert "INVALID_TX_TN" in codes
    assert any(i.code == "INVALID_TX_TN" and i.severity == "error" for i in report.issues)


def test_kbix_end_tx_tn_accepted_under_us_military() -> None:
    report = lint(_KBIX_END_TX_TN, product="TAF", profile="us_military")
    codes = {i.code for i in report.issues}
    assert "INVALID_TX_TN" not in codes
    assert "TX_TN_PRESENT" in codes
    assert all(i.severity != "error" or i.code != "INVALID_TX_TN" for i in report.issues)


def test_base_tx_tn_info_under_both_profiles() -> None:
    for profile in ("annex3", "us_military"):
        report = lint(_BASE_TX_TN, product="TAF", profile=profile)
        codes = {i.code for i in report.issues}
        assert "INVALID_TX_TN" not in codes
        assert "TX_TN_PRESENT" in codes


def test_tx_tn_after_change_group_accepted_under_us_military() -> None:
    """us_military treats TX/TN after the first BECMG/TEMPO as TX_TN_PRESENT (not error)."""
    tac = "TAF KBIX 301800Z 3018/3124 11012KT 9999 FEW050 BECMG 3100/3101 07009KT 9999 SCT050 TX26/3018Z TN18/3111Z="
    report = lint(tac, product="TAF", profile="us_military")
    codes = {i.code for i in report.issues}
    assert "INVALID_TX_TN" not in codes
    assert "TX_TN_PRESENT" in codes
    annex = lint(tac, product="TAF", profile="annex3")
    assert "INVALID_TX_TN" in {i.code for i in annex.issues}
