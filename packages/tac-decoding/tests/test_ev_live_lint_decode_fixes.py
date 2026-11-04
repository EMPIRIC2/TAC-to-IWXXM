"""Coverage for live-eval decode fixes (WS R…, RVR FT/trend, CA TAF RMK).

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding import decode_tac


def test_ws_runway_pair_explained() -> None:
    tac = "METAR LEMD 042030Z 35003KT 9999 FEW060 09/03 Q1014 WS R36R NOSIG="
    result = decode_tac(tac, product="metar")
    assert any("wind shear" in (s.explanation or "").lower() for s in result.segments)
    assert not any(r.text.strip() in {"WS", "R36R", "WS R36R"} for r in result.residuals)


def test_rvr_ft_trend_explained() -> None:
    tac = "METAR CYBG 041900Z 10009KT 1/8SM R11/1800FT/N -DZ FG VV002 05/05 A2989 RMK FG8 VIS VRB 0-1/4 SLP129="
    result = decode_tac(tac, product="metar")
    assert not any(t.text.strip().startswith("R11/") for t in result.residuals)
    assert "0-1/4" not in {t.text.strip() for t in result.residuals}


def test_taf_rmk_trailer_known_ignore() -> None:
    tac = "TAF CYAZ 041740Z 0418/0424 12010G20KT P6SM SCT020 RMK NXT FCST BY 04Z="
    result = decode_tac(tac, product="taf")
    assert not any(r.text.strip() for r in result.residuals)
    assert any(s.code == "RMK" for s in result.segments)
    assert any("trailer" in (s.explanation or "").lower() for s in result.segments)


def test_taf_rmk_national_phd_and_six_digit_time() -> None:
    tac = "TAF SBAT 040300Z 0406/0418 07005KT 9999 SCT020 TN25/0412Z TX34/0416Z RMK PHD NXT FCST BY 032000Z="
    result = decode_tac(tac, product="taf")
    assert not any("PHD" in r.text for r in result.residuals)
    assert any("remark code" in (s.explanation or "").lower() for s in result.segments)
    assert any("Next forecast time" in (s.explanation or "") for s in result.segments)


def test_taf_rmk_unknown_trailer_falls_through() -> None:
    """After RMK, unknown crumbs skip the known-ignore arms (branch cover)."""
    tac = "TAF CYUL 031340Z 0314/0414 28008KT P6SM SCT040 RMK ZZQQ="
    result = decode_tac(tac, product="taf")
    assert any("ZZQQ" in r.text for r in result.residuals)


def test_ws_without_runway_does_not_pair() -> None:
    """WS not followed by bare R{nn} falls through to normal classify."""
    tac = "METAR LEMD 042030Z 35003KT 9999 FEW060 09/03 Q1014 WS ALL NOSIG="
    result = decode_tac(tac, product="metar")
    assert not any(s.code == "WS ALL" for s in result.segments)
