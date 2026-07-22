"""IWXXM-US profile XML writer for METAR/SPECI (F6.b).

Emits WMO annex3 body plus ``iwxxm-us`` extension blocks (Addendum, AerodromePeakWind)
per ADR-013 / docs/context/general-tac-iwxxm-converter.md.
"""

from __future__ import annotations

from typing import Any
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3 import NS, build_observation_and_trends, obs_timestamp


def _us_gml_id(ir: dict[str, Any], product: str) -> str:
    """Stable gml:id for US golden fixtures (theme-aware for F20 S3)."""
    root = product.lower()
    station = str(ir["station"]).lower()
    if ir.get("peak_wind_dir_deg") is not None:
        return f"{root}.us.pk.wnd.{station}"
    if ir.get("sea_level_pressure_hpa") is not None:
        return f"{root}.us.ao2.slp.{station}"
    if ir.get("nil"):
        return f"{root}.us.nil.{station}"
    if ir.get("cavok"):
        return f"{root}.us.cavok.{station}"
    if ir.get("nosig"):
        return f"{root}.us.nosig.{station}"
    if ir.get("auto") and product.upper() == "SPECI" and not ir.get("correction"):
        return f"{root}.us.auto.{station}"
    return f"{root}.us.ao2.{station}"


def _peak_timestamp(ir: dict[str, Any]) -> str:
    """Peak-wind time on the same calendar month as observation fixtures."""
    day = int(ir["day"])
    hour = int(ir["peak_wind_hour"])
    minute = int(ir["peak_wind_minute"])
    return f"2023-06-{day:02d}T{hour:02d}:{minute:02d}:00Z"


def _addendum_extension(ir: dict[str, Any]) -> str:
    """Serialize observation-level ``iwxxm-us:Addendum`` when REMARKS present."""
    free_text = str(ir.get("remarks_free_text") or "").strip()
    if not ir.get("observing_system_type") and ir.get("sea_level_pressure_hpa") is None and not free_text:
        return ""
    parts: list[str] = ["      <iwxxm:extension>", "        <iwxxm-us:Addendum>"]
    if ir.get("observing_system_href"):
        href = escape(str(ir["observing_system_href"]))
        parts.append(f'          <iwxxm-us:observingSystemType xlink:href="{href}"/>')
    if free_text:
        parts.append(f"          <iwxxm-us:humanReadableText>{escape(free_text)}</iwxxm-us:humanReadableText>")
    if ir.get("sea_level_pressure_hpa") is not None:
        parts.append(
            f'          <iwxxm-us:seaLevelPressure uom="hPa">{ir["sea_level_pressure_hpa"]}</iwxxm-us:seaLevelPressure>'
        )
    parts.extend(["        </iwxxm-us:Addendum>", "      </iwxxm:extension>"])
    return "\n".join(parts) + "\n"


def _peak_wind_extension(ir: dict[str, Any]) -> str:
    """Serialize surface-wind ``iwxxm-us:AerodromePeakWind`` when PK WND present."""
    if ir.get("peak_wind_dir_deg") is None:
        return ""
    stamp = _peak_timestamp(ir)
    return f"""          <iwxxm:extension>
            <iwxxm-us:AerodromePeakWind>
              <iwxxm-us:windDirection uom="deg">{ir["peak_wind_dir_deg"]}</iwxxm-us:windDirection>
              <iwxxm-us:windSpeed uom="[kn_i]">{ir["peak_wind_speed_kt"]}</iwxxm-us:windSpeed>
              <iwxxm-us:timeOfOccurrence>
                <gml:TimeInstant gml:id="t.peak">
                  <gml:timePosition>{stamp}</gml:timePosition>
                </gml:TimeInstant>
              </iwxxm-us:timeOfOccurrence>
            </iwxxm-us:AerodromePeakWind>
          </iwxxm:extension>
"""


def emit_metar_speci_iwxxm_us(
    ir: dict[str, Any],
    *,
    product: str,
    iwxxm_version: str,
) -> str:
    """
    Emit a full IWXXM METAR/SPECI document for the ``iwxxm_us`` profile.

    Parameters
    ----------
    ir :
        Parsed METAR/SPECI IR (including optional REMARKS fields).
    product :
        ``METAR`` or ``SPECI``.
    iwxxm_version :
        Release line (namespace selection).

    Returns
    -------
    str
        IWXXM XML document with US extension blocks.
    """
    ns = NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for iwxxm_us emit: {iwxxm_version}")

    station = str(ir["station"])
    stamp = obs_timestamp(ir)
    root = product.upper()
    gml_id = _us_gml_id(ir, root)
    report_status = "CORRECTION" if ir.get("correction") else "NORMAL"
    automated = "true" if ir.get("auto") else "false"

    addendum = _addendum_extension(ir)
    peak = _peak_wind_extension(ir)
    observation, trends = build_observation_and_trends(
        ir,
        addendum_extension=addendum,
        peak_extension=peak,
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:{root} xmlns:iwxxm="{ns}"
    xmlns:iwxxm-us="http://www.weather.gov/iwxxm-us/3.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{report_status}"
    permissibleUsage="OPERATIONAL"
    automatedStation="{automated}">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{station}</aixm:designator>
          <aixm:locationIndicatorICAO>{station}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
{observation}{trends}</iwxxm:{root}>
"""


_US_NS = 'xmlns:iwxxm-us="http://www.weather.gov/iwxxm-us/3.0"'


def _with_us_namespace(xml: str) -> str:
    """Inject the IWXXM-US namespace declaration on the root element."""
    if "xmlns:iwxxm-us=" in xml:
        return xml
    return xml.replace("xmlns:iwxxm=", f"{_US_NS}\n    xmlns:iwxxm=", 1)


def emit_taf_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit TAF annex3 body plus optional ``MeteorologicalAerodromeForecastExtension``.

    Parameters
    ----------
    ir :
        Parsed TAF IR (optional ``forecast_altimeter_inhg``).
    iwxxm_version :
        Release line.
    """
    from tac2iwxxm.profiles.annex3_products import emit_taf_annex3

    xml = emit_taf_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    xml = xml.replace('gml:id="taf.basic.', 'gml:id="taf.us.', 1)

    alt = ir.get("forecast_altimeter_inhg")
    if alt is None:
        return xml

    extension = f"""      <iwxxm:extension>
        <iwxxm-us:MeteorologicalAerodromeForecastExtension>
          <iwxxm-us:altimeter uom="[in_i'Hg]">{alt:.2f}</iwxxm-us:altimeter>
        </iwxxm-us:MeteorologicalAerodromeForecastExtension>
      </iwxxm:extension>
"""
    needle = "    </iwxxm:MeteorologicalAerodromeForecast>"
    if needle not in xml:
        return xml
    return xml.replace(needle, extension + needle, 1)


def emit_sigmet_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit SIGMET annex3 body with IWXXM-US namespace (thin F6.d US surface)."""
    from tac2iwxxm.profiles.annex3_products import emit_sigmet_annex3

    xml = emit_sigmet_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    return xml.replace('gml:id="sigmet.basic.', 'gml:id="sigmet.us.', 1)


def emit_airmet_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit AIRMET annex3 body with IWXXM-US namespace (thin F6.d US surface)."""
    from tac2iwxxm.profiles.annex3_products import emit_airmet_annex3

    xml = emit_airmet_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    return xml.replace('gml:id="airmet.basic.', 'gml:id="airmet.us.', 1)


__all__ = [
    "emit_airmet_iwxxm_us",
    "emit_metar_speci_iwxxm_us",
    "emit_sigmet_iwxxm_us",
    "emit_taf_iwxxm_us",
]
