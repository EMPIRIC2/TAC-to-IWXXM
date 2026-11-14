"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _apply_airmet_area_to_ir(ir: dict[str, Any], area: dict[str, Any]) -> None:
    """
    Internal helper ``_apply_airmet_area_to_ir``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    area : dict[str, Any]
        Argument ``area``.
    """
    ir.update(area)


def _parse_sequence_token(raw: str) -> tuple[int, str]:
    """
    Internal helper ``_parse_sequence_token``.

    Parameters
    ----------
    raw : str
        Argument ``raw``.

    Returns
    -------
    tuple[int, str]
        Return value.
    """
    token = " ".join(raw.upper().split())
    phonetic = re.fullmatch(r"([A-Z]+)\s+(\d+)", token)
    if phonetic is not None:
        return int(phonetic.group(2)), token
    lettered = re.fullmatch(r"([A-Z])(\d+)", token)
    if lettered is not None:
        return int(lettered.group(2)), token
    numeric = re.fullmatch(r"(\d+)", token)
    if numeric is not None:
        return int(numeric.group(1)), token
    raise ValueError(f"unable to parse SIGMET/AIRMET sequence: {raw!r}")


def _strip_siga0_heading(text: str) -> str:
    """
    Internal helper ``_strip_siga0_heading``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    str
        Return value.
    """
    lines = [ln for ln in text.splitlines() if not _SIGA0_LINE.match(ln.strip())]
    return "\n".join(lines)


def _parse_convective_sigmet(
    text: str,
    *,
    issue_day: int | None = None,
    office: str | None = None,
) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_convective_sigmet``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    issue_day : int | None, optional
        Day of month used when ``VALID UNTIL`` has no day.

    office : str | None, optional
        Issuing office from the heading when the body has no unit id.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    match = _CONVECTIVE_SIGMET.match(text)
    if match is None:
        return None
    body = re.split(
        r"\b(?:OUTLOOK|REF\s+INTL)\b",
        match.group("body"),
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    tag = match.group("tag").upper()
    named_unit = match.group("unit")
    unit = (named_unit or office or "MKCC").upper()
    to_d, to_h, to_m = _parse_until_token(match.group("until"), issue_day=issue_day)
    # Active period ends at UNTIL; issue ~2h earlier (NWS convective convention).
    from_h = to_h - 2
    from_d = to_d
    from_m = to_m
    if from_h < 0:
        from_h += 24
        from_d = max(1, from_d - 1)
    states = " ".join(match.group("states").upper().split())
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "SIGMET",
        "fir": unit,
        "mwo": "KKCI",
        "sequence": 0,
        "valid_from_day": from_d,
        "valid_from_hour": from_h,
        "valid_from_minute": from_m,
        "valid_to_day": to_d,
        "valid_to_hour": to_h,
        "valid_to_minute": to_m,
        "convective": True,
        "convective_tag": tag,
        "affected_states": states,
        "fir_name": f"{unit} FIC",
        "raw": text,
        "us_sigmet_hazard": {
            "href": _NWS_SIGMET_AREA_TS,
            "tag": tag,
        },
    }
    area_mov = _AREA_TS_MOV.search(body)
    if area_mov is not None:
        ir["motion_dir_deg"] = int(area_mov.group("dir"))
        ir["motion_speed_kt"] = int(area_mov.group("spd"))
    top = _TOP_FL.search(body)
    if top is not None:
        ir["top_fl"] = int(top.group("fl"))
        if "ABV" in top.group(0).upper():
            ir["top_qualifier"] = "ABV"
        elif "BLW" in top.group(0).upper():
            ir["top_qualifier"] = "BLW"
    elif re.search(r"\bTOPS\s+TO\s+FL(?P<fl>\d{2,3})\b", body, re.I):
        fl_m = re.search(r"\bTOPS\s+TO\s+FL(?P<fl>\d{2,3})\b", body, re.I)
        if fl_m is not None:  # pragma: no branch — same regex as elif guard
            ir["top_fl"] = int(fl_m.group("fl"))
            ir["top_qualifier"] = "TO"
    # Isolate the FROM chain before AREA / DVLPG / LINE / DMSHG hazard lead-ins (NWS WST).
    geom_src = re.split(
        r"\b(?:DVLPG|AREA|DMSHG\s+LINE|LINE)\b",
        body,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    vor_geometry = parse_vor_reference_geometry(f"FROM {geom_src}")
    if vor_geometry is not None:
        ir["geometry"] = vor_geometry
    return ir


def _sigmet_region_indicator(match: re.Match[str], body: str) -> str:
    """
    Return the flight information region indicator for a SIGMET header.

    Parameters
    ----------
    match : re.Match[str]
        Header match. The leading indicator may be absent.

    body : str
        SIGMET body after the watch-office hyphen.

    Returns
    -------
    str
        Leading indicator, else the four-letter token before ``FIR``, else the watch office.
    """
    raw = match.group("fir")
    if raw:
        return raw.upper()
    named = _BODY_FIR.search(body.upper())
    if named is not None:
        return named.group("fir")
    return match.group("mwo").upper()


def parse_sigmet(tac: str, *, product: str = "SIGMET") -> dict[str, Any]:
    """
    Parse a SIGMET TAC into IR.

    Parameters
    ----------
    tac : str
        SIGMET TAC text.

    product : str, optional
        Expected ``SIGMET``.

    Returns
    -------
    dict
        Intermediate representation.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_sigmet)
    2
    """
    if product.upper() != "SIGMET":
        raise ValueError(f"product mismatch: expected SIGMET, found {product}")

    raw_in = tac.lstrip("\ufeff").lstrip()
    ahl_tt: str | None = None
    ahl_match = _AHL_PREFIX.match(raw_in)
    body_tac = raw_in
    if ahl_match is not None:
        ahl_tt = ahl_match.group("tt").upper()
        body_tac = raw_in[ahl_match.end() :]

    body_tac = _strip_siga0_heading(body_tac)
    body_tac = unwrap_wrapped_coordinates(body_tac)
    text = _normalize(body_tac)
    issue_day = int(ahl_match.group("yygggg")[:2]) if ahl_match is not None else None
    office = ahl_match.group("cccc") if ahl_match is not None else None
    conv = _parse_convective_sigmet(text, issue_day=issue_day, office=office)
    if conv is not None:
        if ahl_tt is not None:
            conv["ahl_tt"] = ahl_tt
        return conv
    match = _SIGMET.match(text)
    if match is None:
        raise ValueError("unable to parse SIGMET header")

    body = without_cancellation_remark(match.group("body"))
    from_d, from_h, from_m = _parse_valid(match.group("from"))
    to_d, to_h, to_m = _parse_valid(match.group("to"))
    _require_ordered_valid_period(from_d, from_h, from_m, to_d, to_h, to_m, product="SIGMET")
    seq_num, seq_label = _parse_sequence_token(match.group("seq"))
    fir = _sigmet_region_indicator(match, body)
    upper_body = body.upper()
    if "AMSWELL" in upper_body:
        fir_name = "AMSWELL FIR"
    elif "SHANLON" in upper_body:
        fir_name = "SHANLON FIR/UIR"
    elif "SHANWICK OCEANIC FIR" in upper_body:
        fir_name = "SHANWICK OCEANIC FIR"
    else:
        fir_name = flight_information_region_name(
            body,
            fir,
            watch_office=match.group("mwo"),
        )
    phenomenon = _detect_phenomenon(body, _SIG_PHENOMENA)
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "SIGMET",
        "fir": fir,
        "mwo": match.group("mwo").upper(),
        "sequence": seq_num,
        "valid_from_day": from_d,
        "valid_from_hour": from_h,
        "valid_from_minute": from_m,
        "valid_to_day": to_d,
        "valid_to_hour": to_h,
        "valid_to_minute": to_m,
        "fir_name": fir_name,
        "raw": text,
    }
    if phenomenon is not None:
        ir["phenomenon"] = phenomenon
    if seq_label != str(seq_num):
        ir["sequence_label"] = seq_label
    fir_extra = match.groupdict().get("fir_extra")
    extras = [p for p in (fir_extra or "").upper().split() if len(p) == 4]
    if extras:
        ir["additional_firs"] = extras
    if ahl_tt is not None:
        ir["ahl_tt"] = ahl_tt
    _enrich_sigmet_body(ir, body)
    if not ir.get("cancel") and not ir.get("phenomenon"):
        # AirWx tokens such as MOD TURB belong on AIRMET; SigWx uses SEV TURB.
        if re.search(r"\bMOD\s+TURB\b", body, flags=re.IGNORECASE):
            raise ValueError(
                "SIGMET body missing phenomenon: moderate turbulence (MOD TURB) is "
                "not a SIGMET phenomenon — use SEV TURB on a SIGMET, or issue an AIRMET"
            )
        raise ValueError("SIGMET body missing phenomenon")
    # Content-selected IWXXM root under product=sigmet (E19-13 / F23 V2 / TC-EV029-004).
    # WC/WV AHL select family roots for CNL when the body omits phenomenon.
    if ir.get("phenomenon") == "TC" or ahl_tt == "WC":
        ir["iwxxm_root"] = "TropicalCycloneSIGMET"
    elif ir.get("phenomenon") == "VA" or ir.get("va_cnl_fir_moved") or (ahl_tt == "WV" and ir.get("cancel")):
        ir["iwxxm_root"] = "VolcanicAshSIGMET"
    return ir


def parse_airmet(tac: str, *, product: str = "AIRMET") -> dict[str, Any]:
    """
    Parse an AIRMET TAC into IR.

    Parameters
    ----------
    tac : str
        AIRMET TAC text.

    product : str, optional
        Expected ``AIRMET``.

    Returns
    -------
    dict
        Intermediate representation.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_airmet)
    2
    """
    if product.upper() != "AIRMET":
        raise ValueError(f"product mismatch: expected AIRMET, found {product}")

    raw_in = tac.strip()
    ahl_tt: str | None = None
    ahl_match = _AHL_PREFIX.match(raw_in)
    body_tac = raw_in
    if ahl_match is not None:
        ahl_tt = ahl_match.group("tt").upper()
        body_tac = raw_in[ahl_match.end() :]

    text = _normalize(body_tac)
    conus = _try_parse_conus_airmet(text)
    if conus is not None:
        body = conus.pop("body")
        ir: dict[str, Any] = {
            "ir_version": 1,
            "product": "AIRMET",
            "raw": text,
            **conus,
        }
    else:
        match = _AIRMET.match(text)
        if match is None:
            raise ValueError("unable to parse AIRMET header")

        body = match.group("body")
        from_d, from_h, from_m = _parse_valid(match.group("from"))
        to_d, to_h, to_m = _parse_valid(match.group("to"))
        _require_ordered_valid_period(from_d, from_h, from_m, to_d, to_h, to_m, product="AIRMET")
        seq_num, seq_label = _parse_sequence_token(match.group("seq"))
        phenomenon = _detect_phenomenon(body, _AIR_PHENOMENA)
        ir = {
            "ir_version": 1,
            "product": "AIRMET",
            "fir": match.group("fir").upper(),
            "mwo": match.group("mwo").upper(),
            "sequence": seq_num,
            "valid_from_day": from_d,
            "valid_from_hour": from_h,
            "valid_from_minute": from_m,
            "valid_to_day": to_d,
            "valid_to_hour": to_h,
            "valid_to_minute": to_m,
            "fir_name": "SHANLON FIR" if "SHANLON" in body.upper() else match.group("fir").upper(),
            "raw": text,
        }
        if phenomenon is not None:
            ir["phenomenon"] = phenomenon
        if seq_label != str(seq_num):
            ir["sequence_label"] = seq_label
    main_body, outlook_body = _split_airmet_main_and_outlook(body)
    hazard_body, frzlvl_from_main = _split_frzlvl_section(main_body)
    frzlvl_body = frzlvl_from_main
    if outlook_body is not None:
        outlook_hazard, frzlvl_from_outlook = _split_frzlvl_section(outlook_body)
        if frzlvl_from_outlook is not None:
            frzlvl_body = frzlvl_from_outlook
            outlook_body = outlook_hazard
    if ahl_tt is not None:
        ir["ahl_tt"] = ahl_tt
    gfa_code = _detect_ca_gfa_phenomenon(hazard_body)
    if gfa_code is not None:
        ir["ca_gfa_phenomenon"] = gfa_code
        structured = _parse_ca_gfa_structured(hazard_body, gfa_code)
        if structured is not None:
            ir["ca_gfa_structured"] = structured
    chart = _GFA_CHART.search(hazard_body)
    if chart is not None:
        ir["gfa_chart_id"] = chart.group(1).upper()
    area_segments = _split_airmet_areas(hazard_body)
    default_phenomenon = ir.get("phenomenon")
    default_phenomenon_s = str(default_phenomenon) if default_phenomenon is not None else None
    if len(area_segments) > 1:
        areas = [_airmet_area_ir(segment, default_phenomenon=default_phenomenon_s) for segment in area_segments]
        ir["areas"] = areas
        _apply_airmet_area_to_ir(ir, areas[0])
    else:
        _enrich_hazard_body(ir, hazard_body)
    if frzlvl_body is not None:
        ir["frzlvl_section"] = _parse_frzlvl_section(frzlvl_body)
    if outlook_body is not None:
        if default_phenomenon_s is None:
            raise ValueError("AIRMET body missing phenomenon")
        outlook = _parse_airmet_outlook(outlook_body, default_phenomenon=default_phenomenon_s)
        outlook["valid_from_day"] = ir["valid_from_day"]
        if outlook["valid_to_hour"] < outlook["valid_from_hour"] or (
            outlook["valid_to_hour"] == outlook["valid_from_hour"]
            and outlook["valid_to_minute"] < outlook["valid_from_minute"]
        ):
            outlook["valid_to_day"] = ir["valid_to_day"] + 1
        else:
            outlook["valid_to_day"] = ir["valid_to_day"]
        ir["outlook"] = outlook
    if not ir.get("cancel") and not ir.get("phenomenon") and not ir.get("ca_gfa_phenomenon"):
        raise ValueError("AIRMET body missing phenomenon")
    _attach_us_airmet_hazard(ir)
    return ir
