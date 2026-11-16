"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _vaa_motion(match: re.Match[str]) -> dict[str, int | float]:
    """
    Record ash-cloud direction and speed, keeping kilometres per hour distinct from knots.

    Parameters
    ----------
    match : re.Match[str]
        ``MOV`` group with a compass point, speed, and unit.

    Returns
    -------
    dict[str, int | float]
        ``motion_dir_deg`` plus either ``motion_speed_kmh`` or ``motion_speed_kt``.
    """
    recorded: dict[str, int | float] = {"motion_dir_deg": _DIR_DEG[match.group("dir").upper()]}
    speed = int(match.group("spd"))
    unit = match.group("unit").upper().replace("/", "")
    if unit == "MPS":
        recorded["motion_speed_kmh"] = round(speed * 3.6)
    elif unit == "KMH":
        recorded["motion_speed_kmh"] = speed
    else:
        recorded["motion_speed_kt"] = speed
    return recorded


def _fields(text: str) -> dict[str, str]:
    """
    Internal helper ``_fields``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    dict[str, str]
        Return value.
    """
    out: dict[str, str] = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        match = _FIELD_LINE.match(line.strip())
        if match and re.fullmatch(r"[A-Z0-9 /+]+", match.group("key").strip()):
            current_key = re.sub(r"\s+", " ", match.group("key").strip().upper())
            out[current_key] = match.group("val").strip()
            continue
        if current_key is not None:
            cont = line.strip()
            if cont:  # pragma: no branch — blank lines already skipped above
                prev = out.get(current_key, "")
                out[current_key] = f"{prev} {cont}".strip() if prev else cont
    return out


def _parse_dtg(token: str) -> str | None:
    """
    Internal helper ``_parse_dtg``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    Returns
    -------
    str | None
        Return value.
    """
    token = token.strip()
    m = _DTG_SHORT.search(token.replace(" ", ""))
    if m:
        return f"{m.group('yyyy')}-{m.group('mm')}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"
    return None


def _day_hhmm_to_iso(token: str, *, issue_iso: str) -> str | None:
    """
    Internal helper ``_day_hhmm_to_iso``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    issue_iso : str
        Argument ``issue_iso``.

    Returns
    -------
    str | None
        Return value.
    """
    m = _DAY_HHMM.search(token.replace(" ", ""))
    if m is None:
        return None
    year = issue_iso[0:4]
    month = issue_iso[5:7]
    return f"{year}-{month}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"


def _latlon(token: str, *, ndigits: int | None = 2) -> tuple[float, float] | None:
    """
    Internal helper ``_latlon``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    ndigits : int | None, optional
        Argument ``ndigits``.

    Returns
    -------
    tuple[float, float] | None
        Return value.
    """
    m = _PSN.search(token)
    if m is None:
        m = re.search(r"(?P<ns>[NS])(?P<lat>\d{4})\s+(?P<ew>[EW])(?P<lon>\d{5})", token)
    if m is None:
        return None
    lat_raw = m.group("lat")
    lon_raw = m.group("lon")
    if len(lat_raw) == 4:
        lat = int(lat_raw[0:2]) + int(lat_raw[2:4]) / 60.0
    else:
        lat = int(lat_raw[0:2]) + int(lat_raw[2:4]) / 60.0 + int(lat_raw[4:5]) / 600.0
    if len(lon_raw) == 5:
        lon = int(lon_raw[0:3]) + int(lon_raw[3:5]) / 60.0
    else:
        lon = int(lon_raw[0:3]) + int(lon_raw[3:5]) / 60.0
    if m.group("ns") == "S":
        lat = -lat
    if m.group("ew") == "W":
        lon = -lon
    if ndigits is None:
        return lat, lon
    return round(lat, ndigits), round(lon, ndigits)


def _point_to_pair(ns: str, lat: str, ew: str, lon: str) -> tuple[float, float]:
    """
    Internal helper ``_point_to_pair``.

    Parameters
    ----------
    ns : str
        Argument ``ns``.

    lat : str
        Argument ``lat``.

    ew : str
        Argument ``ew``.

    lon : str
        Argument ``lon``.

    Returns
    -------
    tuple[float, float]
        Return value.
    """
    lat_f = int(lat[0:2]) + int(lat[2:4]) / 60.0
    lon_f = int(lon[0:3]) + int(lon[3:5]) / 60.0
    if ns == "S":
        lat_f = -lat_f
    if ew == "W":
        lon_f = -lon_f
    return round(lat_f, 2), round(lon_f, 2)


def _pos_list(points: list[tuple[float, float]]) -> str:
    """
    Internal helper ``_pos_list``.

    Parameters
    ----------
    points : list[tuple[float, float]]
        Argument ``points``.

    Returns
    -------
    str
        Return value.
    """
    if not points:
        return ""
    ring = list(points)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return " ".join(f"{lat:.2f} {lon:.2f}" for lat, lon in ring)


def _parse_ash_clouds(blob: str) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_ash_clouds``.

    Parameters
    ----------
    blob : str
        Argument ``blob``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
    upper = " ".join(blob.split())
    if re.search(r"\bNO\s+VA\s+EXP\b", upper):
        return []
    clouds: list[dict[str, Any]] = []
    for match in _CLOUD_CHUNK.finditer(upper):
        level = match.group("level").upper()
        body = match.group("body")
        points = [
            _point_to_pair(m.group("ns"), m.group("lat"), m.group("ew"), m.group("lon")) for m in _POINT.finditer(body)
        ]
        if not points:
            continue
        cloud: dict[str, Any] = {"pos_list": _pos_list(points)}
        sfc = _SFC_FL.search(level)
        band = _FL_BAND.search(level)
        if sfc:
            cloud["lower"] = "GND"
            cloud["lower_ref"] = "SFC"
            cloud["upper_fl"] = int(sfc.group("hi"))
            cloud["upper_ref"] = "STD"
        elif band:  # pragma: no branch — CLOUD_CHUNK levels are SFC or FL band
            cloud["lower_fl"] = int(band.group("lo"))
            cloud["upper_fl"] = int(band.group("hi"))
            cloud["lower_ref"] = "STD"
            cloud["upper_ref"] = "STD"
        mov = _MOV.search(body)
        if mov:
            cloud.update(_vaa_motion(mov))
        clouds.append(cloud)
    return clouds


def _parse_eruption(details: str) -> tuple[str | None, str]:
    """
    Internal helper ``_parse_eruption``.

    Parameters
    ----------
    details : str
        Argument ``details``.

    Returns
    -------
    tuple[str | None, str]
        Return value.
    """
    text = " ".join(details.split())
    m = _ERUPTION_AT.search(text)
    if not m:
        return None, text
    return _parse_dtg(m.group("dtg")), m.group("rest").strip()


def parse_vaa(tac: str, *, product: str = "VAA") -> dict[str, Any]:
    """
    Parse a Volcanic Ash Advisory TAC into IR.

    Parameters
    ----------
    tac : str
        VAA TAC text.

    product : str, optional
        Expected ``VAA``.

    Returns
    -------
    dict[str, Any]
        A Volcanic Ash Advisory TAC into IR.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (parse_vaa)
    2
    """
    if product.upper() != "VAA":
        raise ValueError(f"product mismatch: expected VAA, found {product}")

    text = tac.strip()
    if "VA ADVISORY" not in text.upper():
        raise ValueError("unable to parse VAA: missing VA ADVISORY header")

    fields = _fields(text)
    dtg = fields.get("DTG")
    issue = _parse_dtg(dtg or "") if dtg else None
    if issue is None:
        raise ValueError("unable to parse VAA DTG")

    psn = _latlon(fields.get("PSN", ""))
    elev = fields.get("SOURCE ELEV", "")
    elev_m = None
    elev_match = re.search(r"(\d+)\s*M", elev.upper())
    if elev_match:
        elev_m = int(elev_match.group(1))

    eruption_date, eruption_details = _parse_eruption(fields.get("ERUPTION DETAILS", ""))

    obs_time = _day_hhmm_to_iso(fields.get("OBS VA DTG", ""), issue_iso=issue)
    observation_clouds = _parse_ash_clouds(fields.get("OBS VA CLD", ""))

    forecasts: list[dict[str, Any]] = []
    for hours in (6, 12, 18):
        key = f"FCST VA CLD +{hours} HR"
        raw = fields.get(key, "")
        if not raw:
            continue
        parts = " ".join(raw.split())
        time_iso = _day_hhmm_to_iso(parts, issue_iso=issue)
        if re.search(r"\bNO\s+VA\s+EXP\b", parts.upper()):
            forecasts.append(
                {
                    "hours": hours,
                    "time": time_iso,
                    "status": "NO_VOLCANIC_ASH_EXPECTED",
                    "clouds": [],
                }
            )
        else:
            # Drop leading day/time token before cloud levels.
            cloud_blob = re.sub(r"^\d{2}/\d{4}Z\s*", "", parts)
            forecasts.append(
                {
                    "hours": hours,
                    "time": time_iso,
                    "status": "PROVIDED",
                    "clouds": _parse_ash_clouds(cloud_blob),
                }
            )

    remarks = " ".join(fields.get("RMK", "").split())
    remarks_nil = not remarks or remarks.upper() == "NIL"

    next_adv = _parse_dtg(fields.get("NXT ADVISORY", "")) if fields.get("NXT ADVISORY") else None

    return {
        "ir_version": 1,
        "product": "VAA",
        # F26 theme V2 / TC-F26-006 - advisory root under product=vaa (never VolcanicAshSIGMET).
        "iwxxm_root": "VolcanicAshAdvisory",
        "issue_time": issue,
        "vaac": fields.get("VAAC", "UNKNOWN"),
        "volcano": fields.get("VOLCANO", "UNKNOWN"),
        "area": fields.get("AREA", ""),
        "advisory_number": fields.get("ADVISORY NR", ""),
        "information_source": fields.get("INFO SOURCE", ""),
        "eruption_details": eruption_details,
        "eruption_date": eruption_date,
        "lat": psn[0] if psn else None,
        "lon": psn[1] if psn else None,
        "source_elevation_m": elev_m,
        "observation_time": obs_time,
        "observation_clouds": observation_clouds,
        "forecasts": forecasts,
        "remarks": "" if remarks_nil else remarks,
        "remarks_nil": remarks_nil,
        "next_advisory_time": next_adv,
        "raw": text,
    }
