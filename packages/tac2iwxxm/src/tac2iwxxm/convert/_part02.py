"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _quarantine_identity(product: str, tac: str, now: str) -> str:
    """
    Extra identity elements required on a failed shell.

    Parameters
    ----------
    product : str
        F6 product code.

    tac : str
        Original TAC text.

    now : str
        Issue timestamp.

    Returns
    -------
    str
        Identity XML, or an empty string when the shell already has its fields.
    """
    if product == "TAF":
        return _valid_period_xml(tac, now)
    if product in {"SIGMET", "AIRMET"}:
        unit = _ATS_UNIT.search(tac)
        name = unit.group(1) if unit else None
        return _unit_xml("issuingAirTrafficServicesUnit", name, unit_type="FIC") + _valid_period_xml(tac, now)
    centres = {
        "VAA": ("issuingVolcanicAshAdvisoryCentre", "VAAC", "OTHER:VAAC"),
        "TCA": ("issuingTropicalCycloneAdvisoryCentre", "TCAC", "OTHER:TCAC"),
        "SWXA": ("issuingSpaceWeatherCentre", "SWXC", "OTHER:SWXC"),
    }
    spec = centres.get(product)
    if spec is None:
        return ""
    tag, label, unit_type = spec
    return _unit_xml(tag, _advisory_centre(tac, label), unit_type=unit_type)


def _quarantine_xml(
    product: str,
    tac: str,
    iwxxm_version: str,
    *,
    bulletin_id: str | None = None,
    centre_designator: str | None = None,
    centre_name: str | None = None,
) -> str:
    """
    Emit official-shaped quarantine shell with ``@translationFailedTAC``.

    Parameters
    ----------
    product : str
        F6 product code.

    tac : str
        Original TAC text (stored on translationFailedTAC).

    iwxxm_version : str
        IWXXM release line for namespace.

    Returns
    -------
    str
        Quarantine IWXXM document (no operational observation/baseForecast).
    """
    from datetime import datetime
    from xml.sax.saxutils import escape

    root = _QUARANTINE_ROOT.get(product, product)
    ns = _PREVIEW_NS.get(iwxxm_version, _PREVIEW_NS["2025-2"])
    gml_id = f"{product.lower()}.translation.failed"
    failed_tac = escape(" ".join(tac.split()))
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    designator = centre_designator or ""
    centre = centre_name or ""
    bulletin_attr = f'translatedBulletinID="{escape(bulletin_id)}" ' if bulletin_id else ""
    if bulletin_id or designator or centre:
        centre_attr = f'translationCentreDesignator="{escape(designator)}" translationCentreName="{escape(centre)}" '
    else:
        centre_attr = ""
    station_m = _STATION_AFTER_PRODUCT.search(tac)
    station = station_m.group("station").upper() if station_m else "YUDO"
    aerodrome = ""
    if product in {"METAR", "SPECI", "TAF"}:
        aerodrome = f"""  <iwxxm:aerodrome>
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
"""
    time_block = f"""  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{now}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
"""
    if product in {"METAR", "SPECI"}:
        time_block += f"""  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>{now}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
"""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<iwxxm:{root} xmlns:iwxxm="{ns}" '
        'xmlns:gml="http://www.opengis.net/gml/3.2" '
        'xmlns:aixm="http://www.aixm.aero/schema/5.1.1" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'gml:id="{gml_id}" '
        'reportStatus="NORMAL" '
        'permissibleUsage="OPERATIONAL" '
        f"{bulletin_attr}"
        f'translatedBulletinReceptionTime="{now}" '
        f"{centre_attr}"
        f'translationTime="{now}" '
        f'translationFailedTAC="{failed_tac}">\n'
        f"{time_block}{aerodrome}{_quarantine_identity(product, tac, now)}"
        f"</iwxxm:{root}>\n"
    )


def _remark_span(tac: str, message: str) -> tuple[int | None, int | None]:
    """
    Internal helper ``_remark_span``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    message : str
        Argument ``message``.

    Returns
    -------
    tuple[int | None, int | None]
        Return value.
    """
    for needle, pattern in _REMARK_SPAN_PATTERNS:
        if needle in message:
            match = pattern.search(tac)
            if match is not None:
                return match.start(), match.end()
    return None, None


class ConvertError(ValueError):
    """
    Fatal conversion failure.

    Parameters
    ----------
    message : str
        Human-readable description.
    """

    def __init__(self, message: str) -> None:
        """
        Store ``message``.

        Parameters
        ----------
        message : str
            Human-readable message.
        """
        super().__init__(message)


def _parse(product: str, tac: str) -> dict[str, Any]:
    """
    Internal helper ``_parse``.

    Parameters
    ----------
    product : str
        Argument ``product``.

    tac : str
        Argument ``tac``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    parsers: dict[str, Callable[..., dict[str, Any]]] = {
        "METAR": parse_metar_speci,
        "SPECI": parse_metar_speci,
        "TAF": parse_taf,
        "SIGMET": parse_sigmet,
        "AIRMET": parse_airmet,
        "VAA": parse_vaa,
        "TCA": parse_tca,
        "SWXA": parse_swxa,
        "VONA": parse_vona,
    }
    return parsers[product](tac, product=product)


def _parse_pack_ir(
    product: str,
    tac: str,
    *,
    iwxxm_version: str,
    profile: str,
) -> dict[str, Any]:
    """
    Internal helper ``_parse_pack_ir``.

    Parameters
    ----------
    product : str
        Argument ``product``.

    tac : str
        Argument ``tac``.

    iwxxm_version : str
        Argument ``iwxxm_version``.

    profile : str
        Argument ``profile``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    packs = {item.id: item for item in load_packs(profile)}
    pack_id = pack_id_for_product(product, tac)
    pack = packs.get(pack_id)
    if pack is None:
        msg = f"no pack for product {product!r} ({pack_id})"
        raise PackIrMapError(msg)
    matched = match_tac(
        tac,
        pack,
        context=MatchContext(iwxxm_version=iwxxm_version, profile=profile),
    )
    return map_spans_to_convert_ir(matched, tac=tac, product=product)


def _parse_for_convert(
    product: str,
    tac: str,
    *,
    ir_source: str,
    iwxxm_version: str,
    profile: str,
    ir_source_explicit: bool,
) -> dict[str, Any]:
    """
    Internal helper ``_parse_for_convert``.

    Parameters
    ----------
    product : str
        Argument ``product``.

    tac : str
        Argument ``tac``.

    ir_source : str
        Argument ``ir_source``.

    iwxxm_version : str
        Argument ``iwxxm_version``.

    profile : str
        Argument ``profile``.

    ir_source_explicit : bool
        Argument ``ir_source_explicit``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    if ir_source == "pack":
        try:
            return _parse_pack_ir(product, tac, iwxxm_version=iwxxm_version, profile=profile)
        except PackIrMapError:
            if ir_source_explicit:
                raise
            # auto/default: incomplete packs fall back to the legacy parser.
            return _parse(product, tac)
    return _parse(product, tac)


def _emit(product: str, profile: str, ir: dict[str, Any], iwxxm_version: str) -> str:
    """
    Internal helper ``_emit``.

    Parameters
    ----------
    product : str
        Argument ``product``.

    profile : str
        Argument ``profile``.

    ir : dict[str, Any]
        Argument ``ir``.

    iwxxm_version : str
        Argument ``iwxxm_version``.

    Returns
    -------
    str
        Return value.
    """
    if product in {"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA"}:
        # ADR-047: core F6 products emit via YAML maps (python plugins remain builders).
        return emit_with_map(ir, product=product, profile=profile, iwxxm_version=iwxxm_version)
    if product == "SWXA":
        return emit_swxa_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "VONA":
        return emit_vona_annex3(ir, iwxxm_version=iwxxm_version)
    raise ValueError(f"no emitter for product {product!r}")


def _inject_translation_centre(
    xml: str,
    *,
    designator: str,
    name: str,
    heading: tuple[str, str] | None = None,
) -> str:
    """
    Insert ``translationCentre*`` attributes on the IWXXM root element.

    Parameters
    ----------
    xml : str
        Successful convert document (not a quarantine shell).
    designator : str
        ``translationCentreDesignator`` value.
    name : str
        ``translationCentreName`` value.

    Returns
    -------
    str
        XML with centre attributes on the first ``iwxxm:*`` root start tag.
    """
    extra = f'\n    translationCentreDesignator="{escape(designator)}"\n    translationCentreName="{escape(name)}"'
    if heading is not None:
        bulletin_id, translation_time = heading
        extra += (
            f'\n    translatedBulletinID="{escape(bulletin_id)}"'
            f'\n    translatedBulletinReceptionTime="{escape(translation_time)}"'
            f'\n    translationTime="{escape(translation_time)}"'
        )
    match = _ROOT_OPEN.search(xml)
    if match is None:
        return xml
    return xml[: match.start()] + match.group(1) + match.group(2) + extra + match.group(3) + xml[match.end() :]


def _xml_gzip(xml: str | None, suggested_filename: str | None) -> bytes | None:
    """
    Gzip the IWXXM text when the suggested name ends in ``.xml.gz``.

    Parameters
    ----------
    xml : str | None
        IWXXM document text.

    suggested_filename : str | None
        Guideline filename, or ``None``.

    Returns
    -------
    bytes | None
        Compressed document, or ``None`` when there is nothing to compress.

    Examples
    --------
    >>> _xml_gzip(None, None) is None
    True
    """
    if xml and suggested_filename and suggested_filename.endswith(".xml.gz"):
        return gzip.compress(xml.encode("utf-8"))
    return None
