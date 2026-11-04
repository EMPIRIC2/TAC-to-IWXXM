"""Decode regressions for TAF non-RMK residual conventions (F9).

[Corpus: product §F9] [Corpus: tests]
"""

from __future__ import annotations

from tac_decoding.decode import _explain_taf, decode_tac


def _codes(tac: str) -> dict[str, str]:
    return {s.code: s.explanation for s in decode_tac(tac, product="TAF").segments}


def _residual(tac: str) -> list[str]:
    return [r.text for r in decode_tac(tac, product="TAF").residuals]


def test_australian_t_q_sequence() -> None:
    tac = "TAF AYPY 031700Z 0318/0418 VRB03KT 9999 SCT040 T 26 27 29 31 Q 1009 1010 1012 1011"
    codes = _codes(tac)
    assert "Australian temperature" in codes["T"]
    assert "26 °C" in codes["26"]
    assert "Australian QNH" in codes["Q"]
    assert "1009 hPa" in codes["1009"]
    assert not any(t.startswith("T ") for t in _residual(tac))


def test_navy_fs_and_metwatch_from() -> None:
    fs = "TAF KNID 030700Z 0307/0407 VRB06KT 9999 FEW250 QNH2993INS AUTOMATED SENSOR METWATCH 0307 TIL 0316 TX22/0321Z TN07/0314Z FS30237"
    codes = _codes(fs)
    assert "Navy" in codes["FS30237"]
    assert "Metwatch time" in codes["0307"]
    assert "FS30237" not in _residual(fs)
    assert "Navy" in (_explain_taf("FN12345", seen={}) or "")

    frm = "TAF KNYL 040000Z 0400/0506 VRB03KT 9999 FEW180 QNH2991INS AUTOMATED SENSOR METWATCH FROM 0406 TIL 0414 TX27/0423Z TN14/0413Z"
    assert _codes(frm)["FROM"] == "From"
    assert "FROM" not in _residual(frm)


def test_wnd_aft_and_last_amds_and_ltd() -> None:
    wnd = "TAF KGRK 040000Z 0400/0506 33012KT 9999 FEW040 QNH2992INS WND 33009KT AFT 0404 TX22/0421Z TN10/0411Z"
    codes = _codes(wnd)
    assert codes["WND"] == "Wind"
    assert "After day" in codes["0404"]
    assert "WND" not in _residual(wnd)
    last = "TAF KBIX 030300Z 0303/0409 07009KT 9999 FEW020 TX26/0320Z TN21/0310Z LAST NO AMDS AFT 0305 NEXT 0311"
    codes = _codes(last)
    assert codes["LAST"] == "Last"
    assert codes["AMDS"] == "Amendments"
    assert "Next amendment" in codes["0311"]
    assert not any("LAST" in t for t in _residual(last))
    ltd = "TAF KSUN 031120Z 0312/0418 VRB03KT P6SM SCT015 AMD LTD TO CLD VIS AND WIND TIL 031300"
    codes = _codes(ltd)
    assert codes["LTD"] == "Limited"
    assert codes["CLD"] == "Cloud"
    assert "Limited amendment until" in codes["031300"]


def test_explain_taf_edge_seen_states() -> None:
    assert _explain_taf("COR", seen={}) == "Amendment / correction indicator"
    seen: dict[str, int] = {"aft_expect": 1}
    assert _explain_taf("XX", seen=seen) is None
    seen = {"last_amd": 1}
    assert _explain_taf("AMD", seen=seen) == "Amendments"
    seen = {"au_q": 1}
    assert _explain_taf("TEMPO", seen=seen) == "Temporary fluctuations expected during the following period"
    assert seen.get("au_q") == 0
    seen = {"metwatch": 1}
    assert "Metwatch time" in (_explain_taf("0316", seen=seen) or "")
    seen = {"amd_ltd": 1}
    assert "Limited amendment until" in (_explain_taf("041200", seen=seen) or "")
    seen = {"next_expect": 1, "last_amd": 1}
    assert "Next amendment" in (_explain_taf("050600", seen=seen) or "")
