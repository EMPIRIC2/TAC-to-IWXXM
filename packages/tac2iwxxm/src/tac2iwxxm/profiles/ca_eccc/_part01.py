"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _ca_gml_id(ir: dict[str, Any], product: str) -> str:
    """
    Internal helper ``_ca_gml_id``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    product : str
        Argument ``product``.

    Returns
    -------
    str
        Return value.
    """
    ca_root = str(ir.get("ca_iwxxm_root") or product).lower()
    station = str(ir["station"]).lower()
    if ca_root == "lwis":
        return f"lwis.ca.{station}"
    if ca_root == "sawr":
        return f"sawr.ca.{station}"
    root = product.lower()
    if ir.get("auto"):
        return f"{root}.ca.auto.{station}"
    if ir.get("visibility_sm") is not None:
        return f"{root}.ca.vis.sm.{station}"
    if ir.get("altimeter_inhg") is not None:
        return f"{root}.ca.alt.a.{station}"
    if ir.get("pressure_change_href"):
        return f"{root}.ca.pres.{station}"
    return f"{root}.ca.basic.{station}"


def _prepare_ca_ir(ir: dict[str, Any]) -> dict[str, Any]:
    """
    Internal helper ``_prepare_ca_ir``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    out = dict(ir)
    if out.get("cavok") or out.get("visibility_not_observable"):
        return out
    vis_sm = out.get("visibility_sm")
    if vis_sm is not None:
        out["visibility_display_uom"] = "[mi_i]"
        out["visibility_display_value"] = vis_sm
    return out


def _ca_pressure_change_href(ir: dict[str, Any]) -> str | None:
    """
    Internal helper ``_ca_pressure_change_href``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str | None
        Return value.
    """
    href = ir.get("pressure_change_href")
    if not isinstance(href, str):
        return None
    if "FALLING" in href or "PRESFR" in href:
        return CA_PRES_FALLING
    if "RISING" in href or "PRESRR" in href:
        return CA_PRES_RISING
    return None


def _ca_observing_system_href(ir: dict[str, Any]) -> str | None:
    """
    Internal helper ``_ca_observing_system_href``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str | None
        Return value.
    """
    explicit = ir.get("ca_observing_system_href")
    if isinstance(explicit, str) and explicit:
        return explicit
    ca_root = str(ir.get("ca_iwxxm_root") or "").upper()
    if ca_root == "LWIS":
        return CA_OBS_LWIS
    if ca_root == "SAWR":
        return CA_OBS_SAWR
    if ir.get("auto"):
        return CA_OBS_AWOS
    return None


def _ca_iwxxm_root_tag(ir: dict[str, Any], product: str) -> tuple[str, str]:
    """
    Internal helper ``_ca_iwxxm_root_tag``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    product : str
        Argument ``product``.

    Returns
    -------
    tuple[str, str]
        Return value.
    """
    ca_root = str(ir.get("ca_iwxxm_root") or product).upper()
    if ca_root in {"LWIS", "SAWR"}:
        return "iwxxm-ca", ca_root
    return "iwxxm", product.upper()


def _density_altitude_xml(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_density_altitude_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    if ir.get("density_altitude_missing"):
        return '          <iwxxm-ca:densityAltitude uom="[ft_i]" xsi:nil="true" nilReason="missing"/>\n'
    ft = ir.get("density_altitude_ft")
    if ft is None:
        return ""
    return f'          <iwxxm-ca:densityAltitude uom="[ft_i]">{int(ft)}</iwxxm-ca:densityAltitude>\n'


def _icing_addendum_xml(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_icing_addendum_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    href = ir.get("ca_icing_href")
    if not isinstance(href, str) or not href:
        return ""
    return f'          <iwxxm-ca:icing xlink:href="{escape(href)}"/>\n'


def _processed_quantity_addendum_inner(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_processed_quantity_addendum_inner``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    qty_raw = ir.get("processed_quantities")
    if not isinstance(qty_raw, list) or not qty_raw:
        return ""
    parts: list[str] = []
    for row_obj in cast(list[object], qty_raw):
        if not isinstance(row_obj, dict):
            continue
        row = cast(dict[str, Any], row_obj)
        elem = escape(str(row["processed_weather_element_href"]))
        vtype = escape(str(row["value_type_href"]))
        period = escape(str(row.get("value_period") or "PT1H"))
        uom = escape(str(row.get("uom") or "[in_i]"))
        val = row.get("processed_value")
        val_txt = f"{float(str(val)):.2f}" if val is not None else "0"
        parts.append(
            f"""          <iwxxm-ca:processedQuantity>
            <iwxxm-ca:ProcessedProperty>
              <iwxxm-ca:processedWeatherElement xlink:href="{elem}"/>
              <iwxxm-ca:valueType xlink:href="{vtype}"/>
              <iwxxm-ca:valuePeriod>{period}</iwxxm-ca:valuePeriod>
              <iwxxm-ca:processedValue uom="{uom}">{val_txt}</iwxxm-ca:processedValue>
            </iwxxm-ca:ProcessedProperty>
          </iwxxm-ca:processedQuantity>
"""
        )
    return "".join(parts)


def _addendum_extension(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_addendum_extension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    free_text = str(ir.get("remarks_free_text") or "").strip()
    obs_href = _ca_observing_system_href(ir)
    pres_href = _ca_pressure_change_href(ir)
    has_slp = ir.get("sea_level_pressure_hpa") is not None
    density_xml = _density_altitude_xml(ir).rstrip("\n")
    icing_xml = _icing_addendum_xml(ir).rstrip("\n")
    processed_xml = _processed_quantity_addendum_inner(ir).rstrip("\n")
    if not any([obs_href, pres_href, has_slp, free_text, density_xml, icing_xml, processed_xml]):
        return ""

    parts: list[str] = [
        "      <iwxxm:extension>",
        "        <iwxxm-ca:Addendum>",
    ]
    if obs_href:
        parts.append(f'          <iwxxm-ca:observingSystemType xlink:href="{escape(obs_href)}"/>')
    if free_text:
        parts.append(f"          <iwxxm-ca:humanReadableText>{escape(free_text)}</iwxxm-ca:humanReadableText>")
    if has_slp:
        parts.append(
            f'          <iwxxm-ca:seaLevelPressure uom="hPa">{ir["sea_level_pressure_hpa"]}</iwxxm-ca:seaLevelPressure>'
        )
    if density_xml:
        parts.append(density_xml)
    if icing_xml:
        parts.append(icing_xml)
    if pres_href:
        parts.append(f'          <iwxxm-ca:pressureChangeIndicator xlink:href="{escape(pres_href)}"/>')
    if processed_xml:
        parts.append(processed_xml)
    parts.extend(
        [
            "        </iwxxm-ca:Addendum>",
            "      </iwxxm:extension>",
        ]
    )
    return "\n".join(parts) + "\n"


def _ca_taf_gml_id(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_ca_taf_gml_id``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    station = str(ir["station"]).lower()
    if ir.get("amendment"):
        return f"taf.ca.amd.{station}"
    if ir.get("nclws"):
        return f"taf.ca.nclws.{station}"
    hrefs = ir.get("ca_forecast_weather_hrefs")
    if isinstance(hrefs, list) and hrefs:
        return f"taf.ca.wx.{station}"
    return f"taf.ca.basic.{station}"


def _prepare_ca_taf_ir(ir: dict[str, Any]) -> dict[str, Any]:
    """
    Internal helper ``_prepare_ca_taf_ir``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    out = dict(ir)
    if out.get("cavok") or out.get("visibility_not_observable"):
        return out
    vis_sm = out.get("visibility_sm")
    if vis_sm is not None:
        out["visibility_display_uom"] = "[mi_i]"
        out["visibility_display_value"] = vis_sm
    return out


def _nclws_extension_inner(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_nclws_extension_inner``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    nclws = ir.get("nclws")
    if not isinstance(nclws, dict):
        return ""
    nclws_data = cast(dict[str, Any], nclws)
    station = str(ir["station"]).lower()
    top_ft = int(nclws_data["layer_top_ft"])
    wind_dir = int(nclws_data["wind_dir_deg"])
    wind_kt = int(nclws_data["wind_speed_kt"])
    return "\n".join(
        [
            f'        <iwxxm-ca:NonConvectiveLowLevelWindShear gml:id="nclws.{station}">',
            f'          <iwxxm-ca:windDirection uom="deg">{wind_dir}</iwxxm-ca:windDirection>',
            f'          <iwxxm-ca:windSpeed uom="[kn_i]">{wind_kt}</iwxxm-ca:windSpeed>',
            "          <iwxxm-ca:layerAboveAerodrome>",
            '            <iwxxm-ca:lowerLimit uom="[ft_i]">0</iwxxm-ca:lowerLimit>',
            f'            <iwxxm-ca:upperLimit uom="[ft_i]">{top_ft}</iwxxm-ca:upperLimit>',
            "          </iwxxm-ca:layerAboveAerodrome>",
            "        </iwxxm-ca:NonConvectiveLowLevelWindShear>",
        ]
    )


def _ca_taf_weather_extension_inner(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_ca_taf_weather_extension_inner``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    hrefs = ir.get("ca_forecast_weather_hrefs")
    if not isinstance(hrefs, list) or not hrefs:
        return ""
    parts: list[str] = []
    for href_obj in cast(list[object], hrefs):
        if not isinstance(href_obj, str) or not href_obj:
            continue
        parts.append(f'        <iwxxm-ca:weather xlink:href="{escape(href_obj)}"/>')
    return "\n".join(parts)


def _taf_forecast_extension(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_taf_forecast_extension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    inner = "\n".join(
        block
        for block in (
            _nclws_extension_inner(ir),
            _ca_taf_weather_extension_inner(ir),
        )
        if block
    )
    if not inner:
        return ""
    return "\n".join(
        [
            "      <iwxxm:extension>",
            inner,
            "      </iwxxm:extension>",
            "",
        ]
    )


def _nclws_extension(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_nclws_extension``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    return _taf_forecast_extension(ir)


def _inject_ca_taf_namespace(xml: str, *, iwxxm_version: str) -> str:
    """
    Internal helper ``_inject_ca_taf_namespace``.

    Parameters
    ----------
    xml : str
        Argument ``xml``.

    iwxxm_version : str
        Argument ``iwxxm_version``.

    Returns
    -------
    str
        Return value.
    """
    needle = f'<iwxxm:TAF xmlns:iwxxm="{NS[iwxxm_version]}"'
    if needle not in xml:
        return xml
    return xml.replace(
        needle,
        f'{needle}\n    xmlns:iwxxm-ca="{CA_NS}"',
        1,
    )


def _inject_ca_taf_gml_id(xml: str, *, gml_id: str) -> str:
    """
    Internal helper ``_inject_ca_taf_gml_id``.

    Parameters
    ----------
    xml : str
        Argument ``xml``.

    gml_id : str
        Argument ``gml_id``.

    Returns
    -------
    str
        Return value.
    """
    return re.sub(r'gml:id="taf\.[^"]+"', f'gml:id="{gml_id}"', xml, count=1)
