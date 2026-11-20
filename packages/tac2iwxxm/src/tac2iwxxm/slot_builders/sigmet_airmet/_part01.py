"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _normalize(tac: str) -> str:
    """
    Internal helper ``_normalize``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    Returns
    -------
    str
        Return value.
    """
    lines = [ln.strip() for ln in tac.strip().rstrip("=").splitlines() if ln.strip()]
    return " ".join(lines)


def _parse_valid(token: str) -> tuple[int, int, int]:
    """
    Internal helper ``_parse_valid``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    Returns
    -------
    tuple[int, int, int]
        Return value.
    """
    return int(token[0:2]), int(token[2:4]), int(token[4:6])


def _apply_motion(ir: dict[str, Any], body: str) -> None:
    """
    Record movement direction and speed, keeping kilometres per hour distinct from knots.

    Parameters
    ----------
    ir : dict
        Hazard intermediate representation being filled.
    body : str
        SIGMET or AIRMET body text.

    Returns
    -------
    None
        ``ir`` is updated in place when a movement group matches.
    """
    if ir.get("stationary"):
        return
    mov = _MOV.search(body)
    if mov is None:
        degrees = compound_movement_degrees(body)
        if degrees is None:
            return
        ir["motion_dir_deg"] = degrees
        return
    ir["motion_dir_deg"] = _DIR_DEG[mov.group("dir").upper()]
    if mov.group("spd") is None:
        return
    speed = int(mov.group("spd"))
    unit = mov.group("unit").upper().replace("/", "")
    if unit == "MPS":
        ir["motion_speed_kmh"] = round(speed * 3.6)
    elif unit == "KMH":
        ir["motion_speed_kmh"] = speed
    else:
        ir["motion_speed_kt"] = speed


def _detect_phenomenon(body: str, table: tuple[tuple[str, str], ...]) -> str | None:
    """
    Return the first matching phenomenon code, or ``None`` when none match.

    Parameters
    ----------
    body : str
        Hazard body text.

    table : tuple[tuple[str, str], ...]
        Needle → IR code pairs, longest / most specific first.

    Returns
    -------
    str | None
        Matched IR phenomenon code, or ``None`` (do not invent ``TS``).
    """
    upper = body.upper()
    for needle, code in table:
        if needle in upper:
            return code
    return None


def _require_ordered_valid_period(
    from_day: int,
    from_hour: int,
    from_minute: int,
    to_day: int,
    to_hour: int,
    to_minute: int,
    *,
    product: str,
) -> None:
    """
    Reject same-day VALID groups whose end is not after begin.

    Day-of-month wrap (for example ``312200/010200``) stays allowed. Same-day
    inverted or zero-length periods fail closed.

    Parameters
    ----------
    from_day, from_hour, from_minute : int
        VALID begin group.
    to_day, to_hour, to_minute : int
        VALID end group.
    product : str
        ``SIGMET`` or ``AIRMET`` for the error message.
    """
    if from_day == to_day and (to_hour, to_minute) <= (from_hour, from_minute):
        raise ValueError(f"{product} valid period end must be after begin")


def _detect_ca_gfa_phenomenon(body: str) -> str | None:
    """
    Internal helper ``_detect_ca_gfa_phenomenon``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    str | None
        Return value.
    """
    upper = body.upper()
    for needle, code in _CA_GFA_PHENOMENA:
        if needle in upper:
            return code
    return None


def _parse_ca_gfa_structured(body: str, gfa_code: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_ca_gfa_structured``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    gfa_code : str
        Argument ``gfa_code``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    if gfa_code not in {"SFC_VIS_and_BKN_CLD", "SFC_VIS_and_OVC_CLD"}:
        return None
    structured: dict[str, Any] = {}
    sm = _GFA_SFC_VIS_SM.search(body)
    if sm is not None:
        metres = int(sm.group("vis")) * 1609
        structured["surface_visibility_m"] = {"lower": metres, "higher": metres}
    else:
        vis_m = _GFA_SFC_VIS_M.search(body)
        if vis_m is not None:
            metres = int(vis_m.group("vis"))
            structured["surface_visibility_m"] = {"lower": metres, "higher": metres}
    cloud = _GFA_CLOUD_BASE.search(body)
    if cloud is not None:
        base_ft = int(cloud.group("base")) * 100
        structured["cloud_base_ft"] = {"lower": base_ft, "higher": base_ft}
    spd = re.search(r"\bMOV\s+[NSEW]{1,2}\s+(?P<spd>\d{2,3})KT\b", body.upper())
    if spd is not None:
        kt = int(spd.group("spd"))
        structured["surface_wind_kt"] = {"lower": kt, "higher": kt}
    return structured or None


def _detect_intensity(body: str) -> str:
    """
    Internal helper ``_detect_intensity``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    str
        Return value.
    """
    upper = body.upper()
    for token, code in _INTENSITY.items():
        if re.search(rf"\b{token}\b", upper):
            return code
    return "NO_CHANGE"


def _point_lat_lon(match: re.Match[str]) -> tuple[float, float]:
    """
    Internal helper ``_point_lat_lon``.

    Parameters
    ----------
    match : re.Match[str]
        Argument ``match``.

    Returns
    -------
    tuple[float, float]
        Return value.
    """
    lat = int(match.group("lat_deg")) + int(match.group("lat_min")) / 60.0
    lon = int(match.group("lon_deg")) + int(match.group("lon_min")) / 60.0
    groups = match.groupdict()
    if (groups.get("lat_hemi") or "N").upper() == "S":
        lat = -lat
    if (groups.get("lon_hemi") or "E").upper() == "W":
        lon = -lon
    if abs(lat) > 90.0 or abs(lon) > 180.0:
        raise ValueError(f"coordinate out of range: lat={lat}, lon={lon}")
    return lat, lon


def _format_pos_list(points: list[tuple[float, float]]) -> str:
    """
    Join latitude and longitude pairs for a GML position list.

    Parameters
    ----------
    points : list[tuple[float, float]]
        Vertices in latitude, longitude order.

    Returns
    -------
    str
        Space-separated positions.
    """
    return " ".join(f"{lat:.4f} {lon:.4f}" for lat, lon in points)


def _close_ring(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """
    Repeat the first vertex so a GML linear ring is closed.

    Parameters
    ----------
    points : list[tuple[float, float]]
        Open vertex list.

    Returns
    -------
    list[tuple[float, float]]
        The same vertices with the first appended.
    """
    return [*points, points[0]]


def _side_offset(side: str) -> tuple[float, float]:
    """
    Degree step toward a compass side.

    Parameters
    ----------
    side : str
        Sixteen-point compass token.

    Returns
    -------
    tuple[float, float]
        Latitude and longitude offsets in degrees.
    """
    bearing = math.radians(_DIR_DEG[side])
    return (
        _LINE_SIDE_OFFSET_DEG * math.cos(bearing),
        _LINE_SIDE_OFFSET_DEG * math.sin(bearing),
    )


def _offset_vertices(
    points: list[tuple[float, float]],
    *,
    half_width_deg: float,
) -> list[tuple[float, float]]:
    """
    Build a corridor ring around a centreline.

    Parameters
    ----------
    points : list[tuple[float, float]]
        Line vertices, at least two.
    half_width_deg : float
        Half-width in degrees of latitude.

    Returns
    -------
    list[tuple[float, float]]
        Closed ring around the line.
    """

    def _normal(start: tuple[float, float], end: tuple[float, float]) -> tuple[float, float]:
        """
        Perpendicular step from one vertex to the next.

        Parameters
        ----------
        start : tuple[float, float]
            Segment start, latitude then longitude.
        end : tuple[float, float]
            Segment end, latitude then longitude.

        Returns
        -------
        tuple[float, float]
            Latitude and longitude offsets of half the corridor width.
        """
        dlat = end[0] - start[0]
        dlon = end[1] - start[1]
        length = math.hypot(dlat, dlon) or 1.0
        return (-dlon / length * half_width_deg, dlat / length * half_width_deg)

    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    last = len(points) - 1
    for index, point in enumerate(points):
        if index == 0:
            north, east = _normal(points[0], points[1])
        elif index == last:
            north, east = _normal(points[-2], points[-1])
        else:
            first = _normal(points[index - 1], point)
            second = _normal(point, points[index + 1])
            north = (first[0] + second[0]) / 2
            east = (first[1] + second[1]) / 2
        left.append((point[0] + north, point[1] + east))
        right.append((point[0] - north, point[1] - east))
    return _close_ring(left + list(reversed(right)))


def _apply_line_geometry(ir: dict[str, Any], body: str) -> bool:
    """
    Record a line of coordinates as a surface ring.

    A stated width becomes a corridor. A compass side, such as ``E OF LINE``,
    becomes a thin ring on that side. The ring is the line, not the whole FIR.

    Parameters
    ----------
    ir : dict
        Hazard intermediate representation being filled.
    body : str
        SIGMET or AIRMET body text.

    Returns
    -------
    bool
        True when a line was found, including a line with too few vertices.
    """
    if re.search(r"\bLINE\b", body, re.IGNORECASE) is None:
        return False
    span = _LINE_SPAN.search(body)
    if span is None:  # pragma: no cover
        return True
    raw_points = [_point_lat_lon(match) for match in _POINT.finditer(span.group("body"))]
    if len(raw_points) < 2:
        return True
    width = _LINE_WIDTH.search(body)
    if width is not None:
        amount = int(width.group("width"))
        full_width_deg = amount / 111.195 if width.group("unit").upper() == "KM" else amount / 60.0
        ring = _offset_vertices(raw_points, half_width_deg=full_width_deg / 2)
    else:
        side_match = _LINE_SIDE.search(body)
        if side_match is None:
            ring = _offset_vertices(raw_points, half_width_deg=_LINE_SIDE_OFFSET_DEG)
        else:
            dlat, dlon = _side_offset(side_match.group("side").upper())
            offset = [(lat + dlat, lon + dlon) for lat, lon in raw_points]
            ring = _close_ring([*raw_points, *reversed(offset)])
    ir["geometry"] = {"kind": "polygon", "pos_list": _format_pos_list(ring)}
    return True


def _polygon_from_wi_body(wi_body: str) -> dict[str, Any] | None:
    """
    Internal helper ``_polygon_from_wi_body``.

    Parameters
    ----------
    wi_body : str
        Argument ``wi_body``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    pts = [_point_lat_lon(m) for m in _POINT.finditer(wi_body)]
    if len(pts) < 3:
        return None
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    pos_list = " ".join(f"{lat:.4f} {lon:.4f}" for lat, lon in pts)
    return {"kind": "polygon", "pos_list": pos_list}


def _parse_va_eruption(body: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_va_eruption``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    match = _VA_ERUPTION.search(body)
    if match is None:
        return None
    lat, lon = _point_lat_lon(match)
    return {"name": match.group("name").upper(), "lat": lat, "lon": lon}


def _parse_va_locations(body: str) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_va_locations``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
    locations: list[dict[str, Any]] = []
    for match in _VA_LOCATION.finditer(body):
        obs_geom = _polygon_from_wi_body(match.group("obs_wi"))
        if obs_geom is None:
            continue
        loc: dict[str, Any] = {
            "time_indicator": "OBSERVATION",
            "obs_hhmm": match.group("obs_hhmm"),
            "geometry": obs_geom,
            "intensity_change": _INTENSITY.get(
                (match.group("intensity") or "NC").upper(),
                "NO_CHANGE",
            ),
        }
        if match.group("sfc_fl"):
            fl_m = re.search(r"(\d{2,3})", match.group("sfc_fl"))
            if fl_m is not None:  # pragma: no branch — SFC/FLnnn always has digits
                loc["lower_surface"] = "SFC"
                loc["upper_fl"] = int(fl_m.group(1))
        elif match.group("lo") and match.group("hi"):
            loc["lower_fl"] = int(match.group("lo"))
            loc["upper_fl"] = int(match.group("hi"))
        fcst_wi = match.group("fcst_wi")
        if fcst_wi:
            fcst_geom = _polygon_from_wi_body(fcst_wi)
            if fcst_geom is not None:
                loc["forecast"] = {
                    "hhmm": match.group("fcst_hhmm"),
                    "geometry": fcst_geom,
                }
        locations.append(loc)
    return locations
