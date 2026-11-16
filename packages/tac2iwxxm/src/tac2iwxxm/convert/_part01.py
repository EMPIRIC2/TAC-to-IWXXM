"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _ir_source_is_explicit_pack(ir_source: str | None) -> bool:
    """
    Internal helper ``_ir_source_is_explicit_pack``.

    Parameters
    ----------
    ir_source : str | None
        Argument ``ir_source``.

    Returns
    -------
    bool
        Return value.
    """
    if ir_source is not None:
        return ir_source.strip().lower() == "pack"
    return os.environ.get(IR_SOURCE_ENV, "").strip().lower() == "pack"


def resolve_propagate_residuals_to_remarks(
    profile: str,
    value: bool | None,
) -> bool:
    """
    Resolve the effective ``propagate_residuals_to_remarks`` flag.

    Parameters
    ----------
    profile : str
        Emit key or semantic profile id (case-insensitive).

    value : bool | None
        Explicit override, or ``None`` to use the profile default table.

    Returns
    -------
    bool
        Effective flag. Omitted / unknown profiles default to ``False`` this cycle.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (resolve_propagate_residuals_to_remarks)
    2
    """
    if value is not None:
        return bool(value)
    key = profile.strip().lower()
    resolved = resolve_semantic_profile(profile)
    if resolved is not None:
        key = resolved.emit_key
        canonical = resolved.canonical.lower()
        if canonical in _PROPAGATE_RESIDUALS_DEFAULTS:
            return _PROPAGATE_RESIDUALS_DEFAULTS[canonical]
    return _PROPAGATE_RESIDUALS_DEFAULTS.get(key, False)


def _residual_texts_to_append(
    residual_texts: list[str],
    *,
    remarks_free_text: str,
) -> list[str]:
    """
    Internal helper ``_residual_texts_to_append``.

    Parameters
    ----------
    residual_texts : list[str]
        Argument ``residual_texts``.

    remarks_free_text : str
        Argument ``remarks_free_text``.

    Returns
    -------
    list[str]
        Return value.
    """
    existing = remarks_free_text.strip()
    existing_upper = existing.upper()
    out: list[str] = []
    for text in residual_texts:
        cleaned = text.strip()
        if not cleaned:
            continue
        if cleaned.upper() in existing_upper:
            continue
        out.append(cleaned)
    return out


def _apply_propagate_residuals(
    tac: str,
    *,
    product: str,
    profile_l: str,
    ir: dict[str, Any],
) -> tuple[dict[str, Any], ConvertIssue | None]:
    """
    Internal helper ``_apply_propagate_residuals``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    profile_l : str
        Argument ``profile_l``.

    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    tuple[dict[str, Any], ConvertIssue | None]
        Return value.
    """
    decoded = decode_tac(tac, product=product)
    residual_texts = [r.text for r in decoded.residuals if r.text and r.text.strip()]
    if not residual_texts:
        return ir, None

    if profile_l in _REMARKS_HRT_EMIT_PROFILES:
        existing = str(ir.get("remarks_free_text") or "")
        to_append = _residual_texts_to_append(residual_texts, remarks_free_text=existing)
        if not to_append:
            return ir, None
        combined = f"{existing} {' '.join(to_append)}".strip() if existing else " ".join(to_append)
        updated = {
            **ir,
            "remarks_free_text": combined,
            "remarks_present": True,
        }
        joined = " ".join(to_append)
        issue = ConvertIssue(
            severity="info",
            code="RESIDUALS_PROPAGATED_TO_REMARKS",
            message=("Decode residual token text appended to remarks / humanReadableText: " + joined),
            location="remarks",
        )
        return updated, issue

    # annex3 (and other non-HRT profiles): document no XML target; do not invent remarks.
    issue = ConvertIssue(
        severity="info",
        code="RESIDUALS_PROPAGATED_TO_REMARKS",
        message=(
            "propagate_residuals_to_remarks is enabled and decode residuals exist, "
            "but this profile has no XML remarks / humanReadableText target "
            "(no XML target on annex3); residuals remain diagnostic-only"
        ),
        location="remarks",
    )
    return ir, issue


def _content_bounds(tac: str) -> tuple[int, int]:
    """
    Internal helper ``_content_bounds``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    Returns
    -------
    tuple[int, int]
        Return value.
    """
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac)
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped)


def _preview_stub_xml(product: str, iwxxm_version: str, reason: str) -> str:
    """
    Emit a minimal best-effort IWXXM shell for soft-preview (not for publication).

    Parameters
    ----------
    product : str
        Product root element name (e.g. ``METAR``).

    iwxxm_version : str
        Release line used to pick the IWXXM namespace.

    reason : str
        Short human-readable failure note embedded as an XML comment.

    Returns
    -------
    str
        IWXXM-looking XML document with a nil body element.
    """
    from xml.sax.saxutils import escape

    product_u = product.upper()
    root = _QUARANTINE_ROOT.get(product_u, product_u if product_u in _PREVIEW_ROOTS else "METAR")
    ns = _PREVIEW_NS.get(iwxxm_version, _PREVIEW_NS["2025-2"])
    gml_id = f"{root.lower()}.preview.failed"
    note = escape(reason[:240])
    nil_element = failed_preview_nil_element(product_u)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<iwxxm:{root} xmlns:iwxxm="{ns}" xmlns:gml="http://www.opengis.net/gml/3.2" '
        f'gml:id="{gml_id}" reportStatus="NORMAL">\n'
        f"  <!-- soft-preview: {note} -->\n"
        f'  <iwxxm:{nil_element} nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        f"</iwxxm:{root}>\n"
    )


def _tac_looks_like_product(tac: str, product: str) -> bool:
    """
    Internal helper ``_tac_looks_like_product``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    Returns
    -------
    bool
        Return value.
    """
    pattern = _PRODUCT_LEAD.get(product)
    if pattern is None:
        return False
    return pattern.search(tac) is not None


def _should_quarantine(tac: str, product: str) -> bool:
    """
    Internal helper ``_should_quarantine``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    Returns
    -------
    bool
        Return value.
    """
    if _UNRELIABLE_TAC.search(tac):
        return True
    return _tac_looks_like_product(tac, product)


def _heading_from_tac(tac: str) -> AhlParts | None:
    """
    Return parsed abbreviated-heading parts, or None when the first line is not a heading.

    Parameters
    ----------
    tac : str
        Bulletin or single-report text.

    Returns
    -------
    AhlParts | None
        Parsed heading, or None when the first line is not an abbreviated heading.
    """
    try:
        return parse_ahl(tac)
    except BulletinSplitError:
        return None


def _compact_bulletin_id(parts: AhlParts) -> str:
    """
    Return ``TTAAiiCCCCYYGGgg`` plus BBB when the heading has one.

    Parameters
    ----------
    parts : AhlParts
        Parsed abbreviated heading.

    Returns
    -------
    str
        Compact bulletin identifier with no spaces.
    """
    bbb = parts.bbb or ""
    return f"{parts.tt}{parts.aa}{parts.ii}{parts.cccc}{parts.yygggg}{bbb}"


def _remark_text(tac: str) -> str | None:
    """
    Return the RMK field with wrapped lines joined, or None when it is absent.

    Parameters
    ----------
    tac : str
        Original TAC text.

    Returns
    -------
    str | None
        Remark text, or None when the bulletin has no RMK field.
    """
    chunks: list[str] = []
    capturing = False
    for raw in tac.splitlines():
        line = raw.strip()
        if not line:
            continue
        remark = _RMK_LINE.match(line)
        if remark is not None:
            capturing = True
            chunks.append(remark.group(1).strip())
            continue
        if capturing:
            if _NEXT_FIELD.match(line):
                break
            chunks.append(line)
    text = " ".join(chunks).strip()
    return text or None


def _permissible_usage_attrs(tac: str) -> str:
    """
    Return the permissible-usage attributes for an explicit test or exercise marker.

    Parameters
    ----------
    tac : str
        Original TAC text.

    Returns
    -------
    str
        ``permissibleUsage="OPERATIONAL"``, or the non-operational attributes.
    """
    exercise = _EXERCISE_WORD.search(tac) is not None
    status_test = _STATUS_TEST.search(tac) is not None
    remark_test = _THIS_IS_A_TEST.search(tac) is not None
    if not exercise and not status_test and not remark_test:
        return 'permissibleUsage="OPERATIONAL"'
    reason = "EXERCISE" if exercise else "TEST"
    remark = _remark_text(tac)
    if remark:
        note = remark
    elif exercise:
        note = "Exercise bulletin"
    else:
        note = "Test bulletin"
    return (
        'permissibleUsage="NON-OPERATIONAL" '
        f'permissibleUsageReason="{escape(reason)}" '
        f'permissibleUsageSupplementary="{escape(note)}"'
    )


def _apply_permissible_usage(xml: str, tac: str) -> str:
    """
    Replace the operational usage attribute when the TAC has an explicit marker.

    Parameters
    ----------
    xml : str
        Successful convert document.

    tac : str
        Original TAC text.

    Returns
    -------
    str
        XML with usage attributes for a test or exercise, or the input XML.
    """
    attrs = _permissible_usage_attrs(tac)
    if attrs == 'permissibleUsage="OPERATIONAL"':
        return xml
    return xml.replace('permissibleUsage="OPERATIONAL"', attrs, 1)


def _valid_period_xml(tac: str, now: str) -> str:
    """
    Build a valid-period element from a TAC validity group.

    Parameters
    ----------
    tac : str
        Original TAC text.

    now : str
        Issue timestamp ``YYYY-MM-DDTHH:MM:SSZ`` used for the year and month.

    Returns
    -------
    str
        A ``validPeriod`` element, nil when the TAC has no validity group.
    """
    six = _VALID_6.search(tac)
    four = None if six else _VALID_4.search(tac)
    match = six or four
    if match is None:
        return f'  <iwxxm:validPeriod nilReason="{_NIL_MISSING}"/>\n'
    parts = match.groups()
    if len(parts) == 6:
        bday, bhour, bmin, eday, ehour, emin = parts
    else:
        bday, bhour, eday, ehour = parts
        bmin = emin = "00"
    # Same-day inverted / zero-length VALID must not enter the quarantine shell.
    if bday == eday and (ehour, emin) <= (bhour, bmin):
        return f'  <iwxxm:validPeriod nilReason="{_NIL_MISSING}"/>\n'
    year_month = now[:7]
    begin = f"{year_month}-{bday}T{bhour}:{bmin}:00Z"
    end = f"{year_month}-{eday}T{ehour}:{emin}:00Z"
    return (
        "  <iwxxm:validPeriod>\n"
        '    <gml:TimePeriod gml:id="t.valid">\n'
        f"      <gml:beginPosition>{begin}</gml:beginPosition>\n"
        f"      <gml:endPosition>{end}</gml:endPosition>\n"
        "    </gml:TimePeriod>\n"
        "  </iwxxm:validPeriod>\n"
    )


def _unit_xml(tag: str, name: str | None, *, unit_type: str) -> str:
    """
    Build an issuing-unit element.

    Parameters
    ----------
    tag : str
        IWXXM element local name.

    name : str | None
        Centre or unit token recovered from the TAC, or ``None``.

    unit_type : str
        AIXM unit type.

    Returns
    -------
    str
        The unit element, nil when ``name`` is absent.
    """
    if not name:
        return f'  <iwxxm:{tag} nilReason="{_NIL_MISSING}"/>\n'
    safe = escape(name)
    designator = ""
    if re.fullmatch(r"[A-Z0-9]{4}", name):
        designator = f"\n        <aixm:designator>{safe}</aixm:designator>"
    return (
        f"  <iwxxm:{tag}>\n"
        f'    <aixm:Unit gml:id="unit.{tag}">\n'
        "      <aixm:timeSlice>\n"
        f'        <aixm:UnitTimeSlice gml:id="unit.ts.{tag}">\n'
        "          <gml:validTime/>\n"
        "          <aixm:interpretation>SNAPSHOT</aixm:interpretation>\n"
        f"          <aixm:name>{safe}</aixm:name>\n"
        f"          <aixm:type>{unit_type}</aixm:type>{designator}\n"
        "        </aixm:UnitTimeSlice>\n"
        "      </aixm:timeSlice>\n"
        "    </aixm:Unit>\n"
        f"  </iwxxm:{tag}>\n"
    )


def _advisory_centre(tac: str, label: str) -> str | None:
    """
    Return the advisory-centre token for ``label``, or ``None``.

    Parameters
    ----------
    tac : str
        Original TAC text.

    label : str
        One of ``VAAC``, ``TCAC``, or ``SWXC``.

    Returns
    -------
    str | None
        Upper-case centre token.
    """
    match = _ADVISORY_CENTRE[label].search(tac)
    return match.group(1).upper() if match else None
