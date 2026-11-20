"""TAF token explainers.

[Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding.decode_format import (
    _fmt_cloud,
    _fmt_qnh,
    _fmt_time,
    _fmt_valid_period,
    _fmt_vis_sm,
    _fmt_wind,
    _fmt_wx,
)
from tac_decoding.decode_patterns import *
from tac_decoding.glossary import resolve_location_name


def _explain_taf(token: str, *, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_taf``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    seen : dict[str, int]
        Argument ``seen``.

    Returns
    -------
    str | None
        Return value.
    """
    upper = token.upper()
    if upper == "TAF" and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        return "Report type (terminal aerodrome forecast)"
    if upper == "COR":
        return "Amendment / correction indicator"
    if upper == "AMD":
        if seen.get("last_amd"):
            return "Amendments"
        return "Amendment / correction indicator"
    if upper == "CNL":
        return "Cancelled forecast"
    if upper == "NIL":
        return "Nil forecast"
    if upper == "=":
        return "Report terminator"
    if upper == "RMK":
        seen["rmk"] = 1
        return "Remarks section"
    if seen.get("rmk"):
        crumb = upper.rstrip(".")
        if crumb in _TAF_RMK_TRAILER_WORD or upper in _TAF_RMK_TRAILER_WORD:
            return "National forecast trailer"
        if _TAF_RMK_NATIONAL.match(upper):
            return "National TAF remark code"
        if _TAF_RMK_NEXT_TIME.match(upper):
            return "Next forecast time"
    if _STATION.match(upper) and seen.get("station", 0) == 0:
        seen["station"] = 1
        place = resolve_location_name(upper)
        if place:
            return f"Station {place} ({upper})"
        return f"Station {upper}"
    if m := _TIME_Z.match(upper):
        return _fmt_time(m, label="Issue time")
    if m := _TAF_VALID.match(upper):
        return _fmt_valid_period(
            day1=int(m.group("d1")),
            hour1=m.group("h1"),
            minute1="00",
            day2=int(m.group("d2")),
            hour2=m.group("h2"),
            minute2="00",
        )
    if m := _WIND.match(upper):
        return _fmt_wind(m, label="Forecast wind")
    if seen.get("au_t") and _AU_TEMP_DIGIT.match(upper):
        return f"Forecast temperature {int(upper)} °C"
    if seen.get("au_t") and upper == "Q":
        seen["au_t"] = 0
        seen["au_q"] = 1
        return "Australian QNH sequence"
    if seen.get("au_q") and _AU_QNH_DIGIT.match(upper):
        return f"Forecast QNH {int(upper)} hPa"
    if seen.get("au_q") and not _AU_QNH_DIGIT.match(upper):
        seen["au_q"] = 0
    if seen.get("metwatch") and (m := _TAF_AFT_HH.match(upper)):
        seen["metwatch"] = 0
        mm = m.group("mm") or "00"
        return f"Metwatch time day {int(m.group('dd'))} {m.group('hh')}:{mm} UTC"
    if seen.get("aft_expect"):
        seen["aft_expect"] = 0
        if m := _TAF_AFT_HH.match(upper):
            mm = m.group("mm") or "00"
            return f"After day {int(m.group('dd'))} {m.group('hh')}:{mm} UTC"
    if seen.get("next_expect") and (m := _TAF_AFT_HH.match(upper)):
        seen["next_expect"] = 0
        seen["last_amd"] = 0
        mm = m.group("mm") or "00"
        return f"Next amendment day {int(m.group('dd'))} {m.group('hh')}:{mm} UTC"
    if seen.get("amd_ltd") and (m := _TAF_AFT_HH.match(upper)):
        seen["amd_ltd"] = 0
        mm = m.group("mm") or "00"
        return f"Limited amendment until day {int(m.group('dd'))} {m.group('hh')}:{mm} UTC"
    if _VIS_M.match(upper):
        return f"Forecast visibility {int(upper)} m"
    if m := _VIS_SM.match(upper):
        return _fmt_vis_sm(m, label="Forecast visibility")
    if m := _VIS_FRAC.match(upper):
        return f"Forecast visibility {m.group('num')}/{m.group('den')} statute miles"
    if m := _CLOUD.match(upper):
        return _fmt_cloud(m, forecast=True)
    if m := _ALT.match(upper):
        return f"Altimeter {int(m.group('val')) / 100:.2f} inHg"
    if m := _QNH.match(upper):
        return _fmt_qnh(m.group("val"))
    if m := _TAF_FM.match(upper):
        return (
            f"From day {int(m.group('dd'))} at {m.group('hh')}:{m.group('mm')} UTC, then the conditions change quickly"
        )
    if upper == "TEMPO":
        return "Temporary fluctuations expected during the following period"
    if upper == "BECMG":
        return "Becoming, a gradual change during the following period"
    if upper == "INTER":
        return "Intermittent changes lasting under 30 minutes during the following period"
    if upper == "CAVOK":
        return "Ceiling and visibility OK"
    if upper == "NSW":
        return "No significant weather"
    if m := _VV.match(upper):
        if m.group("h") == "///":
            return "Vertical visibility not reported"
        return f"Vertical visibility {int(m.group('h')) * 100} ft"
    if m := _TAF_TX_TN.match(upper):
        which = "Maximum" if m.group("which") == "X" else "Minimum"
        sign = "-" if m.group("sign") == "M" else ""
        return (
            f"{which} forecast temperature {sign}{int(m.group('tt'))} °C "
            f"on day {int(m.group('dd'))} at {m.group('hh')}:00 UTC"
        )
    if m := _TAF_QNH_INS.match(upper):
        inches = int(m.group("raw")) / 100
        return f"Lowest forecast altimeter setting {inches:.2f} inHg"
    if m := _TAF_WS.match(upper):
        height = int(m.group("hhh")) * 100
        return (
            f"Non-convective low-level wind shear: wind "
            f"{int(m.group('dir'))}° at {int(m.group('spd'))} kt "
            f"at {height} ft above ground"
        )
    if m := _TAF_TURB.match(upper):
        base = m.group("base")
        thick = m.group("thick")
        base_txt = "base not reported" if base == "///" else f"base {int(base) * 100} ft"
        thick_txt = "thickness not reported" if thick == "/" else f"thickness {int(thick) * 1000} ft"
        return f"Forecast turbulence (intensity {m.group('intensity')}), {base_txt}, {thick_txt}"
    if m := _TAF_ICING.match(upper):
        base = m.group("base")
        thick = m.group("thick")
        base_txt = "base not reported" if base == "///" else f"base {int(base) * 100} ft"
        thick_txt = "thickness not reported" if thick == "/" else f"thickness {int(thick) * 1000} ft"
        return f"Forecast icing (intensity {m.group('intensity')}), {base_txt}, {thick_txt}"
    if m := _TAF_PROB.match(upper):
        return f"{int(m.group('pct'))}% probability of the following conditions"
    if upper.startswith(("FM", "TEMPO", "BECMG", "PROB", "INTER")):
        return "Change / probability group"
    if upper == "TS":
        return "Forecast weather: Thunderstorm"
    if upper == "VCSH":
        return "Forecast weather: Showers in the vicinity"
    if upper == "VCTS":
        return "Forecast weather: Thunderstorm in the vicinity"
    if m := _WX.match(upper):
        return _fmt_wx(m, forecast=True)
    if upper == "NOT":
        return "Not"
    if upper == "SKED":
        return "Scheduled"
    if upper == "TIL":
        return "Until"
    if upper == "AUTOMATED":
        return "Automated"
    if upper == "SENSOR":
        return "Sensor"
    if upper == "METWATCH":
        seen["metwatch"] = 1
        return "Meteorological watch period"
    if seen.get("metwatch") and upper == "FROM":
        return "From"
    if _NAVY_FS_FN.match(upper):
        return f"Navy forecast supplement code ({upper})"
    if upper == "WND":
        return "Wind"
    if upper == "AFT":
        seen["aft_expect"] = 1
        return "After"
    if upper == "LAST":
        seen["last_amd"] = 1
        return "Last"
    if seen.get("last_amd") and upper == "NO":
        return "No"
    if seen.get("last_amd") and upper in {"AMD", "AMDS"}:
        return "Amendments"
    if seen.get("last_amd") and upper == "NEXT":
        seen["next_expect"] = 1
        return "Next"
    if upper == "LTD":
        seen["amd_ltd"] = 1
        return "Limited"
    if seen.get("amd_ltd") and upper == "TO":
        return "To"
    if seen.get("amd_ltd") and upper in {"CLD", "VIS", "AND", "WIND"}:
        return _RMK_WORD.get(upper, upper.title())
    if upper == "T" and not seen.get("au_t") and not seen.get("au_q"):
        seen["au_t"] = 1
        return "Australian temperature sequence"
    return None
