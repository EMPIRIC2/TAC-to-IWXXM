"""TC-EVDR-002 — staging METAR residual families (legacy decode + pack)."""

from __future__ import annotations

from tac_decoding.decode import decode_tac
from tac_decoding.match import match_tac
from tac_decoding.packs import load_packs


def _codes(tac: str) -> dict[str, str]:
    result = decode_tac(tac, product="METAR")
    return {segment.code: segment.explanation for segment in result.segments}


def _pack_codes(tac: str) -> dict[str, str]:
    packs = {pack.id: pack for pack in load_packs()}
    result = match_tac(tac, packs["metar"])
    return {span.code: span.explanation for span in result.spans}


def test_metar_six_hour_max_min_and_precip() -> None:
    tac = "METAR KJFK 031851Z 18008KT 10SM FEW250 24/18 A3012 RMK AO2 SLP201 T02440178 10244 20222 60001 70015="
    codes = _codes(tac)
    assert "maximum" in codes["10244"].lower()
    assert "24.4" in codes["10244"]
    assert "minimum" in codes["20222"].lower()
    assert "22.2" in codes["20222"]
    assert "0.01" in codes["60001"]
    assert "0.15" in codes["70015"]
    residual = " ".join(r.text for r in decode_tac(tac, product="METAR").residuals)
    for tok in ("10244", "20222", "60001", "70015"):
        assert tok not in residual
    pack = _pack_codes("10244 20222 60001 70015")
    assert all(tok in pack for tok in ("10244", "20222", "60001", "70015"))


def test_metar_sensor_outages_and_ao2a() -> None:
    tac = "METAR KNHK 031855Z AUTO 00000KT 10SM CLR 18/12 A2992 RMK AO2A FZRANO TSNO="
    codes = _codes(tac)
    assert "freezing" in codes["FZRANO"].lower()
    assert "lightning" in codes["TSNO"].lower() or "thunderstorm" in codes["TSNO"].lower()
    assert "augment" in codes["AO2A"].lower() or "observer" in codes["AO2A"].lower()
    residual = " ".join(r.text for r in decode_tac(tac, product="METAR").residuals)
    for tok in ("FZRANO", "TSNO", "AO2A"):
        assert tok not in residual
    pack = _pack_codes("AO2A FZRANO TSNO")
    assert all(tok in pack for tok in ("AO2A", "FZRANO", "TSNO"))


def test_metar_twenty_four_hour_temps_and_t0() -> None:
    tac = "METAR KABC 031200Z 00000KT 10SM CLR 10/M01 A2990 RMK AO2 T0100 401001000="
    codes = _codes(tac)
    assert "24" in codes["401001000"].lower() or "maximum" in codes["401001000"].lower()
    assert "T0100" in codes
    assert "dewpoint" not in codes["T0100"].lower() or "temperature" in codes["T0100"].lower()
    residual = " ".join(r.text for r in decode_tac(tac, product="METAR").residuals)
    assert "401001000" not in residual
    assert "T0100" not in residual
