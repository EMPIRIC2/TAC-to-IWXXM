"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def emit_sigmet_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit SIGMET annex3 body with IWXXM-US namespace and weather-hazard extensions.

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed product fields.

    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    str
        SIGMET annex3 body with IWXXM-US namespace and weather-hazard extensions.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_sigmet_iwxxm_us)
    2
    """
    from tac2iwxxm.profiles.annex3_emit import emit_sigmet_annex3

    xml = emit_sigmet_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    for prefix in ("basic", "conv", "va", "tc", "cnl"):
        xml = xml.replace(f'gml:id="sigmet.{prefix}.', 'gml:id="sigmet.us.', 1)
    ext = _sigmet_weather_hazards_extension(ir)
    return _inject_evolving_extension(xml, ext, "</iwxxm:SIGMETEvolvingCondition>")


def emit_airmet_iwxxm_us(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit AIRMET annex3 body with IWXXM-US namespace and weather-hazard extensions.

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed product fields.

    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    str
        AIRMET annex3 body with IWXXM-US namespace and weather-hazard extensions.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_airmet_iwxxm_us)
    2
    """
    from tac2iwxxm.profiles.annex3_emit import emit_airmet_annex3

    xml = emit_airmet_annex3(ir, iwxxm_version=iwxxm_version)
    xml = _with_us_namespace(xml)
    xml = xml.replace('gml:id="airmet.basic.', 'gml:id="airmet.us.', 1)
    ext = _airmet_weather_hazards_extension(ir)
    xml = _inject_evolving_extension(xml, ext, "</iwxxm:AIRMETEvolvingCondition>")
    inline_lo = ir.get("inline_frzlvl_lo")
    inline_hi = ir.get("inline_frzlvl_hi")
    if inline_lo is not None and inline_hi is not None:
        inline_ext = _inline_freezing_levels_xml(int(inline_lo), int(inline_hi), prefix="obs")
        xml = _inject_first_evolving_extension(xml, inline_ext)
    outlook_raw = ir.get("outlook")
    if isinstance(outlook_raw, dict):
        outlook_ir = cast(dict[str, Any], outlook_raw)
        subperiod = _airmet_subperiod_extension(ir, outlook_ir)
        fir = str(ir["fir"]).lower()
        member_token = f'gml:id="cond.{fir}.outlook.1"'
        if member_token in xml:
            start = xml.index(member_token)
            close_idx = xml.index("</iwxxm:AIRMETEvolvingCondition>", start)
            xml = xml[:close_idx] + subperiod + xml[close_idx:]
    frzlvl_ext = _airmet_freezing_level_forecast_extension(ir)
    if frzlvl_ext and "</iwxxm:AIRMET>" in xml:
        xml = xml.replace("</iwxxm:AIRMET>", f"{frzlvl_ext}</iwxxm:AIRMET>", 1)
    return xml
