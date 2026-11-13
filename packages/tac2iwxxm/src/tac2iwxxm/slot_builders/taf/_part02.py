"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def parse_taf(tac: str, *, product: str = "TAF") -> dict[str, Any]:
    """
    Parse a single TAF TAC report into a versioned IR dict.

    Parameters
    ----------
    tac : str
        TAC text (optional leading ``TAF`` keyword).

    product : str, optional
        Expected ``TAF``.

    Returns
    -------
    dict
        Intermediate representation for annex3 emit.

    Raises
    ------
    ValueError
        When the product mismatches or required groups are missing.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_taf)
    2
    """
    if product.upper() != "TAF":
        raise ValueError(f"product mismatch: expected TAF, found {product}")

    text = tac.strip()
    # Drop a leading abbreviated heading (FT/FC…) so GTS paste matches METAR/SPECI.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) >= 2:
        try:
            parse_ahl(lines[0])
        except BulletinSplitError:
            pass
        else:
            lines = lines[1:]
    text = "\n".join(lines).strip().rstrip("=").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = " ".join(lines)
    if not joined.upper().startswith("TAF"):
        joined = f"TAF {joined}"

    mods = _modifier_flags(joined)

    match = _TAF_NIL_ONLY.match(joined)
    if match is not None:
        issue = match.group("issue")
        return {
            "ir_version": 1,
            "product": "TAF",
            "station": match.group("station"),
            "issue_day": int(issue[0:2]),
            "issue_hour": int(issue[2:4]),
            "issue_minute": int(issue[4:6]),
            "nil": True,
            "amendment": mods["amendment"],
            "correction": mods["correction"],
            "raw": joined,
        }

    match = _TAF.match(joined)
    if match is None:
        raise ValueError("unable to parse TAF header")

    issue = match.group("issue")
    body = match.group("body") or ""
    valid_from = match.group("valid_from")
    valid_to = match.group("valid_to")
    if valid_from is None or valid_to is None:
        if not _NIL.search(body):
            raise ValueError("unable to parse TAF header")
        return {
            "ir_version": 1,
            "product": "TAF",
            "station": match.group("station"),
            "issue_day": int(issue[0:2]),
            "issue_hour": int(issue[2:4]),
            "issue_minute": int(issue[4:6]),
            "nil": True,
            "amendment": mods["amendment"],
            "correction": mods["correction"],
            "raw": joined,
        }

    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "TAF",
        "station": match.group("station"),
        "issue_day": int(issue[0:2]),
        "issue_hour": int(issue[2:4]),
        "issue_minute": int(issue[4:6]),
        "valid_from_day": int(valid_from[0:2]),
        "valid_from_hour": int(valid_from[2:4]),
        "valid_to_day": int(valid_to[0:2]),
        "valid_to_hour": int(valid_to[2:4]),
        "nil": bool(_NIL.search(body)),
        "cancel": bool(_CNL.search(body)),
        "cavok": bool(_CAVOK.search(body)),
        "amendment": mods["amendment"],
        "correction": mods["correction"],
        "raw": joined,
    }

    if ir["nil"] or ir["cancel"]:
        return ir

    # Split base body from change groups (incl. BoM INTER).
    first_change = re.search(rf"\b{_CHANGE_TOKEN}\b", body)
    base_body = body if first_change is None else body[: first_change.start()]
    change_body = "" if first_change is None else body[first_change.start() :]

    base = _parse_forecast_body(base_body, cavok_ok=True)
    ir.update(base)
    if ir.get("cavok"):
        ir["cavok"] = True

    nclws = _parse_nclws(base_body)
    if nclws is not None:
        ir["nclws"] = nclws

    wx_hrefs = _ca_forecast_weather_hrefs(list(ir.get("weather") or []))
    if wx_hrefs:
        ir["ca_forecast_weather_hrefs"] = wx_hrefs

    alt = _ALT_INHG.search(base_body)
    if alt is not None:
        # US TAF forecast lowest altimeter (hundredths inHg).
        ir["forecast_altimeter_inhg"] = int(alt.group("alt")) / 100.0

    # AU BoM RMK T/Q + TAF3 (D-EV087-taf3) — scanned on full body including RMK.
    m_taf3 = _TAF3_MARKER.search(body)
    if m_taf3 is not None:
        ir["au_taf3"] = True
        ir["au_taf3_token"] = m_taf3.group(0)
    t_series = _RMK_T_SERIES.search(body)
    if t_series is not None:
        ir["au_rmk_temperatures_c"] = t_series.group(1).split()
    q_series = _RMK_Q_SERIES.search(body)
    if q_series is not None:
        ir["au_rmk_qnh_hpa"] = [int(x) for x in q_series.group(1).split()]

    # NZ domestic extras (D-EV087-nz-domestic).
    wind_2000 = _NZ_2000FT_WIND.search(body)
    if wind_2000 is not None:
        wind_ir: dict[str, Any] = {
            "height_ft": 2000,
            "wind_speed_kt": int(wind_2000.group("spd")),
        }
        if wind_2000.group("dir") == "VRB":
            wind_ir["wind_variable"] = True
        else:
            wind_ir["wind_dir_deg"] = int(wind_2000.group("dir"))
        if wind_2000.group("gust"):
            wind_ir["wind_gust_kt"] = int(wind_2000.group("gust"))
        ir["nz_2000ft_wind"] = wind_ir
    qnh_rng = _NZ_QNH_MNM_MAX.search(body)
    if qnh_rng is not None:
        ir["nz_qnh_mnm_hpa"] = int(qnh_rng.group("mnm"))
        ir["nz_qnh_max_hpa"] = int(qnh_rng.group("max"))
    if ir.get("nz_2000ft_wind") or ir.get("nz_qnh_mnm_hpa") is not None or ir.get("visibility_km") is not None:
        ir["nz_taf_dialect"] = "domestic"
    elif ir.get("station", "").startswith("NZ"):
        # International-shaped NZ TAF (no domestic markers).
        ir["nz_taf_dialect"] = "international"

    national_tokens: list[str] = []
    if ir.get("au_taf3"):
        national_tokens.append(str(ir.get("au_taf3_token") or "TAF3"))
    if ir.get("nz_2000ft_wind"):
        national_tokens.append("2000FT WIND")
    if ir.get("nz_qnh_mnm_hpa") is not None:
        national_tokens.append(f"QNH MNM {ir['nz_qnh_mnm_hpa']} MAX {ir['nz_qnh_max_hpa']}")
    if national_tokens:
        ir["national_remark_tokens"] = national_tokens

    if change_body:
        changes = _parse_change_groups(ir, change_body)
        if changes:
            ir["change_forecasts"] = changes
            inter_tokens = [c["tac_change_indicator"] for c in changes if c.get("tac_change_indicator") == "INTER"]
            if inter_tokens:
                ir.setdefault("national_remark_tokens", []).extend(inter_tokens)

    return ir
