"""Anti-soften guards for keep-as-error live 30d residuals.

Plain AUTO omissions and true INVALID_PROB stay error. Do not soften
MISSING_VISIBILITY / MISSING_QNH for CW*, or INVALID_PROB.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate.api import lint_with_profile

# Live-map snippets (session live-tac-eval-30d; no secrets).
_KHLC_MISSING_VIS = (
    "METAR KHLC 021153Z AUTO 21015G35KT FEW017 SCT026 SCT034 21/17 A2961 "
    "RMK AO2 PK WND 21035/1145 SLP010 60000 T02060172 10206 20178 55004 $"
)
_CWDQ_MISSING_VIS_QNH = (
    "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214 T00630051 50002"
)
_K05U_MISSING_WIND = (
    "METAR K05U 021155Z AUTO 10SM OVC048 03/02 A3023 RMK AO2 10038 20017 70002"
)
# Truncated / illegal PROB structure (OKKK live: PROB30 TEM PO …).
_OKKK_INVALID_PROB = (
    "TAF OKKK 011700Z 0118/0224 12010G20KT 7000 FEW040 BKN080 "
    "TEMPO 0118/0206 4000 -TSRA FEW030CB TEMPO 0120/0206 VRB03KT 2000 BR HZ "
    "PROB30 TEM PO 0123/0203 0800 FG"
)


def test_khlc_auto_omitted_vis_stays_missing_visibility_error() -> None:
    report = lint_with_profile(
        _KHLC_MISSING_VIS, product="METAR", profile="annex3", icao="KHLC"
    )
    matched = [i for i in report.issues if i.code == "MISSING_VISIBILITY"]
    assert matched
    assert all(i.severity == "error" for i in matched)


def test_cwdq_aws_omitted_vis_and_qnh_stay_error() -> None:
    report = lint_with_profile(
        _CWDQ_MISSING_VIS_QNH, product="METAR", profile="annex3", icao="CWDQ"
    )
    codes = {i.code: i.severity for i in report.issues}
    assert codes.get("MISSING_VISIBILITY") == "error"
    assert codes.get("MISSING_QNH") == "error"


def test_k05u_auto_omitted_wind_stays_missing_wind_error() -> None:
    report = lint_with_profile(
        _K05U_MISSING_WIND, product="METAR", profile="annex3", icao="K05U"
    )
    matched = [i for i in report.issues if i.code == "MISSING_WIND"]
    assert matched
    assert all(i.severity == "error" for i in matched)


def test_okkk_malformed_prob_stays_invalid_prob_error() -> None:
    report = lint_with_profile(
        _OKKK_INVALID_PROB, product="TAF", profile="annex3", icao="OKKK"
    )
    matched = [i for i in report.issues if i.code == "INVALID_PROB"]
    assert matched
    assert all(i.severity == "error" for i in matched)
