"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def convert(
    tac: str,
    *,
    product: str,
    profile: str = "annex3",
    iwxxm_version: str | None = None,
    preview: bool = False,
    emit_translation_centre: bool = False,
    translation_centre_designator: str = "",
    translation_centre_name: str = "",
    report_status: str | None = None,
    report_variant: str | None = None,
    propagate_residuals_to_remarks: bool | None = None,
    ir_source: str | None = None,
    bulletin_date: str | None = None,
) -> ConvertResult:
    """
    Convert a TAC report to IWXXM XML.

    Parameters
    ----------
    tac : str
        TAC text (single report or bulletin containing one report).

    product : str
        One of the F6 products or ``SWXA`` (F28).

    profile : str, optional
        ``annex3`` (default) or ``iwxxm_us`` (METAR/SPECI US extensions; others T5.4-T5.5).

    iwxxm_version : str | None, optional
        Target IWXXM release line.

    preview : bool, optional
        When ``True``, fatal parse/profile failures still return best-effort stub XML
        (soft-preview / ADR-022). Does not imply Schematron-passed publish.

    emit_translation_centre : bool, optional
        When ``True``, emit ``translationCentreDesignator`` / ``translationCentreName``
        on successful convert (cross-State / Translation Centre mode; FAQ §14.5).
        Default ``False`` omits them for in-State convert. Quarantine shells always
        include centre attrs (official ``*-translation-failed`` model).

    translation_centre_designator : str, optional
        Designator when ``emit_translation_centre`` is true.

    translation_centre_name : str, optional
        Human-readable centre name when ``emit_translation_centre`` is true.

    report_status : str | None, optional
        Optional IWXXM ``reportStatus`` override (``NORMAL`` / ``AMENDMENT`` /
        ``CORRECTION``). Used for AHL BBB→reportStatus when the TAC body has no
        COR/AMD keyword (EV-029 M2 / #823 B3). When omitted, emitters keep
        body-derived COR → CORRECTION behavior.

    propagate_residuals_to_remarks : bool | None, optional
        When ``True``, fold decode residual token text into the profile remarks /
        ``humanReadableText`` path (or document no XML target on annex3). When
        ``None``, use the semantic-profile default (annex3 / ICAO_2025 → off).

    ir_source : str | None, optional
        ``legacy``, ``pack``, or ``auto`` (default). ``auto`` uses pack IR for
        METAR/SPECI and legacy parsers for other products. Override with
        ``TAC2IWXXM_CONVERT_IR_SOURCE`` when omitted.

    bulletin_date : str | None, optional
        Optional ``YYYY-MM-DD`` (or a timestamp with that prefix) used as the
        year and month for TAC day stamps. Omitted conversions keep example
        pins such as ``2023-06`` and ``2012-08``.

    Returns
    -------
    ConvertResult
        Structured result with XML, IR, and issues.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (convert)
    2
    """
    product_u = product.upper()
    if product_u in {"METAR", "SPECI"}:
        tac = fold_observation_case(tac)
    requested_iwxxm_version = iwxxm_version or "2025-2"
    resolved = resolve_semantic_profile(profile)
    if resolved is None:
        profile_l = profile.lower()
        issue = ConvertIssue(
            severity="error",
            code="UNSUPPORTED_PROFILE",
            message=f"profile {profile_l!r} not supported yet",
        )
        xml = (
            _preview_stub_xml(
                product_u,
                requested_iwxxm_version,
                f"UNSUPPORTED_PROFILE: {issue.message}",
            )
            if preview
            else None
        )
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=requested_iwxxm_version,
            xml=xml,
            issues=[issue],
        )

    profile_l = resolved.emit_key
    semantic_profile = resolved.canonical
    deprecated_alias_used = resolved.alias_used
    heading = _heading_from_tac(tac)
    issued_at = datetime.now(UTC)
    issued_text = issued_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    bulletin_id = _compact_bulletin_id(heading) if heading is not None else None
    suggested_filename = (
        iwxxm_filename(heading, issued_at=issued_at, gzip=True)
        if heading is not None and profile_l != EMIT_CA_ECCC
        else None
    )
    do_propagate = resolve_propagate_residuals_to_remarks(profile_l, propagate_residuals_to_remarks)
    effective_iwxxm_version = (
        CA_IWXXM_VERSION
        if profile_l in {EMIT_CA_ECCC, EMIT_CA_MSC_SIGMET} and iwxxm_version is None
        else requested_iwxxm_version
    )

    def _fail(
        code: str,
        message: str,
        *,
        span: bool = False,
    ) -> ConvertResult:
        """
        Internal helper ``_fail``.

        Parameters
        ----------
        code : str
            Argument ``code``.

        message : str
            Argument ``message``.

        span : bool, optional
            Argument ``span``.

        Returns
        -------
        ConvertResult
            Return value.
        """
        span_start = span_end = None
        if span:
            span_start, span_end = _content_bounds(tac)
        issue = ConvertIssue(
            severity="error",
            code=code,
            message=message,
            start=span_start,
            end=span_end,
        )
        xml = _preview_stub_xml(product_u, effective_iwxxm_version, f"{code}: {message}") if preview else None
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=effective_iwxxm_version,
            semantic_profile=semantic_profile,
            deprecated_alias_used=deprecated_alias_used,
            xml=xml,
            issues=[issue],
        )

    if product_u not in _SUPPORTED_PRODUCTS:
        return _fail("UNSUPPORTED_PRODUCT", f"product {product_u!r} not supported yet")
    gated = products_for(profile_l)
    if gated is not None and product_u not in gated:
        return _fail(
            "UNSUPPORTED_PROFILE",
            f"profile {profile_l} not supported yet for product {product_u!r}",
        )
    supported_versions = supported_iwxxm_versions_for_profile(profile_l)
    if effective_iwxxm_version not in supported_versions:
        if profile_l == EMIT_CA_ECCC:
            message = f"profile ca_eccc requires iwxxm_version {CA_IWXXM_VERSION!r}, got {effective_iwxxm_version!r}"
        else:
            message = (
                f"profile {profile_l} supports iwxxm_version(s) {sorted(supported_versions)!r}, "
                f"got {effective_iwxxm_version!r}"
            )
        return _fail(
            "INVALID_IWXXM_VERSION",
            message,
        )
    if profile_l in _SOURCE_UNAVAILABLE:
        return _fail("SOURCE_UNAVAILABLE", _SOURCE_UNAVAILABLE[profile_l])
    if not preview:
        # TC-EVYFC-004 / D-YFC-05: fail-closed pin↔SCH (soft-preview waived).
        try:
            from iwxxm_validate.pin_sch import PinSchError, assert_pin_schematron_match
        except ImportError:
            # Optional workspace member missing in some install layouts — validate path still gates.
            pass
        else:
            try:
                assert_pin_schematron_match(effective_iwxxm_version)
            except PinSchError as exc:
                return _fail("PIN_SCH_MISMATCH", str(exc))
    resolved_report_variant: str | None = None
    if report_variant is not None and report_variant.strip():
        resolved_report_variant = report_variant.strip().upper()
        supported_variants = supported_report_variants_for_profile(profile_l, product_u)
        if not supported_variants:
            return _fail(
                "INVALID_REPORT_VARIANT",
                f"profile {profile_l} does not define report variants for product {product_u!r}",
            )
        if resolved_report_variant not in supported_variants:
            return _fail(
                "INVALID_REPORT_VARIANT",
                (
                    f"profile {profile_l} supports report_variant(s) {sorted(supported_variants)!r} "
                    f"for product {product_u!r}, got {resolved_report_variant!r}"
                ),
            )

    status_override: str | None = None
    if report_status is not None:
        status_override = report_status.strip().upper()
        if status_override not in _REPORT_STATUSES:
            return _fail(
                "INVALID_REPORT_STATUS",
                f"report_status {report_status!r} must be one of {sorted(_REPORT_STATUSES)}",
            )

    time_anchor: str | None = None
    if bulletin_date is not None and str(bulletin_date).strip():
        try:
            time_anchor = anchor_from_bulletin_date(str(bulletin_date))
        except ValueError:
            return _fail("INVALID_BULLETIN_DATE", "bulletin_date must be a calendar date (YYYY-MM-DD)")

    anchor_token = push_bulletin_anchor(time_anchor)
    propagate_issue: ConvertIssue | None = None
    try:
        if _UNRELIABLE_TAC.search(tac):
            raise ValueError("unreliable TAC marked INVALID - quarantine")
        try:
            source = resolve_ir_source(product_u, ir_source=ir_source)
        except ValueError as exc:
            return _fail("INVALID_IR_SOURCE", str(exc))
        ir = _parse_for_convert(
            product_u,
            tac,
            ir_source=source,
            iwxxm_version=effective_iwxxm_version,
            profile=profile_l,
            ir_source_explicit=_ir_source_is_explicit_pack(ir_source),
        )
        if time_anchor is not None:
            ir = {**ir, "time_anchor": time_anchor}
        if resolved_report_variant is not None and profile_l == EMIT_CA_ECCC and product_u == "METAR":
            ir = {**ir, "ca_iwxxm_root": resolved_report_variant}
        if status_override is not None:
            ir = {**ir, "report_status": status_override}
        if do_propagate:
            ir, propagate_issue = _apply_propagate_residuals(
                tac,
                product=product_u,
                profile_l=profile_l,
                ir=ir,
            )
        if profile_l == EMIT_US_NWS_CONVECTIVE_SIGMET:
            if not ir.get("convective"):
                return _fail(
                    "NOT_CONVECTIVE_SIGMET",
                    "This profile converts United States convective SIGMET text, not an international SIGMET.",
                )
            xml = _emit(product_u, EMIT_IWXXM_US, ir, effective_iwxxm_version)
        else:
            xml = _emit(product_u, profile_l, ir, effective_iwxxm_version)
    except ImpossibleTacDay as exc:
        return _fail("IMPOSSIBLE_TAC_DAY", str(exc))
    except UnknownVOR as exc:
        return _fail("PARSE_ERROR", f"unknown VOR reference {exc}", span=True)
    except ValueError as exc:
        message = str(exc)
        if preview:
            return _fail("PARSE_ERROR", message, span=True)
        # Structural SIGMET/AIRMET defects fail closed — do not soft-succeed a
        # quarantine shell that could still invent TS or inverted validPeriod.
        hard_fail_markers = (
            "missing phenomenon",
            "incomplete CNL",
            "valid period end must be after begin",
            "coordinate out of range",
        )
        if any(marker in message for marker in hard_fail_markers):
            return _fail("PARSE_ERROR", message, span=True)
        if _should_quarantine(tac, product_u):
            span_start, span_end = _content_bounds(tac)
            quarantine_xml = _quarantine_xml(
                product_u,
                tac.strip(),
                effective_iwxxm_version,
                bulletin_id=bulletin_id,
                centre_designator=translation_centre_designator or None,
                centre_name=translation_centre_name or None,
            )
            return ConvertResult(
                ok=True,
                product=product_u,
                profile=profile_l,
                iwxxm_version=effective_iwxxm_version,
                semantic_profile=semantic_profile,
                deprecated_alias_used=deprecated_alias_used,
                xml=quarantine_xml,
                xml_gzip=_xml_gzip(quarantine_xml, suggested_filename),
                suggested_filename=suggested_filename,
                issues=[
                    ConvertIssue(
                        severity="warning",
                        code="TRANSLATION_FAILED",
                        message=message,
                        start=span_start,
                        end=span_end,
                    )
                ],
            )
        return _fail("PARSE_ERROR", message, span=True)
    finally:
        pop_bulletin_anchor(anchor_token)

    issues: list[ConvertIssue] = []
    # Alias resolution remains server-side; do not surface DEPRECATED_PROFILE_ALIAS
    # to operators (EV-beta-ux-export-auth / D-EV-beta-05).
    if propagate_issue is not None:
        issues.append(propagate_issue)
    # Pipeline overlay: decode residuals → TAC warning (ADR-054 ladder; live-eval map).
    decoded_for_partial = decode_tac(tac, product=product_u)
    residual_spans = [r for r in decoded_for_partial.residuals if r.text and r.text.strip()]
    if residual_spans:
        first = residual_spans[0]
        issues.append(
            ConvertIssue(
                severity="warning",
                code="PARTIAL_DECODE",
                message=("Some TAC tokens were not decoded (partial decode); conversion may still succeed"),
                location="decode",
                start=first.start,
                end=residual_spans[-1].end,
            )
        )
    # D-EV087-inter-emit / national remark provenance (AU INTER, TAF3, NZ domestic extras).
    national_tokens = ir.get("national_remark_tokens")
    if isinstance(national_tokens, list) and national_tokens:
        joined = ", ".join(str(t) for t in cast(list[object], national_tokens))
        issues.append(
            ConvertIssue(
                severity="info",
                code="NATIONAL_TAC_PROVENANCE",
                message=(
                    f"National TAC tokens preserved for diagnostics/remarks "
                    f"(IWXXM core has no dedicated enum): {joined}"
                ),
                location="remarks",
            )
        )
    if profile_l == EMIT_ANNEX3 and product_u in {"METAR", "SPECI"} and ir.get("remarks_present"):
        rmk_match = _RMK_TOKEN.search(tac)
        issues.append(
            ConvertIssue(
                severity="info",
                code="REMARKS_EXCLUDED",
                message="Remarks after RMK stay out of the international report.",
                location="remarks",
                start=rmk_match.start() if rmk_match else None,
                end=rmk_match.end() if rmk_match else None,
            )
        )
    if profile_l in {EMIT_CA_ECCC, EMIT_IWXXM_US}:
        raw_remarks: object = ir.get("remark_issues")
        if isinstance(raw_remarks, list):
            for item in cast(list[object], raw_remarks):
                message = str(item)
                remark_start, remark_end = _remark_span(tac, message)
                issues.append(
                    ConvertIssue(
                        severity="warning",
                        code="MALFORMED_REMARKS",
                        message=message,
                        location="remarks",
                        start=remark_start,
                        end=remark_end,
                    )
                )

    if profile_l == EMIT_CA_ECCC:
        if not translation_centre_designator:
            translation_centre_designator, translation_centre_name = default_ca_translation_centre()
        emit_translation_centre = True

    if emit_translation_centre:
        # METAR/SPECI: translationTime attrs match observationTime (TAC stamp), not wall clock.
        translation_stamp = issued_text
        if product_u in {"METAR", "SPECI"}:
            translation_stamp = obs_timestamp(ir)
        xml = _inject_translation_centre(
            xml,
            designator=translation_centre_designator,
            name=translation_centre_name,
            heading=(bulletin_id, translation_stamp) if bulletin_id is not None else None,
        )

    xml = _apply_permissible_usage(xml, tac)

    return ConvertResult(
        ok=True,
        product=product_u,
        profile=profile_l,
        iwxxm_version=effective_iwxxm_version,
        semantic_profile=semantic_profile,
        deprecated_alias_used=deprecated_alias_used,
        xml=xml,
        xml_gzip=_xml_gzip(xml, suggested_filename),
        ir=ir,
        issues=issues,
        suggested_filename=suggested_filename,
    )
