"""CA / national TAF RMK trailers must not drive decode residuals.

Live 30d: 161/176 TAF partials were only RMK NXT FCST BY / AUTO OBS / PH* tails.
[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding import decode_tac

_CYAZ = (
    "TAF CYAZ 041740Z 0418/0424 12010G20KT P6SM SCT020 BKN120 "
    "TEMPO 0418/0421 P6SM -RA BKN020 OVC120 "
    "FM042100 12015G25KT P6SM BKN020 OVC120 "
    "RMK NXT FCST BY 04Z="
)
_CYBC_AUTO = (
    "TAF CYBC 041940Z 0420/0508 07007KT P6SM OVC012 "
    "TEMPO 0420/0502 3SM -RA -DZ BR OVC008 "
    "RMK FCST BASED ON AUTO OBS. NXT FCST BY 06Z="
)
_SBAT_PHD = (
    "TAF SBAT 040300Z 0406/0418 07005KT 9999 SCT020 "
    "TN25/0412Z TX34/0416Z BECMG 0416/0418 02010KT SCT025 RMK PHD="
)


def _residual_texts(tac: str) -> list[str]:
    result = decode_tac(tac, product="taf")
    return [r.text.strip() for r in result.residuals]


def test_ca_nxt_fcst_by_not_residual() -> None:
    texts = _residual_texts(_CYAZ)
    assert not any("NXT FCST BY" in t or t.startswith("RMK NXT") for t in texts)
    assert not any(t.startswith("RMK") for t in texts)


def test_ca_auto_obs_trailer_not_residual() -> None:
    texts = _residual_texts(_CYBC_AUTO)
    assert not any("FCST BASED ON AUTO" in t or "NXT FCST BY" in t for t in texts)


def test_national_phd_rmk_not_residual() -> None:
    texts = _residual_texts(_SBAT_PHD)
    assert not any("PHD" in t for t in texts)
