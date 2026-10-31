"""Live TAF PROB+period is warning; PROB+BECMG stays error (#1487/#1488/#1489)."""

from __future__ import annotations

import pytest
from tac_validate import lint

# Stage live samples (EV-live-map-stage-recheck-2026-10-31) — abbreviated bodies.
_CYOW = (
    "TAF CYOW 311440Z 3115/0118 VRB03KT P6SM FEW050 BECMG 3116/3118 28010KT "
    "BECMG 3122/3124 VRB03KT FM010800 25005KT P6SM FEW006 "
    "PROB30 0108/0112 1SM BR FM011500 24008KT P6SM FEW040="
)
_EGLL = (
    "TAF EGLL 311055Z 3112/0118 08005KT 9999 SCT020 BECMG 3121/3124 5000 HZ "
    "TEMPO 0100/0103 2000 MIFG BR BKN002 PROB30 0101/0103 0300 FG VV/// "
    "BECMG 0103/0106 0300 FG VV///="
)
_KIAH = (
    "TAF KIAH 311720Z 3118/0124 10005KT P6SM SCT010 BKN025 "
    "FM311900 07005KT P6SM SCT020 BKN035 PROB30 3119/3121 -SHRA "
    "FM010700 VRB03KT 6SM BR FEW003 OVC007="
)
_HKJK = (
    "TAF HKJK 302300Z 3100/0106 02005KT 9999 BKN020 "
    "PROB30 BECMG 3114/3117 -RA FEW022CB BKN080="
)
_NVVA = (
    "TAF NVVA 310500Z 3106/0106 11010KT 9999 SCT020 BKN040 "
    "PROB30 INTER 3106/3112 9000 SHRA BKN018="
)
_TEMPO_OK = (
    "TAF MZBZ 081200Z 0812/0912 12010KT 9999 FEW020 PROB40 TEMPO 0818/0822 4000 TSRA="
)


@pytest.mark.parametrize(
    "tac",
    [_CYOW, _EGLL, _KIAH],
    ids=["CYOW", "EGLL", "KIAH"],
)
def test_bug_2026_10_31_prob_period_is_warning(tac: str) -> None:
    report = lint(tac, product="TAF")
    codes = {i.code: i.severity for i in report.issues}
    assert codes.get("PROB_PERIOD_WITHOUT_TEMPO") == "warning"
    assert "INVALID_PROB" not in codes
    assert report.ok is True


def test_bug_2026_10_31_prob_inter_is_warning() -> None:
    report = lint(_NVVA, product="TAF")
    assert any(
        i.code == "PROB_PERIOD_WITHOUT_TEMPO" and i.severity == "warning"
        for i in report.issues
    )
    assert report.ok is True


def test_bug_2026_10_31_prob_becmg_still_error() -> None:
    report = lint(_HKJK, product="TAF")
    assert report.ok is False
    assert any(
        i.code == "INVALID_PROB" and i.severity == "error" for i in report.issues
    )


def test_bug_2026_10_31_prob_tempo_still_info() -> None:
    report = lint(_TEMPO_OK, product="TAF")
    assert any(i.code == "PROB_PRESENT" and i.severity == "info" for i in report.issues)
    assert "INVALID_PROB" not in {i.code for i in report.issues}
    assert "PROB_PERIOD_WITHOUT_TEMPO" not in {i.code for i in report.issues}
