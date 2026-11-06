"""Anti-soften guards for keep-as-error live 30d residuals (#1556 / epic #1551).

Plain AUTO omissions and true INVALID_PROB stay lint **error**. Do not soften
MISSING_VISIBILITY / MISSING_QNH for CW*, invent Europe blankets, or remap
INVALID_PROB. Convert may still emit TRANSLATION_FAILED warn — out of scope.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tests.bugs.live_tac_eval.helpers import assert_has_code, lint_annex3

# Live-map / NA AUTO snippets (session live-tac-eval-30d; no secrets).
_KHLC_MISSING_VIS = (
    "METAR KHLC 021153Z AUTO 21015G35KT FEW017 SCT026 SCT034 21/17 A2961 "
    "RMK AO2 PK WND 21035/1145 SLP010 60000 T02060172 10206 20178 55004 $"
)
# US AUTO omitted altimeter (not CW*/CZ* — those stay error too, separately).
_KDEN_MISSING_QNH = "METAR KDEN 021100Z AUTO 14002KT 10SM FEW020 06/05 RMK AO2"
# CW* AWS: VIS + QNH omissions must remain error (no Canada soften).
_CWDQ_MISSING_VIS_QNH = (
    "METAR CWDQ 021100Z AUTO 14002KT 06/05 RMK AO1 SLP214 T00630051 50002"
)
_K05U_MISSING_WIND = (
    "METAR K05U 021155Z AUTO 10SM OVC048 03/02 A3023 RMK AO2 10038 20017 70002"
)
# Minimal NA AUTO omitting temperature/dewpoint group.
_KDEN_MISSING_TEMP_DEWPOINT = (
    "METAR KDEN 021153Z AUTO 18012KT 10SM FEW040 A3005 RMK AO2"
)
# Minimal NA METAR omitting observation time (ddhhmmZ).
_KJFK_MISSING_OBS_TIME = "METAR KJFK AUTO 18012KT 10SM FEW040 15/07 A3005"
# Truncated / illegal PROB structure (OKKK live: PROB30 TEM PO …).
_OKKK_INVALID_PROB = (
    "TAF OKKK 011700Z 0118/0224 12010G20KT 7000 FEW040 BKN080 "
    "TEMPO 0118/0206 4000 -TSRA FEW030CB TEMPO 0120/0206 VRB03KT 2000 BR HZ "
    "PROB30 TEM PO 0123/0203 0800 FG"
)

# (case_id, product, icao, tac, expected_error_codes)
_KEEP_AS_ERROR_CASES: list[tuple[str, str, str, str, tuple[str, ...]]] = [
    (
        "khlc_auto_omitted_vis",
        "METAR",
        "KHLC",
        _KHLC_MISSING_VIS,
        ("MISSING_VISIBILITY",),
    ),
    (
        "kden_auto_omitted_qnh",
        "METAR",
        "KDEN",
        _KDEN_MISSING_QNH,
        ("MISSING_QNH",),
    ),
    (
        "cwdq_aws_omitted_vis_and_qnh",
        "METAR",
        "CWDQ",
        _CWDQ_MISSING_VIS_QNH,
        ("MISSING_VISIBILITY", "MISSING_QNH"),
    ),
    (
        "k05u_auto_omitted_wind",
        "METAR",
        "K05U",
        _K05U_MISSING_WIND,
        ("MISSING_WIND",),
    ),
    (
        "kden_auto_omitted_temp_dewpoint",
        "METAR",
        "KDEN",
        _KDEN_MISSING_TEMP_DEWPOINT,
        ("MISSING_TEMP_DEWPOINT",),
    ),
    (
        "kjfk_omitted_obs_time",
        "METAR",
        "KJFK",
        _KJFK_MISSING_OBS_TIME,
        ("MISSING_OBS_TIME",),
    ),
    (
        "okkk_malformed_prob",
        "TAF",
        "OKKK",
        _OKKK_INVALID_PROB,
        ("INVALID_PROB",),
    ),
]


@pytest.mark.parametrize(
    ("case_id", "product", "icao", "tac", "codes"),
    _KEEP_AS_ERROR_CASES,
    ids=[row[0] for row in _KEEP_AS_ERROR_CASES],
)
def test_live_omission_and_invalid_prob_stay_error(
    case_id: str,
    product: str,
    icao: str,
    tac: str,
    codes: tuple[str, ...],
) -> None:
    """Each keep-as-error code must remain severity error under prefer/annex3."""
    del case_id  # used as parametrize id only
    report = lint_annex3(tac, product=product, icao=icao)
    for code in codes:
        assert_has_code(report, code, severity="error")
