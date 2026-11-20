"""METAR/SPECI token explainers.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_format import (
    _explain_recent_weather,
    _fmt_cloud,
    _fmt_qnh,
    _fmt_time,
    _fmt_vis_sm,
    _fmt_wind,
    _fmt_wx,
    _signed_temp,
)
from tac_decoding.decode_patterns import *
from tac_decoding.decode_tokens import (
    _canadian_clouds,
    _pressure_tendency,
    _qfe,
    _runway_state,
    _rvr_bound,
    _tenths_c,
    _us_precip_addenda,
    _varying_rvr,
    _wx_began_or_ended,
)
from tac_decoding.glossary import resolve_location_name
from tac_decoding.remark_plain import explain_remark_plain


def _explain_metar_speci(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_metar_speci``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    product : str
        Argument ``product``.

    seen : dict[str, int]
        Argument ``seen``.

    Returns
    -------
    str | None
        Return value.
    """
    upper = token.upper()
    if seen.get("density_alt"):
        seen["density_alt"] = 0
        if m := _DENSITY_FT.match(upper):
            return f"Density altitude {m.group('n')} ft"
    if seen.get("wind_aloft"):
        seen["wind_aloft"] = 0
        if m := _WIND_ALOFT_FT.match(upper):
            return f"Wind at {int(m.group('ft'))} ft"
        if upper == "SKEID":
            seen["sensor_wind"] = 1
            return "Wind sensor (Skeid)"
    if seen.get("sensor_wind"):
        if m := _WIND.match(upper):
            seen["sensor_wind"] = 0
            return _fmt_wind(m, label="Sensor wind")
        if m := _WIND_VAR.match(upper):
            return f"Sensor wind direction varying from {int(m.group('a'))}° to {int(m.group('b'))}°"
        seen["sensor_wind"] = 0
    if seen.get("cig"):
        seen["cig"] = 0
        if m := _WIND_VAR.match(upper):
            return f"Ceiling varying from {int(m.group('a')) * 100} ft to {int(m.group('b')) * 100} ft"
        if m := _CIG_HUNDREDS.match(upper):
            seen["cig_rwy"] = 1
            return f"Ceiling {int(m.group('h')) * 100} ft"
    if seen.get("cig_rwy"):
        if m := _RWY_DESIGNATOR.match(upper):
            seen["cig_rwy"] = 0
            return f"Runway {m.group('rw')}"
        seen["cig_rwy"] = 0
    if seen.get("vis_expect"):
        seen["vis_expect"] = 0
        if m := _VIS_VARIABLE.match(upper):
            return f"Visibility varying from {m.group('lo')} to {m.group('hi')} statute miles"
        if m := _VIS_VRB_RANGE.match(upper):
            return f"Visibility varying from {m.group('a')} to {m.group('b')} statute miles"
        if upper.isdigit() and len(upper) <= 2:
            return f"Visibility {int(upper)} statute miles"
        if m := _VIS_SM.match(upper):
            return _fmt_vis_sm(m, label="Visibility")
        if upper in {"HYR", "LWR"}:
            seen["vis_dir"] = 1
            return _RMK_WORD[upper]
    if seen.get("vis_dir") and upper in _SIG_DIR:
        seen["vis_dir"] = 0
        return _SIG_DIR_NAME[upper]
    if seen.get("sog_expect"):
        seen["sog_expect"] = 0
        if m := _SOG_VALUE.match(upper):
            return f"Snow on ground {int(m.group('cm'))} cm"
    if seen.get("wshft_expect"):
        seen["wshft_expect"] = 0
        if m := _WSHFT_MIN.match(upper):
            return f"Wind shift at minute {m.group('mm')}"
    if seen.get("movd_expect"):
        seen["movd_expect"] = 0
        if upper in _SIG_DIR:
            return f"Moved {_SIG_DIR_NAME[upper]}"
    if upper in {"METAR", "SPECI"} and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        label = "routine" if upper == "METAR" else "special"
        return f"Report type ({label} meteorological aerodrome report)"
    if upper == "COR":
        return "Correction indicator"
    if upper == "RTD":
        return "Delayed routine report"
    if _BBB_CORRECTION.match(upper):
        return f"Correction ({upper})"
    if _BBB_DELAYED.match(upper):
        return f"Delayed report ({upper})"
    if _BBB_AMENDMENT.match(upper):
        return f"Amendment ({upper})"
    if upper == "NIL":
        return "Nil report (no observation)"
    if upper == "CAVOK":
        return "Ceiling and visibility OK"
    if upper == "NOSIG":
        seen["in_trend"] = 1
        return "No significant change expected"
    if upper == "TEMPO":
        seen["in_trend"] = 1
        return "Temporary fluctuations expected during the following period"
    if upper == "BECMG":
        seen["in_trend"] = 1
        return "Becoming, a gradual change during the following period"
    if upper == "NSW":
        return "No significant weather"
    if upper == "RMK":
        seen["rmk"] = 1
        return "Remarks section"
    if upper in {"AO1", "A01"}:
        return "Automated station without precipitation discriminator"
    if upper in {"AO2", "A02"}:
        return "Automated station with precipitation discriminator"
    if upper == "AO2A":
        return "Automated station with precipitation discriminator, augmented by an observer"
    if m := _SEA_STATE.match(upper):
        wave = m.group("wave")
        wave_txt = "not reported" if "/" in wave else str(int(wave))
        return f"Sea state: waves {wave_txt}, swell {int(m.group('swell'))}"
    if m := _MISSING_TEMP_DEW.match(upper):
        return f"Temperature {int(m.group('body'))} °C, dewpoint not reported"
    if m := _TEMP_MISSING_DEW.match(upper):
        return f"Temperature {_signed_temp(m.group('body'))} °C, dewpoint not reported"
    if _MISSING_WIND_KT.match(upper):
        return "Wind not reported"
    if _MISSING_QNH_SLASH.match(upper):
        return "Altimeter setting not reported"
    if upper == "FZRANO":
        return "Freezing-rain sensor not working"
    if upper == "TSNO":
        return "Lightning detector not working"
    if upper == "RVRNO":
        return "Runway visual range should be reported but is not available"
    if upper.startswith("SLP") and len(upper) == 6 and upper[3:].isdigit():
        return "Sea-level pressure (FMH-1 SLP code)"
    if upper == "=" or token == "=":
        return "Report terminator"
    if _STATION.match(upper) and seen.get("station", 0) == 0 and seen.get("rtype", 0):
        seen["station"] = 1
        place = resolve_location_name(upper)
        if place:
            return f"Station {place} ({upper})"
        return f"Station {upper}"
    if m := _TIME_Z.match(upper):
        return _fmt_time(m, label="Observation time")
    if m := _WIND.match(upper):
        return _fmt_wind(m, label="Surface wind")
    if m := _VIS_SM.match(upper):
        label = "Trend visibility" if seen.get("in_trend") else "Prevailing visibility"
        return _fmt_vis_sm(m, label=label)
    if m := _VIS_MIN.match(upper):
        compass = _SIG_DIR_NAME[m.group("dir")]
        return f"Minimum visibility {int(m.group('vis'))} m toward {compass} ({m.group('dir')})"
    if _VIS_M.match(upper):
        label = "Trend visibility" if seen.get("in_trend") else "Prevailing visibility"
        return f"{label} {int(upper)} m"
    if m := _TREND_TIME.match(upper):
        kind = m.group("kind")
        return f"Trend {_TREND_TIME_LABEL[kind]} {m.group('hh')}:{m.group('mm')} UTC"
    if m := _CLOUD.match(upper):
        return _fmt_cloud(m, forecast=bool(seen.get("in_trend")))
    if m := _TEMP.match(upper):
        return f"Temperature {_signed_temp(m.group('t'))} °C, dewpoint {_signed_temp(m.group('td'))} °C"
    if m := _ALT.match(upper):
        return f"Altimeter {int(m.group('val')) / 100:.2f} inHg"
    if m := _QNH.match(upper):
        return _fmt_qnh(m.group("val"))
    if m := _WX.match(upper):
        return _fmt_wx(m, forecast=bool(seen.get("in_trend")))
    if m := _RVR.match(upper):
        trend = m.group("trend") or m.group("trend2")
        trend_txt = {
            "U": ", upward trend",
            "D": ", downward trend",
            "N": ", no distinct trend",
        }.get(trend or "", "")
        unit = "ft" if m.group("unit") == "FT" else "m"
        return f"Runway visual range runway {m.group('rw')}: {_rvr_bound(m.group('vis'))} {unit}{trend_txt}"
    if phrase := _varying_rvr(upper):
        return phrase
    if phrase := _runway_state(upper):
        return phrase
    if phrase := _qfe(upper):
        return phrase
    if m := _VV.match(upper):
        if m.group("h") == "///":
            return "Vertical visibility not reported"
        return f"Vertical visibility {int(m.group('h')) * 100} ft"
    if m := _MISSING_CLOUD.match(upper):
        kind = _CA_CLOUD_NAME.get(m.group("ctype") or "")
        if kind:
            return f"Cloud amount not reported, {kind}"
        return "Cloud amount not reported"
    if phrase := _wx_began_or_ended(upper):
        return phrase
    if upper.startswith("PK") or upper == "WND":
        return "Peak wind remarks token"
    if upper == "AUTO":
        return "Automated report"
    if upper == "$":
        return "Station needs maintenance"
    if upper == "WSHFT":
        seen["wshft_expect"] = 1
        return "Wind shift"
    if upper in {"//", "///"}:
        return "Missing data"
    if upper == "TS":
        return "Thunderstorm"
    if upper == "VCSH":
        return "Showers in the vicinity"
    if upper == "VCTS":
        return "Thunderstorm in the vicinity"
    if upper.startswith("RE") and len(upper) > 2 and not seen.get("rmk"):
        recent = _explain_recent_weather(upper[2:])
        if recent is not None:
            return recent
    if m := _WIND_VAR.match(upper):
        return f"Wind direction varying from {int(m.group('a'))}° to {int(m.group('b'))}°"
    if m := _VIS_FRAC.match(upper):
        return f"Prevailing visibility {m.group('num')}/{m.group('den')} statute mile"
    if m := _T_GROUP.match(upper):
        return f"Temperature {_tenths_c(m.group('t'))} °C, dewpoint {_tenths_c(m.group('td'))} °C in tenths"
    if m := _T_TEMP_ONLY.match(upper):
        return f"Temperature {_tenths_c(m.group('body'))} °C (dewpoint not reported)"
    # US AO sensor variants are handled above; precip addenda also clear without RMK.
    if phrase := _us_precip_addenda(upper):
        return phrase
    if seen.get("rmk"):
        remark = _explain_metar_remark(upper, seen)
        if remark:
            return remark
    _ = product
    return None


def _explain_metar_remark(upper: str, seen: dict[str, int]) -> str | None:
    """Groups that show up in the remarks, after ``RMK``.

    Parameters
    ----------
    upper : str
        One remarks group, already uppercased.
    seen : dict[str, int]
        Tokens already accepted while decoding this report.

    Returns
    -------
    str | None
        The remark in plain language, or None when the group stays unexplained.
    """
    if upper == "SLPNO":
        return "Sea-level pressure not available"
    if upper == "PNO":
        return "Precipitation amount not available"
    if m := _SIX_HOUR_MAX.match(upper):
        return f"6-hour maximum temperature {_tenths_c(m.group('body'))} °C"
    if m := _SIX_HOUR_MIN.match(upper):
        return f"6-hour minimum temperature {_tenths_c(m.group('body'))} °C"
    if m := _DAY_MAX_MIN.match(upper):
        return f"24-hour maximum {_tenths_c(m.group('max'))} °C, minimum {_tenths_c(m.group('min'))} °C"
    if m := _PRECIP_3_6H.match(upper):
        amt = m.group("amt")
        if amt == "////":
            return "3- or 6-hour precipitation not determinable"
        hundredths = int(amt)
        if hundredths == 0:
            return "3- or 6-hour precipitation: trace"
        return f"3- or 6-hour precipitation {hundredths / 100:.2f} inches"
    if m := _PRECIP_24H.match(upper):
        amt = m.group("amt")
        if amt == "////":
            return "24-hour precipitation not determinable"
        hundredths = int(amt)
        if hundredths == 0:
            return "24-hour precipitation: trace"
        return f"24-hour precipitation {hundredths / 100:.2f} inches"
    if phrase := _pressure_tendency(upper):
        return phrase
    # Hourly/short/PP precip addenda clear in _explain_metar_speci (with or without RMK).
    if phrase := _canadian_clouds(upper):
        return phrase
    if m := _MM_AMOUNT.match(upper):
        return f"Precipitation {m.group('n')} mm"
    if upper == "CIG":
        seen["cig"] = 1
        return "Ceiling"
    if upper == "DENSITY":
        seen["density"] = 1
        return "Density"
    if upper == "ALT" and seen.get("density"):
        seen["density"] = 0
        seen["density_alt"] = 1
        return "Altitude"
    if upper == "WIND":
        seen["wind_aloft"] = 1
        return "Wind"
    if upper == "VIS":
        seen["vis_expect"] = 1
        return "Visibility"
    if upper == "SOG":
        seen["sog_expect"] = 1
        return "Snow on ground"
    if upper == "WSHFT":
        seen["wshft_expect"] = 1
        return "Wind shift"
    if upper == "MOVD":
        seen["movd_expect"] = 1
        return "Moved"
    if upper == "SFC":
        seen["vis_expect"] = 1
        return "Surface"
    if upper == "TWR":
        seen["vis_expect"] = 1
        return "Tower"
    if m := _WIND_ALOFT_FT.match(upper):
        return f"Wind at {int(m.group('ft'))} ft"
    if m := _ICE_ACCRETION.match(upper):
        hundredths = int(m.group("amt"))
        if hundredths == 0:
            return "Ice accretion: trace"
        return f"Ice accretion {hundredths / 100:.2f} inches"
    if m := _TX_DECIMAL.match(upper):
        return f"Maximum temperature {m.group('val')} °C"
    if m := _CLOUD_TYPE_8.match(upper):
        return f"Cloud-type group (low/mid/high): {m.group('body')}"
    if _MISSING_PRESS_TEND.match(upper):
        return "3-hour pressure tendency not reported"
    if m := _MX_PRESS_9.match(upper):
        return f"Pressure-change remark {upper} (unverified national code)"
    if m := _RWY_DESIGNATOR.match(upper):
        return f"Runway {m.group('rw')}"
    if m := _LTG_TYPES.match(upper):
        return f"Lightning ({m.group('types')})"
    if m := _CB_LOC.match(upper):
        return f"{m.group('head')} toward {m.group('dir').replace('-', ' ').replace('/', ' ')}"
    if _OHD_CHAIN.match(upper):
        return f"Direction chain ({upper.replace('-', ' → ')})"
    if upper == "LAST":
        seen["last_stfd"] = 1
        return "Last"
    if m := _LAST_STFD.match(upper):
        rest = (m.group("rest") or "").strip()
        if rest:
            return f"Last staffed observation; next at {rest}"
        return "Last staffed observation / next time"
    if seen.get("last_stfd") and upper in {"STFD", "OBS", "NXT", "NEXT"}:
        return _RMK_WORD.get(upper, upper.title())
    if seen.get("last_stfd") and (
        _TIME_Z.match(upper) or re.fullmatch(r"\d{6}(?:UTC)?", upper) or re.fullmatch(r"\d{2}", upper)
    ):
        seen["last_stfd"] = 0
        return f"Next staffed observation time ({upper})"
    if m := _PEAK_WIND.match(upper):
        return f"Peak wind {int(m.group('dir'))}° at {int(m.group('spd'))} kt at {m.group('hh')}:{m.group('mm')} UTC"
    if m := _PAST_HOUR.match(upper):
        unit = "hour" if m.group("n") == "1" else "hours"
        return f"In the past {m.group('n')} {unit}"
    if m := _FRAC_MILE.match(upper):
        return f"Visibility {m.group('num')}/{m.group('den')} statute mile"
    if m := _VIS_VARIABLE.match(upper):
        return f"Visibility varying from {m.group('lo')} to {m.group('hi')} statute miles"
    if seen.get("vis_expect") and (m := _VIS_VRB_RANGE.match(upper)):
        seen["vis_expect"] = 0
        return f"Visibility varying from {m.group('a')} to {m.group('b')} statute miles"
    if upper in _RMK_WORD:
        if upper == "VRB":
            seen["vis_expect"] = 1
        return _RMK_WORD[upper]
    if upper in _SIG_DIR:
        return _SIG_DIR_NAME[upper]
    sector = re.fullmatch(rf"({_BEARING})-({_BEARING})", upper)
    if sector:
        return f"From {_SIG_DIR_NAME[sector.group(1)]} to {_SIG_DIR_NAME[sector.group(2)]}"
    if phrase := explain_remark_plain(upper):
        return phrase
    return None
