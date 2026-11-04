"""Decode WS R…, RVR …FT/trend, and VIS VRB fractional ranges (live 30d).

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding import decode_tac

_LEMD_WS = "METAR LEMD 042030Z 35003KT 330V040 9999 FEW060 09/03 Q1014 WS R36R NOSIG="
_CYBG_RVR = (
    "METAR CYBG 041900Z 10009KT 1/8SM R11/1800FT/N -DZ FG VV002 05/05 A2989 "
    "RMK FG8 DENSITY ALT -396FT VIS VRB 0-1/4 SLP129="
)
_CYBG_P6000 = (
    "METAR CYBG 042000Z 09010KT 5/8SM R11/P6000FT/U -DZ BR OVC002 05/05 A2989 "
    "RMK FG6ST2 DENSITY ALT -382FT VIS VRB 3/8-1 SLP128="
)


def _residual_texts(tac: str, *, product: str = "metar") -> list[str]:
    return [r.text.strip() for r in decode_tac(tac, product=product).residuals]


def test_ws_r36r_not_residual() -> None:
    texts = _residual_texts(_LEMD_WS)
    joined = " ".join(texts)
    assert "WS R36R" not in joined
    assert "WS" not in texts
    assert "R36R" not in texts
    result = decode_tac(_LEMD_WS, product="metar")
    assert any("wind shear" in (s.explanation or "").lower() for s in result.segments)


def test_rvr_ft_trend_not_residual() -> None:
    texts = _residual_texts(_CYBG_RVR)
    assert not any(t.startswith("R11/") for t in texts)


def test_rvr_p6000ft_u_not_residual() -> None:
    texts = _residual_texts(_CYBG_P6000)
    assert not any("P6000FT" in t for t in texts)


def test_vis_vrb_range_not_naked_residual() -> None:
    texts = _residual_texts(_CYBG_RVR)
    assert "0-1/4" not in texts
    assert not any(t == "0-1/4" or t.endswith("0-1/4") for t in texts)
