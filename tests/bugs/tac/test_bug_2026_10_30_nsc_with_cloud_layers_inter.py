"""BUG-2026-10-30 — NSC_WITH_CLOUD_LAYERS must not cross INTER groups.

FAQ §14.3 exclusivity is same-group only. AU TAF ``INTER`` was not a
segment boundary, so ``NSC`` + later ``SCT`` in ``INTER`` warned.

Live-map full-world probe 2026-10-30: YMHB / YSDU, pass=true.
Ticket: #1478. [Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint

_YMHB = (
    "TAF YMHB 302006Z 3021/3118 32006KT CAVOK BECMG 3023/3100 35018G32KT CAVOK "
    "FM310200 35020G38KT 9999 -SHRA NSC BECMG 3104/3106 26014KT 9999 -SHRA NSC "
    "INTER 3104/3106 5000 SHRA SCT050TCU"
)

_YSDU = (
    "TAF YSDU 301652Z 3018/3112 03010KT CAVOK FM302100 01015G25KT 9999 -SHRA BKN025 "
    "FM310300 34014KT 9999 -SHRA NSC INTER 3021/3100 4000 SHRA BKN015 "
    "PROB30 INTER 3104/3107 VRB25G40KT 2000 TSRA FEW065CB "
    "PROB30 TEMPO 3107/3111 VRB30G50KT 1000 TSRAGR SCT010 SCT065CB"
)


def test_bug_2026_10_30_ymhb_nsc_then_inter_sct_no_warning() -> None:
    codes = {i.code for i in lint(_YMHB, product="TAF").issues}
    assert "NSC_WITH_CLOUD_LAYERS" not in codes
    assert "NSC_PRESENT" in codes


def test_bug_2026_10_30_ysdu_nsc_then_inter_bkn_no_warning() -> None:
    codes = {i.code for i in lint(_YSDU, product="TAF").issues}
    assert "NSC_WITH_CLOUD_LAYERS" not in codes


def test_bug_2026_10_30_same_group_nsc_few_still_warns() -> None:
    tac = "TAF KJFK 121230Z 1212/1312 18010KT P6SM NSC FEW015="
    hits = [
        i for i in lint(tac, product="TAF").issues if i.code == "NSC_WITH_CLOUD_LAYERS"
    ]
    assert hits
