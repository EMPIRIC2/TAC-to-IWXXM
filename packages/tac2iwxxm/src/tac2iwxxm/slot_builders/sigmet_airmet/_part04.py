"""Split part body (exec'd into package namespace) — US domestic WS SIGMET."""

from __future__ import annotations


def _parse_us_domestic_ws_sigmet(
    text: str,
    *,
    issue_day: int | None = None,
    issue_hour: int | None = None,
    issue_minute: int | None = None,
    office: str | None = None,
) -> dict[str, Any] | None:
    """
    Parse a US domestic non-convective WS SIGMET (``VALID UNTIL`` form).

    Parameters
    ----------
    text : str
        Normalized SIGMET TAC (AHL already stripped).

    issue_day : int | None, optional
        Day of month from the WMO abbreviated heading.

    issue_hour : int | None, optional
        Hour from the WMO abbreviated heading.

    issue_minute : int | None, optional
        Minute from the WMO abbreviated heading.

    office : str | None, optional
        Issuing CCCC from the abbreviated heading when the body has no unit id.

    Returns
    -------
    dict[str, Any] | None
        Intermediate representation, or ``None`` when the text is not this form.
    """
    match = _US_DOMESTIC_WS_SIGMET.match(text)
    if match is None:
        return None
    body = match.group("body").strip()
    geom_src = _US_DOMESTIC_WS_HAZARD_SPLIT.split(body, maxsplit=1)[0]
    named_unit = match.group("unit")
    unit = (named_unit or office or "KKCI").upper()
    until_raw = match.group("until")
    to_d, to_h, to_m = _parse_until_token(until_raw, issue_day=issue_day)
    issue_token = match.group("issue")
    if issue_token:
        from_d, from_h, from_m = _parse_valid(issue_token)
    elif issue_day is not None and issue_hour is not None and issue_minute is not None:
        from_d, from_h, from_m = issue_day, issue_hour, issue_minute
    else:
        # Domestic WS periods are commonly four hours when only UNTIL is present.
        from_h = to_h - 4
        from_d = to_d
        from_m = to_m
        if from_h < 0:
            from_h += 24
            from_d = max(1, from_d - 1)
    seq_num, seq_label = _parse_sequence_token(match.group("seq"))
    states = " ".join(match.group("states").upper().split())
    mwo = (office or "KKCI").upper()
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "SIGMET",
        "fir": unit,
        "mwo": mwo,
        "sequence": seq_num,
        "valid_from_day": from_d,
        "valid_from_hour": from_h,
        "valid_from_minute": from_m,
        "valid_to_day": to_d,
        "valid_to_hour": to_h,
        "valid_to_minute": to_m,
        "affected_states": states,
        "fir_name": f"{unit} FIC",
        "raw": text,
        "us_domestic_ws": True,
    }
    if seq_label != str(seq_num):
        ir["sequence_label"] = seq_label
    phenomenon = _detect_phenomenon(body, _SIG_PHENOMENA)
    if phenomenon is not None:
        ir["phenomenon"] = phenomenon
    if not ir.get("cancel") and not ir.get("phenomenon"):
        # Fail closed before VOR geometry so missing-hazard TACs do not raise UnknownVOR.
        raise ValueError("SIGMET body missing phenomenon")
    blw = _US_DOMESTIC_WS_BLW.search(body)
    if blw is not None:
        ir["top_fl"] = int(blw.group("fl"))
        ir["top_qualifier"] = "BLW"
    # Prefixed FROM so the VOR chain parser sees a closed ring before the hazard lead-in.
    vor_geometry = parse_vor_reference_geometry(f"FROM {geom_src}")
    if vor_geometry is not None:
        ir["geometry"] = vor_geometry
    return ir
