"""IWXXM-US profile XML writer for METAR/SPECI (F6.b).

Emits WMO annex3 body plus ``iwxxm-us`` extension blocks (Addendum, AerodromePeakWind,
AerodromeWindShift, AerodromeVariableRVR) per ADR-013 / docs/context/general-tac-iwxxm-converter.md.
"""

from __future__ import annotations

from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3 import NS, build_observation_and_trends, obs_timestamp


def _us_gml_id(ir: dict[str, Any], product: str) -> str:
    """Stable gml:id for US golden fixtures (theme-aware for F20 S3)."""
    root = product.lower()
    station = str(ir["station"]).lower()
    rvr = ir.get("rvr")
    if isinstance(rvr, dict) and rvr.get("variable"):
        return f"{root}.us.var.rvr.{station}"
    if ir.get("observed_lightning"):
        return f"{root}.us.ltg.{station}"
    if ir.get("snow_increase"):
        return f"{root}.us.snincr.{station}"
    if ir.get("inoperative_sensor_hrefs"):
        return f"{root}.us.sensor.{station}"
    if ir.get("peak_wind_dir_deg") is not None:
        return f"{root}.us.pk.wnd.{station}"
    if ir.get("wind_shift_hour") is not None:
        return f"{root}.us.wshft.{station}"
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


def _wind_shift_timestamp(ir: dict[str, Any]) -> str:
    """Wind-shift time on the same calendar month as observation fixtures."""
    day = int(ir["day"])
    hour = int(ir["wind_shift_hour"])
    minute = int(ir["wind_shift_minute"])
    return f"2023-06-{day:02d}T{hour:02d}:{minute:02d}:00Z"


def _fmt_deg(value: float) -> str:
    """Format sector angle for iwxxm-us Sector (PDF uses .5° steps)."""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:g}"


def _observed_lightning_xml(lightning: dict[str, Any]) -> str:
    """Serialize one ``iwxxm-us:ObservedLightning`` block."""
    parts: list[str] = ["              <iwxxm-us:ObservedLightning>"]
    dist = lightning.get("qualitative_distance_href")
    if dist:
        parts.append(f'                <iwxxm-us:qualitativeDistance xlink:href="{escape(str(dist))}"/>')
    freq = lightning.get("frequency_href")
    if freq:
        parts.append(f'                <iwxxm-us:frequency xlink:href="{escape(str(freq))}"/>')
    typ = lightning.get("type_href")
    if typ:
        parts.append(f'                <iwxxm-us:type xlink:href="{escape(str(typ))}"/>')
    sector_raw = lightning.get("sector")
    if isinstance(sector_raw, dict):
        sector: dict[str, Any] = sector_raw
        if sector.get("in_all_quadrants"):
            parts.append("                <iwxxm-us:sector>")
            parts.append('                  <iwxxm-us:Sector inAllQuadrants="true"/>')
            parts.append("                </iwxxm-us:sector>")
        elif "ccw_deg" in sector and "cw_deg" in sector:
            ccw = _fmt_deg(float(str(sector["ccw_deg"])))
            cw = _fmt_deg(float(str(sector["cw_deg"])))
            parts.append("                <iwxxm-us:sector>")
            parts.append("                  <iwxxm-us:Sector>")
            parts.append(
                f'                    <iwxxm-us:extremeCCWDirection uom="deg">{ccw}</iwxxm-us:extremeCCWDirection>'
            )
            parts.append(
                f'                    <iwxxm-us:extremeCWDirection uom="deg">{cw}</iwxxm-us:extremeCWDirection>'
            )
            parts.append("                  </iwxxm-us:Sector>")
            parts.append("                </iwxxm-us:sector>")
    parts.append("              </iwxxm-us:ObservedLightning>")
    return "\n".join(parts)


def _cloud_character_elem(tag: str, href: str | None, nil_reason: str | None) -> str:
    """Serialize one CharacterOfTheSky CloudTypes child (xlink or nilReason)."""
    if href:
        return f'              <iwxxm-us:{tag} xlink:href="{escape(href)}"/>'
    if nil_reason:
        return f'              <iwxxm-us:{tag} nilReason="{escape(nil_reason)}"/>'
    return ""


def _character_of_the_sky_xml(sky: dict[str, Any]) -> str:
    """Serialize ``iwxxm-us:CharacterOfTheSky`` for VOP."""
    low = _cloud_character_elem(
        "lowCloudCharacter",
        sky.get("low_href") if isinstance(sky.get("low_href"), str) else None,
        sky.get("low_nil_reason") if isinstance(sky.get("low_nil_reason"), str) else None,
    )
    mid = _cloud_character_elem(
        "middleCloudCharacter",
        sky.get("middle_href") if isinstance(sky.get("middle_href"), str) else None,
        sky.get("middle_nil_reason") if isinstance(sky.get("middle_nil_reason"), str) else None,
    )
    high = _cloud_character_elem(
        "highCloudCharacter",
        sky.get("high_href") if isinstance(sky.get("high_href"), str) else None,
        sky.get("high_nil_reason") if isinstance(sky.get("high_nil_reason"), str) else None,
    )
    return f"""              <iwxxm-us:CharacterOfTheSky>
{low}
{mid}
{high}
              </iwxxm-us:CharacterOfTheSky>"""


def _convective_cloud_xml(conv: dict[str, Any]) -> str:
    """Serialize one ``iwxxm-us:ConvectiveCloudLocation`` block."""
    parts: list[str] = ["              <iwxxm-us:ConvectiveCloudLocation>"]
    ctype = conv.get("cloud_type_href")
    if ctype:
        parts.append(f'                <iwxxm-us:cloudType xlink:href="{escape(str(ctype))}"/>')
    dist = conv.get("qualitative_distance_href")
    if dist:
        parts.append(f'                <iwxxm-us:qualitativeDistance xlink:href="{escape(str(dist))}"/>')
    sector_raw = conv.get("sector")
    if isinstance(sector_raw, dict):
        sector: dict[str, Any] = sector_raw
        if sector.get("in_all_quadrants"):
            parts.append("                <iwxxm-us:sector>")
            parts.append('                  <iwxxm-us:Sector inAllQuadrants="true"/>')
            parts.append("                </iwxxm-us:sector>")
        elif "ccw_deg" in sector and "cw_deg" in sector:
            ccw = _fmt_deg(float(str(sector["ccw_deg"])))
            cw = _fmt_deg(float(str(sector["cw_deg"])))
            parts.append("                <iwxxm-us:sector>")
            parts.append("                  <iwxxm-us:Sector>")
            parts.append(
                f'                    <iwxxm-us:extremeCCWDirection uom="deg">{ccw}</iwxxm-us:extremeCCWDirection>'
            )
            parts.append(
                f'                    <iwxxm-us:extremeCWDirection uom="deg">{cw}</iwxxm-us:extremeCWDirection>'
            )
            parts.append("                  </iwxxm-us:Sector>")
            parts.append("                </iwxxm-us:sector>")
    motion = conv.get("direction_of_motion_deg")
    if motion is not None:
        motion_txt = _fmt_deg(float(str(motion)))
        parts.append(f'                <iwxxm-us:directionOfMotion uom="deg">{motion_txt}</iwxxm-us:directionOfMotion>')
    parts.append("              </iwxxm-us:ConvectiveCloudLocation>")
    return "\n".join(parts)


def _vop_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``visuallyObservablePhenomena`` (lightning / convection / sky / obscuration)."""
    lightning_raw = ir.get("observed_lightning")
    has_lightning = isinstance(lightning_raw, dict)
    convective_raw = ir.get("convective_cloud")
    has_convective = isinstance(convective_raw, dict)
    sky_raw = ir.get("character_of_the_sky")
    has_sky = isinstance(sky_raw, dict)
    obscuration_raw = ir.get("obscuration")
    has_obscuration = isinstance(obscuration_raw, dict)
    if not has_lightning and not has_convective and not has_sky and not has_obscuration:
        return ""

    inner_parts: list[str] = [
        "          <iwxxm-us:visuallyObservablePhenomena>",
        "            <iwxxm-us:VisuallyObservablePhenomena>",
    ]
    if has_lightning:
        lightning: dict[str, Any] = lightning_raw  # type: ignore[assignment]
        ol = _observed_lightning_xml(lightning)
        inner_parts.append("              <iwxxm-us:lightning>")
        inner_parts.append(ol)
        inner_parts.append("              </iwxxm-us:lightning>")
    if has_convective:
        convective: dict[str, Any] = convective_raw  # type: ignore[assignment]
        conv_xml = _convective_cloud_xml(convective)
        inner_parts.append("              <iwxxm-us:convection>")
        inner_parts.append(conv_xml)
        inner_parts.append("              </iwxxm-us:convection>")
    if has_sky:
        sky: dict[str, Any] = sky_raw  # type: ignore[assignment]
        sky_xml = _character_of_the_sky_xml(sky)
        inner_parts.append("              <iwxxm-us:characterOfTheSky>")
        inner_parts.append(sky_xml)
        inner_parts.append("              </iwxxm-us:characterOfTheSky>")
    if has_obscuration:
        obsc: dict[str, Any] = obscuration_raw  # type: ignore[assignment]
        height = int(str(obsc["height_ft"]))
        amt = escape(str(obsc["amount_href"]))
        wx = escape(str(obsc["weather_href"]))
        inner_parts.append("              <iwxxm-us:obscuration>")
        inner_parts.append("                <iwxxm-us:Obscurations>")
        inner_parts.append(
            f'                  <iwxxm-us:heightOfWeatherPhenomenon uom="[ft_i]">{height}</iwxxm-us:heightOfWeatherPhenomenon>'
        )
        inner_parts.append(f'                  <iwxxm-us:obscurationAmount xlink:href="{amt}"/>')
        inner_parts.append(f'                  <iwxxm-us:weatherCausingObscuration xlink:href="{wx}"/>')
        inner_parts.append("                </iwxxm-us:Obscurations>")
        inner_parts.append("              </iwxxm-us:obscuration>")
    inner_parts.extend(
        [
            "            </iwxxm-us:VisuallyObservablePhenomena>",
            "          </iwxxm-us:visuallyObservablePhenomena>",
        ]
    )
    return "\n".join(inner_parts) + "\n"


def _hailstone_size_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``hailstoneSize`` from FMH-1 GR remark."""
    hail_raw = ir.get("hailstone_size")
    if not isinstance(hail_raw, dict):
        return ""
    hail: dict[str, Any] = hail_raw
    diam = hail.get("maximum_diameter_in")
    if diam is None:
        return ""
    diam_txt = _fmt_deg(float(str(diam)))  # reuse compact float formatting
    op = hail.get("size_operator")
    op_xml = f"\n                <iwxxm-us:sizeOperator>{escape(str(op))}</iwxxm-us:sizeOperator>" if op else ""
    return f"""          <iwxxm-us:hailstoneSize>
            <iwxxm-us:HailstoneSize>
              <iwxxm-us:maximumDiameter uom="[in_i]">{diam_txt}</iwxxm-us:maximumDiameter>{op_xml}
            </iwxxm-us:HailstoneSize>
          </iwxxm-us:hailstoneSize>
"""


def _snow_increase_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``snowIncrease`` from FMH-1 SNINCR."""
    snow_raw = ir.get("snow_increase")
    if not isinstance(snow_raw, dict):
        return ""
    snow: dict[str, Any] = snow_raw
    incr = int(str(snow["increase_in"]))
    depth = int(str(snow["depth_in"]))
    elem = escape(str(snow["processed_weather_element_href"]))
    vtype = escape(str(snow["value_type_href"]))
    period = escape(str(snow.get("value_period") or "PT1H"))
    return f"""          <iwxxm-us:snowIncrease>
            <iwxxm-us:SnowIncrease>
              <iwxxm-us:snowDepthIncrease>
                <iwxxm-us:ProcessedProperty>
                  <iwxxm-us:processedWeatherElement xlink:href="{elem}"/>
                  <iwxxm-us:valueType xlink:href="{vtype}"/>
                  <iwxxm-us:valuePeriod>{period}</iwxxm-us:valuePeriod>
                  <iwxxm-us:processedValue uom="[in_i]">{incr}</iwxxm-us:processedValue>
                </iwxxm-us:ProcessedProperty>
              </iwxxm-us:snowDepthIncrease>
              <iwxxm-us:snowDepth uom="[in_i]">{depth}</iwxxm-us:snowDepth>
            </iwxxm-us:SnowIncrease>
          </iwxxm-us:snowIncrease>
"""


def _inoperative_sensors_extension(ir: dict[str, Any]) -> str:
    """Serialize observation-level ``iwxxm-us:InoperativeSensors`` for sensor-NO remarks."""
    hrefs_raw = ir.get("inoperative_sensor_hrefs")
    if not isinstance(hrefs_raw, list) or not hrefs_raw:
        return ""
    hrefs = [f"{item}" for item in cast(list[object], hrefs_raw)]
    failed_parts: list[str] = [
        "          <iwxxm-us:failedSensors>",
        "            <iwxxm-us:FailedSensors>",
    ]
    for href in hrefs:
        failed_parts.append(f'              <iwxxm-us:parameter xlink:href="{escape(href)}"/>')
    failed_parts.extend(
        [
            "            </iwxxm-us:FailedSensors>",
            "          </iwxxm-us:failedSensors>",
        ]
    )
    body = "\n".join(failed_parts)
    return f"""      <iwxxm:extension>
        <iwxxm-us:InoperativeSensors>
{body}
        </iwxxm-us:InoperativeSensors>
      </iwxxm:extension>
"""


def _second_location_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``observedAtSecondLocation`` from CIG/VIS RWY remarks."""
    second_raw = ir.get("observed_at_second_location")
    if not isinstance(second_raw, dict):
        return ""
    second: dict[str, Any] = second_raw
    attrs = ""
    if second.get("visibility_below_sensor_minimum"):
        attrs = ' visibilityBelowSensorMinimum="true"'
    parts: list[str] = [
        "          <iwxxm-us:observedAtSecondLocation>",
        f"            <iwxxm-us:ObservedAtSecondLocation{attrs}>",
    ]
    if second.get("ceiling_height_ft") is not None:
        parts.append(
            f'              <iwxxm-us:ceilingHeight uom="[ft_i]">{int(str(second["ceiling_height_ft"]))}</iwxxm-us:ceilingHeight>'
        )
    if second.get("visibility_ft") is not None:
        parts.append(
            f'              <iwxxm-us:visibility uom="[ft_i]">{int(str(second["visibility_ft"]))}</iwxxm-us:visibility>'
        )
    desc = second.get("location_description")
    if desc:
        parts.append("              <iwxxm-us:location>")
        parts.append("                <iwxxm-us:SensorLocation>")
        parts.append(f"                  <iwxxm-us:description>{escape(str(desc))}</iwxxm-us:description>")
        parts.append("                </iwxxm-us:SensorLocation>")
        parts.append("              </iwxxm-us:location>")
    parts.extend(
        [
            "            </iwxxm-us:ObservedAtSecondLocation>",
            "          </iwxxm-us:observedAtSecondLocation>",
        ]
    )
    return "\n".join(parts) + "\n"


def _visibility_us_extension(ir: dict[str, Any]) -> str:
    """Serialize SectorVisibility / TowerVisibility / VariableVisibility extensions."""
    chunks: list[str] = []
    sector_raw = ir.get("sector_visibility")
    if isinstance(sector_raw, dict):
        sector: dict[str, Any] = sector_raw
        below = ""
        if sector.get("below_sensor_minimum"):
            below = "\n              <iwxxm-us:belowSensorMinimum>true</iwxxm-us:belowSensorMinimum>"
        chunks.append(
            f"""          <iwxxm:extension>
            <iwxxm-us:SectorVisibility>
              <iwxxm-us:visibility uom="m">{int(str(sector["visibility_m"]))}</iwxxm-us:visibility>
              <iwxxm-us:direction uom="deg">{_fmt_deg(float(str(sector["direction_deg"])))}</iwxxm-us:direction>{below}
            </iwxxm-us:SectorVisibility>
          </iwxxm:extension>"""
        )
    tower_raw = ir.get("tower_visibility")
    if isinstance(tower_raw, dict):
        tower: dict[str, Any] = tower_raw
        less = ""
        if tower.get("less_than"):
            less = "\n              <iwxxm-us:lessThan>true</iwxxm-us:lessThan>"
        chunks.append(
            f"""          <iwxxm:extension>
            <iwxxm-us:TowerVisibility>
              <iwxxm-us:towerVisibility uom="m">{int(str(tower["visibility_m"]))}</iwxxm-us:towerVisibility>{less}
            </iwxxm-us:TowerVisibility>
          </iwxxm:extension>"""
        )
    var_vis_raw = ir.get("variable_visibility")
    if isinstance(var_vis_raw, dict):
        var_vis: dict[str, Any] = var_vis_raw
        attrs = ' belowMinimum="true"' if var_vis.get("below_minimum") else ""
        chunks.append(
            f"""          <iwxxm:extension>
            <iwxxm-us:VariableVisibility{attrs}>
              <iwxxm-us:minimumVisibility uom="m">{int(str(var_vis["minimum_m"]))}</iwxxm-us:minimumVisibility>
              <iwxxm-us:maximumVisibility uom="m">{int(str(var_vis["maximum_m"]))}</iwxxm-us:maximumVisibility>
            </iwxxm-us:VariableVisibility>
          </iwxxm:extension>"""
        )
    if not chunks:
        return ""
    return "\n".join(chunks)


def _cloud_layer_us_extension(ir: dict[str, Any]) -> str:
    """Serialize VariableCeilingHeight / VariableSkyCondition on CloudLayer."""
    chunks: list[str] = []
    cig_raw = ir.get("variable_ceiling")
    if isinstance(cig_raw, dict):
        cig: dict[str, Any] = cig_raw
        chunks.append(
            f"""              <iwxxm:extension>
                <iwxxm-us:VariableCeilingHeight>
                  <iwxxm-us:minimumHeight uom="[ft_i]">{int(str(cig["minimum_ft"]))}</iwxxm-us:minimumHeight>
                  <iwxxm-us:maximumHeight uom="[ft_i]">{int(str(cig["maximum_ft"]))}</iwxxm-us:maximumHeight>
                </iwxxm-us:VariableCeilingHeight>
              </iwxxm:extension>"""
        )
    sky_raw = ir.get("variable_sky")
    if isinstance(sky_raw, dict):
        sky: dict[str, Any] = sky_raw
        first = escape(str(sky["first_amount_href"]))
        second = escape(str(sky["second_amount_href"]))
        chunks.append(
            f"""              <iwxxm:extension>
                <iwxxm-us:VariableSkyCondition>
                  <iwxxm-us:firstSkyCoverValue xlink:href="{first}"/>
                  <iwxxm-us:secondSkyCoverValue xlink:href="{second}"/>
                </iwxxm-us:VariableSkyCondition>
              </iwxxm:extension>"""
        )
    if not chunks:
        return ""
    return "\n".join(chunks)


def _max_min_temperatures_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``maxMinTemperatures`` from FMH-1 ``1``/``2``/``4`` groups."""
    rows_raw = ir.get("max_min_temperatures")
    if not isinstance(rows_raw, list) or not rows_raw:
        return ""
    parts: list[str] = []
    for row_obj in cast(list[object], rows_raw):
        if not isinstance(row_obj, dict):
            continue
        row: dict[str, Any] = row_obj
        period = escape(str(row.get("preceding_period") or "PT6H"))
        max_xml = _measure_or_nil("maxTemperature", row.get("max_c"), uom="Cel")
        min_xml = _measure_or_nil("minTemperature", row.get("min_c"), uom="Cel")
        parts.append(
            f"""          <iwxxm-us:maxMinTemperatures>
            <iwxxm-us:MaxMinTemperatures>
              <iwxxm-us:precedingPeriod>{period}</iwxxm-us:precedingPeriod>
              {max_xml}
              {min_xml}
            </iwxxm-us:MaxMinTemperatures>
          </iwxxm-us:maxMinTemperatures>
"""
        )
    return "".join(parts)


def _measure_or_nil(tag: str, value: object, *, uom: str) -> str:
    """Emit a MeasureWithNilReason element (value or missing nil)."""
    if value is None:
        return f'<iwxxm-us:{tag} uom="N/A" nilReason="missing" xsi:nil="true"/>'
    if isinstance(value, float):
        txt = f"{value:.1f}"
    else:
        txt = _fmt_deg(float(str(value)))
    return f'<iwxxm-us:{tag} uom="{uom}">{txt}</iwxxm-us:{tag}>'


def _processed_quantity_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``processedQuantity`` ProcessedProperty rows (precip P/6/7)."""
    qty_raw = ir.get("processed_quantities")
    if not isinstance(qty_raw, list) or not qty_raw:
        return ""
    parts: list[str] = []
    for row_obj in cast(list[object], qty_raw):
        if not isinstance(row_obj, dict):
            continue
        row: dict[str, Any] = row_obj
        elem = escape(str(row["processed_weather_element_href"]))
        vtype = escape(str(row["value_type_href"]))
        period = escape(str(row.get("value_period") or "PT1H"))
        uom = escape(str(row.get("uom") or "[in_i]"))
        val = row.get("processed_value")
        val_txt = _fmt_deg(float(str(val))) if val is not None else "0"
        qualifier = row.get("qualifier")
        qual_xml = (
            f"\n                  <iwxxm-us:qualifier>{escape(str(qualifier))}</iwxxm-us:qualifier>"
            if qualifier
            else ""
        )
        parts.append(
            f"""          <iwxxm-us:processedQuantity>
            <iwxxm-us:ProcessedProperty>
              <iwxxm-us:processedWeatherElement xlink:href="{elem}"/>
              <iwxxm-us:valueType xlink:href="{vtype}"/>
              <iwxxm-us:valuePeriod>{period}</iwxxm-us:valuePeriod>{qual_xml}
              <iwxxm-us:processedValue uom="{uom}">{val_txt}</iwxxm-us:processedValue>
            </iwxxm-us:ProcessedProperty>
          </iwxxm-us:processedQuantity>
"""
        )
    return "".join(parts)


def _recent_weather_addendum_inner(ir: dict[str, Any]) -> str:
    """Serialize Addendum ``recentWeather`` from FMH-1 begin/end remarks."""
    rows_raw = ir.get("recent_weather_us")
    if not isinstance(rows_raw, list) or not rows_raw:
        return ""
    day = int(ir["day"])
    obs_hour = int(ir["hour"])
    parts: list[str] = ["          <iwxxm-us:recentWeather>"]
    for idx, row_obj in enumerate(cast(list[object], rows_raw)):
        if not isinstance(row_obj, dict):
            continue
        row: dict[str, Any] = row_obj
        href = escape(str(row["phenomenon_href"]))
        b_hour = int(row["begin_hour"]) if row.get("begin_hour") is not None else obs_hour
        e_hour = int(row["end_hour"]) if row.get("end_hour") is not None else obs_hour
        begin_xml = ""
        end_xml = ""
        if row.get("begin_minute") is not None:
            stamp = f"2023-06-{day:02d}T{b_hour:02d}:{int(str(row['begin_minute'])):02d}:00Z"
            begin_xml = f"<gml:beginPosition>{stamp}</gml:beginPosition>"
        else:
            begin_xml = '<gml:beginPosition indeterminatePosition="unknown"/>'
        if row.get("end_minute") is not None:
            stamp = f"2023-06-{day:02d}T{e_hour:02d}:{int(str(row['end_minute'])):02d}:00Z"
            end_xml = f"<gml:endPosition>{stamp}</gml:endPosition>"
        else:
            end_xml = '<gml:endPosition indeterminatePosition="unknown"/>'
        gid = f"t.recent.{idx}"
        parts.append(
            f"""            <iwxxm-us:RecentWeather>
              <iwxxm-us:weatherPhenomenon xlink:href="{href}"/>
              <iwxxm-us:timeOfEvent>
                <gml:TimePeriod gml:id="{gid}">
                  {begin_xml}
                  {end_xml}
                </gml:TimePeriod>
              </iwxxm-us:timeOfEvent>
            </iwxxm-us:RecentWeather>
"""
        )
    parts.append("          </iwxxm-us:recentWeather>")
    return "\n".join(parts) + "\n"


def _addendum_extension(ir: dict[str, Any]) -> str:
    """Serialize observation-level ``iwxxm-us:Addendum`` when REMARKS present."""
    free_text = str(ir.get("remarks_free_text") or "").strip()
    has_vop = (
        isinstance(ir.get("observed_lightning"), dict)
        or isinstance(ir.get("convective_cloud"), dict)
        or isinstance(ir.get("character_of_the_sky"), dict)
        or isinstance(ir.get("obscuration"), dict)
    )
    has_snow = isinstance(ir.get("snow_increase"), dict)
    has_hail = isinstance(ir.get("hailstone_size"), dict)
    has_second = isinstance(ir.get("observed_at_second_location"), dict)
    has_max_min = isinstance(ir.get("max_min_temperatures"), list) and bool(ir.get("max_min_temperatures"))
    has_processed = isinstance(ir.get("processed_quantities"), list) and bool(ir.get("processed_quantities"))
    has_recent = isinstance(ir.get("recent_weather_us"), list) and bool(ir.get("recent_weather_us"))
    has_flags = bool(
        ir.get("pressure_change_href")
        or ir.get("condensation_trail")
        or ir.get("aurora")
        or ir.get("no_specials")
        or ir.get("maintenance_indicator")
    )
    if (
        not ir.get("observing_system_type")
        and ir.get("sea_level_pressure_hpa") is None
        and not free_text
        and not has_vop
        and not has_snow
        and not has_hail
        and not has_second
        and not has_max_min
        and not has_processed
        and not has_recent
        and not has_flags
    ):
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
    if ir.get("pressure_change_href"):
        href = escape(str(ir["pressure_change_href"]))
        parts.append(f'          <iwxxm-us:pressureChangeIndicator xlink:href="{href}"/>')
    snow = _snow_increase_addendum_inner(ir)
    if snow:
        parts.append(snow.rstrip("\n"))
    vop = _vop_addendum_inner(ir)
    if vop:
        parts.append(vop.rstrip("\n"))
    recent = _recent_weather_addendum_inner(ir)
    if recent:
        parts.append(recent.rstrip("\n"))
    processed = _processed_quantity_addendum_inner(ir)
    if processed:
        parts.append(processed.rstrip("\n"))
    max_min = _max_min_temperatures_addendum_inner(ir)
    if max_min:
        parts.append(max_min.rstrip("\n"))
    second = _second_location_addendum_inner(ir)
    if second:
        parts.append(second.rstrip("\n"))
    if ir.get("condensation_trail"):
        parts.append("          <iwxxm-us:condensationTrail>true</iwxxm-us:condensationTrail>")
    if ir.get("aurora"):
        parts.append("          <iwxxm-us:aurora>true</iwxxm-us:aurora>")
    if ir.get("no_specials"):
        parts.append("          <iwxxm-us:noSpecials>true</iwxxm-us:noSpecials>")
    hail = _hailstone_size_addendum_inner(ir)
    if hail:
        parts.append(hail.rstrip("\n"))
    if ir.get("maintenance_indicator"):
        parts.append("          <iwxxm-us:maintenanceIndicator>true</iwxxm-us:maintenanceIndicator>")
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


def _wind_shift_extension(ir: dict[str, Any]) -> str:
    """Serialize surface-wind ``iwxxm-us:AerodromeWindShift`` when WSHFT present."""
    if ir.get("wind_shift_hour") is None:
        return ""
    stamp = _wind_shift_timestamp(ir)
    attrs = ' frontalPassage="true"' if ir.get("wind_shift_frontal_passage") else ""
    return f"""          <iwxxm:extension>
            <iwxxm-us:AerodromeWindShift{attrs}>
              <iwxxm-us:timeOfWindShift>
                <gml:TimeInstant gml:id="t.wshft">
                  <gml:timePosition>{stamp}</gml:timePosition>
                </gml:TimeInstant>
              </iwxxm-us:timeOfWindShift>
            </iwxxm-us:AerodromeWindShift>
          </iwxxm:extension>
"""


def _variable_rvr_extension(ir: dict[str, Any]) -> str:
    """Serialize RVR ``iwxxm-us:AerodromeVariableRVR`` when variable min/max present."""
    rvr = ir.get("rvr")
    if not isinstance(rvr, dict) or not rvr.get("variable"):
        return ""
    attrs: list[str] = []
    if rvr.get("below_sensor_minimum"):
        attrs.append('belowSensorMinimum="true"')
    if rvr.get("above_sensor_maximum"):
        attrs.append('aboveSensorMaximum="true"')
    attr_s = (" " + " ".join(attrs)) if attrs else ""
    return f"""          <iwxxm:extension>
            <iwxxm-us:AerodromeVariableRVR{attr_s}>
              <iwxxm-us:minimumRVR uom="m">{rvr["min_m"]}</iwxxm-us:minimumRVR>
              <iwxxm-us:maximumRVR uom="m">{rvr["max_m"]}</iwxxm-us:maximumRVR>
            </iwxxm-us:AerodromeVariableRVR>
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


_US_NS = 'xmlns:iwxxm-us="http://www.weather.gov/iwxxm-us/3.0"'


def _with_us_namespace(xml: str) -> str:
    """Inject the IWXXM-US namespace declaration on the root element."""
    if "xmlns:iwxxm-us=" in xml:
        return xml
    return xml.replace("xmlns:iwxxm=", f"{_US_NS}\n    xmlns:iwxxm=", 1)


def _inject_evolving_extension(xml: str, extension: str, closing_tag: str) -> str:
    """Insert an ``iwxxm:extension`` block before the evolving-condition close tag."""
    if not extension or closing_tag not in xml:
        return xml
    return xml.replace(closing_tag, f"{extension}\n            {closing_tag}", 1)


def _airmet_weather_hazards_extension(ir: dict[str, Any]) -> str:
    """Serialize ``iwxxm-us:AIRMETWeatherHazards`` when IR carries US hazard metadata."""
    hazard = ir.get("us_airmet_hazard")
    if not isinstance(hazard, dict):
        return ""
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
    """Serialize ``iwxxm-us:SIGMETWeatherHazards`` when IR carries US hazard metadata."""
    hazard = ir.get("us_sigmet_hazard")
    if not isinstance(hazard, dict):
        return ""
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
    """Emit SIGMET annex3 body with IWXXM-US namespace and weather-hazard extensions."""
    from tac2iwxxm.profiles.annex3_products import emit_sigmet_annex3

    xml = emit_sigmet_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    for prefix in ("basic", "conv", "va", "tc", "cnl"):
        xml = xml.replace(f'gml:id="sigmet.{prefix}.', 'gml:id="sigmet.us.', 1)
    ext = _sigmet_weather_hazards_extension(ir)
    return _inject_evolving_extension(xml, ext, "</iwxxm:SIGMETEvolvingCondition>")


def emit_airmet_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit AIRMET annex3 body with IWXXM-US namespace and weather-hazard extensions."""
    from tac2iwxxm.profiles.annex3_products import emit_airmet_annex3

    xml = emit_airmet_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    xml = xml.replace('gml:id="airmet.basic.', 'gml:id="airmet.us.', 1)
    ext = _airmet_weather_hazards_extension(ir)
    return _inject_evolving_extension(xml, ext, "</iwxxm:AIRMETEvolvingCondition>")


__all__ = [
    "emit_airmet_iwxxm_us",
    "emit_metar_speci_iwxxm_us",
    "emit_sigmet_iwxxm_us",
    "emit_taf_iwxxm_us",
]
