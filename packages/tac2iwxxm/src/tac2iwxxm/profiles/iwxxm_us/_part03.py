"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


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
    ir : dict[str, Any]
        Parsed METAR/SPECI IR (including optional REMARKS fields).

    product : str
        ``METAR`` or ``SPECI``.

    iwxxm_version : str
        Release line (namespace selection).

    Returns
    -------
    str
        IWXXM XML document with US extension blocks.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_metar_speci_iwxxm_us)
    2
    """
    ns = NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for iwxxm_us emit: {iwxxm_version}")

    station = str(ir["station"])
    stamp = obs_timestamp(ir)
    root = product.upper()
    gml_id = _us_gml_id(ir, root)
    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "CORRECTION" if ir.get("correction") else "NORMAL"
    automated = "true" if ir.get("auto") else "false"

    addendum = _addendum_extension(ir)
    sensors = _inoperative_sensors_extension(ir)
    peak = _peak_wind_extension(ir)
    wshft = _wind_shift_extension(ir)
    var_rvr = _variable_rvr_extension(ir)
    vis_ext = _visibility_us_extension(ir)
    cloud_ext = _cloud_layer_us_extension(ir)
    observation, trends = build_observation_and_trends(
        ir,
        addendum_extension=addendum + sensors,
        peak_extension=peak + wshft,
        rvr_extension=var_rvr,
        visibility_extension=vis_ext,
        cloud_layer_extension=cloud_ext,
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


def _with_us_namespace(xml: str) -> str:
    """
    Internal helper ``_with_us_namespace``.

    Parameters
    ----------
    xml : str
        Argument ``xml``.

    Returns
    -------
    str
        Return value.
    """
    if "xmlns:iwxxm-us=" in xml:
        return xml
    return xml.replace("xmlns:iwxxm=", f"{_US_NS}\n    xmlns:iwxxm=", 1)


def _inject_evolving_extension(xml: str, extension: str, closing_tag: str) -> str:
    """
    Internal helper ``_inject_evolving_extension``.

    Parameters
    ----------
    xml : str
        Argument ``xml``.

    extension : str
        Argument ``extension``.

    closing_tag : str
        Argument ``closing_tag``.

    Returns
    -------
    str
        Return value.
    """
    if not extension or closing_tag not in xml:
        return xml
    return xml.replace(closing_tag, f"{extension}\n            {closing_tag}", 1)


def _airmet_subperiod_extension(parent_ir: dict[str, Any], outlook: dict[str, Any]) -> str:
    """
    Internal helper ``_airmet_subperiod_extension``.

    Parameters
    ----------
    parent_ir : dict[str, Any]
        Argument ``parent_ir``.

    outlook : dict[str, Any]
        Argument ``outlook``.

    Returns
    -------
    str
        Return value.
    """
    from tac2iwxxm.time_anchor import iso_stamp

    from_day = int(outlook.get("valid_from_day", parent_ir["valid_from_day"]))
    to_day = int(outlook.get("valid_to_day", from_day))
    begin = iso_stamp(
        parent_ir,
        from_day,
        int(outlook["valid_from_hour"]),
        int(outlook["valid_from_minute"]),
        legacy="2014-05",
    )
    end = iso_stamp(
        parent_ir,
        to_day,
        int(outlook["valid_to_hour"]),
        int(outlook["valid_to_minute"]),
        legacy="2014-05",
    )
    freezing_levels = ""
    inline_lo = outlook.get("inline_frzlvl_lo")
    inline_hi = outlook.get("inline_frzlvl_hi")
    if inline_lo is not None and inline_hi is not None:
        freezing_levels = _inline_freezing_levels_xml(int(inline_lo), int(inline_hi), prefix="outlook")
    return f"""              <iwxxm:extension>
                <iwxxm-us:AIRMETEvolvingConditionExtension>
                  <iwxxm-us:validTimeSubPeriod>
                    <gml:TimePeriod gml:id="t.subperiod.outlook">
                      <gml:beginPosition>{begin}</gml:beginPosition>
                      <gml:endPosition>{end}</gml:endPosition>
                    </gml:TimePeriod>
                  </iwxxm-us:validTimeSubPeriod>{freezing_levels}
                </iwxxm-us:AIRMETEvolvingConditionExtension>
              </iwxxm:extension>
"""


def _flight_level_layer_xml(alt: str, gml_id: str) -> str:
    """
    Internal helper ``_flight_level_layer_xml``.

    Parameters
    ----------
    alt : str
        Argument ``alt``.

    gml_id : str
        Argument ``gml_id``.

    Returns
    -------
    str
        Return value.
    """
    if alt.upper() == "SFC":
        return f"""                    <aixm:AirspaceLayer gml:id="{gml_id}">
                      <aixm:lowerLimit>GND</aixm:lowerLimit>
                      <aixm:lowerLimitReference>SFC</aixm:lowerLimitReference>
                    </aixm:AirspaceLayer>"""
    fl = int(alt)
    return f"""                    <aixm:AirspaceLayer gml:id="{gml_id}">
                      <aixm:upperLimit uom="FL">{fl}</aixm:upperLimit>
                      <aixm:upperLimitReference>STD</aixm:upperLimitReference>
                    </aixm:AirspaceLayer>"""


def _inline_freezing_levels_xml(lo: int, hi: int, *, prefix: str) -> str:
    """
    Internal helper ``_inline_freezing_levels_xml``.

    Parameters
    ----------
    lo : int
        Argument ``lo``.

    hi : int
        Argument ``hi``.

    prefix : str
        Argument ``prefix``.

    Returns
    -------
    str
        Return value.
    """
    return f"""
                  <iwxxm-us:freezingLevel>
                    <iwxxm-us:flightLevel>
{_flight_level_layer_xml(str(lo), f"fl.{prefix}.lo")}
                    </iwxxm-us:flightLevel>
                    <iwxxm-us:multipleLevels>true</iwxxm-us:multipleLevels>
                  </iwxxm-us:freezingLevel>
                  <iwxxm-us:freezingLevel>
                    <iwxxm-us:flightLevel>
{_flight_level_layer_xml(str(hi), f"fl.{prefix}.hi")}
                    </iwxxm-us:flightLevel>
                    <iwxxm-us:multipleLevels>true</iwxxm-us:multipleLevels>
                  </iwxxm-us:freezingLevel>"""


def _freezing_level_isopleth_xml(isopleth: dict[str, Any], idx: int, *, multiple: bool) -> str:
    """
    Internal helper ``_freezing_level_isopleth_xml``.

    Parameters
    ----------
    isopleth : dict[str, Any]
        Argument ``isopleth``.

    idx : int
        Argument ``idx``.

    multiple : bool
        Argument ``multiple``.

    Returns
    -------
    str
        Return value.
    """
    alt = str(isopleth["alt"])
    return f"""          <iwxxm-us:isopleth>
            <iwxxm-us:FreezingLevel>
              <iwxxm-us:flightLevel>
{_flight_level_layer_xml(alt, f"fl.isopleth.{idx}")}
              </iwxxm-us:flightLevel>
              <iwxxm-us:multipleLevels>{str(multiple).lower()}</iwxxm-us:multipleLevels>
            </iwxxm-us:FreezingLevel>
          </iwxxm-us:isopleth>"""


def _airmet_freezing_level_forecast_extension(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_airmet_freezing_level_forecast_extension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    section_raw = ir.get("frzlvl_section")
    if not isinstance(section_raw, dict):
        return ""
    section = cast(dict[str, Any], section_raw)
    isopleths = section.get("isopleths")
    if not isinstance(isopleths, list) or not isopleths:
        return ""
    from tac2iwxxm.time_anchor import iso_stamp

    begin = iso_stamp(
        ir,
        int(ir["valid_from_day"]),
        int(ir["valid_from_hour"]),
        int(ir["valid_from_minute"]),
        legacy="2014-05",
    )
    end = iso_stamp(
        ir,
        int(ir["valid_to_day"]),
        int(ir["valid_to_hour"]),
        int(ir["valid_to_minute"]),
        legacy="2014-05",
    )
    multiple = bool(section.get("multiple_levels"))
    typed_isopleths: list[dict[str, Any]] = []
    typed_isopleths.extend(cast(dict[str, Any], obj) for obj in cast(list[object], isopleths) if isinstance(obj, dict))
    members = "\n".join(
        _freezing_level_isopleth_xml(item, idx, multiple=multiple) for idx, item in enumerate(typed_isopleths, start=1)
    )
    return f"""  <iwxxm:extension>
    <iwxxm-us:FreezingLevelForecast>
      <iwxxm-us:validTimeSubPeriod>
        <gml:TimePeriod gml:id="t.frzlvl">
          <gml:beginPosition>{begin}</gml:beginPosition>
          <gml:endPosition>{end}</gml:endPosition>
        </gml:TimePeriod>
      </iwxxm-us:validTimeSubPeriod>
{members}
    </iwxxm-us:FreezingLevelForecast>
  </iwxxm:extension>
"""


def _inject_first_evolving_extension(xml: str, inner: str) -> str:
    """
    Internal helper ``_inject_first_evolving_extension``.

    Parameters
    ----------
    xml : str
        Argument ``xml``.

    inner : str
        Argument ``inner``.

    Returns
    -------
    str
        Return value.
    """
    if not inner:
        return xml
    wrapped = f"""              <iwxxm:extension>
                <iwxxm-us:AIRMETEvolvingConditionExtension>{inner}
                </iwxxm-us:AIRMETEvolvingConditionExtension>
              </iwxxm:extension>
"""
    token = "</iwxxm:AIRMETEvolvingCondition>"
    idx = xml.find(token)
    if idx == -1:
        return xml
    return xml[:idx] + wrapped + xml[idx:]


def _airmet_weather_hazards_extension(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_airmet_weather_hazards_extension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    hazard_raw = ir.get("us_airmet_hazard")
    if not isinstance(hazard_raw, dict):
        return ""
    hazard = cast(dict[str, Any], hazard_raw)
    href = hazard.get("href")
    if not isinstance(href, str) or not href.strip():
        return ""
    attrs: list[str] = []
    if hazard.get("causing_ifr_conditions"):
        attrs.append('causingIFRConditions="true"')
    if hazard.get("causing_llws_conditions"):
        attrs.append('causingLLWSConditions="true"')
    attr_txt = f" {' '.join(attrs)}" if attrs else ""
    return f"""          <iwxxm:extension>
            <iwxxm-us:AIRMETWeatherHazards{attr_txt}>
              <iwxxm-us:weatherPhenomenon xlink:href="{escape(href)}"/>
            </iwxxm-us:AIRMETWeatherHazards>
          </iwxxm:extension>
"""


def _sigmet_weather_hazards_extension(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_sigmet_weather_hazards_extension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    hazard_raw = ir.get("us_sigmet_hazard")
    if not isinstance(hazard_raw, dict):
        return ""
    hazard = cast(dict[str, Any], hazard_raw)
    href = hazard.get("href")
    if not isinstance(href, str) or not href.strip():
        return ""
    attrs: list[str] = []
    tag = hazard.get("tag")
    if isinstance(tag, str) and tag.strip():
        attrs.append(f'tag="{escape(tag.strip())}"')
    if hazard.get("is_severe") is True:
        attrs.append('isSevere="true"')
    attr_txt = f" {' '.join(attrs)}" if attrs else ""
    return f"""              <iwxxm:extension>
                <iwxxm-us:SIGMETWeatherHazards{attr_txt}>
                  <iwxxm-us:weatherPhenomenon xlink:href="{escape(href)}"/>
                </iwxxm-us:SIGMETWeatherHazards>
              </iwxxm:extension>
"""


def emit_taf_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit TAF annex3 body plus optional ``MeteorologicalAerodromeForecastExtension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed TAF IR (optional ``forecast_altimeter_inhg``).

    iwxxm_version : str
        Release line.

    Returns
    -------
    str
        TAF annex3 body plus optional ``MeteorologicalAerodromeForecastExtension``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_taf_iwxxm_us)
    2
    """
    from tac2iwxxm.profiles.annex3_emit import emit_taf_annex3

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
