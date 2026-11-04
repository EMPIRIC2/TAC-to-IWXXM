"""Standalone PROB+period is valid Annex 3 — do not emit PROB_PERIOD_WITHOUT_TEMPO.

Live 30d: EFHK / ENGM style warnings were false positives.
[Corpus: product §F20] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint
from tac_validate.api import lint_with_profile

# Live-shaped standalone PROB (no TEMPO qualifier on the PROB group).
_EFHK = "TAF EFHK 041727Z 0418/0518 30010KT CAVOK PROB30 0502/0505 4000 BR BKN002="
_ENGM = (
    "TAF ENGM 041700Z 0418/0518 VRB03KT 7000 SCT002 PROB40 0418/0512 0500 FZFG VV001="
)
_CYOW_PERIOD = (
    "TAF CYOW 301800Z 3018/3118 27010KT P6SM SCT040 "
    "PROB30 3020/3024 3SM -SHRA BR BKN020="
)
_HKJK_BECMG = (
    "TAF HKJK 302300Z 3100/0106 02005KT 9999 BKN020 "
    "PROB30 BECMG 3114/3117 -RA FEW022CB BKN080="
)
_TEMPO_OK = (
    "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB40 TEMPO 0818/0822 4000 TSRA="
)


def test_standalone_prob_period_no_prob_period_without_tempo() -> None:
    for tac in (_EFHK, _ENGM, _CYOW_PERIOD):
        report = lint(tac, product="TAF", profile="annex3")
        assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}, tac
        assert "INVALID_PROB" not in {i.code for i in report.issues}, tac
        assert any(i.code == "PROB_PRESENT" for i in report.issues), tac


def test_standalone_prob_period_prefer_path_clean() -> None:
    report = lint_with_profile(_EFHK, product="TAF", profile="annex3", icao="EFHK")
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}


def test_prob_becmg_still_invalid_prob() -> None:
    report = lint(_HKJK_BECMG, product="TAF", profile="annex3")
    assert any(
        i.code == "INVALID_PROB" and i.severity == "error" for i in report.issues
    )


def test_prob_tempo_still_present_info() -> None:
    report = lint(_TEMPO_OK, product="TAF", profile="annex3")
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
