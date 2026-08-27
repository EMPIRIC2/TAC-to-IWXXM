"""Product rules — sigmet_airmet."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *


def _count_families(text: str, families: tuple[tuple[str, re.Pattern[str]], ...]) -> list[str]:
    found: list[str] = []
    for name, pattern in families:
        if pattern.search(text):
            found.append(name)
    return found


def _check_sigmet_g1(*, start: int, end: int, upper: str) -> list[Issue]:
    """F23 theme G1 — CNL / COR / STNR / geometry / single-alt / TOP ABV|BLW."""
    # ruff: noqa: F403, F405
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_COR.search(core):
        _emit_token_info(
            issues,
            code="INVALID_SIGMET_COR",
            message="SIGMET must not use COR (cancel + re-issue) — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token="COR",
        )

    if _SIGMET_CNL.search(core):
        # Cancel reports omit phenomenon/analysis (Guidance AIRMET/SIGMET CNL).
        hit = _count_families(core, _SIGMET_FAMILIES)
        if hit:
            _emit_token_info(
                issues,
                code="INVALID_SIGMET_CNL",
                message="SIGMET CNL must omit phenomenon/analysis body — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
        else:
            _emit_token_info(
                issues,
                code="SIGMET_CNL",
                message="SIGMET CNL cancel report — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
            if _SIGMET_CNL_FIR_MOVED.search(core):
                _emit_token_info(
                    issues,
                    code="VA_CNL_FIR_MOVED",
                    message="VA SIGMET CNL identifies FIR to which ash has moved — research V1",
                    core=core,
                    body_start=start,
                    body_end=end,
                    token="FIR",
                )
        return issues

    if _SIGMET_STNR.search(core):
        if _SIGMET_MOV.search(core):
            _emit_token_info(
                issues,
                code="INVALID_STNR_MOVEMENT",
                message="SIGMET STNR conflicts with MOV — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )
        else:
            _emit_token_info(
                issues,
                code="STNR_MOVEMENT",
                message="SIGMET STNR stationary movement — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )

    if _SIGMET_WI.search(core):
        _emit_token_info(
            issues,
            code="POLYGON_LOCATION",
            message="SIGMET polygon/line WI geometry — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token="WI",
        )
    elif _SIGMET_POINT_COORD.search(core):
        m = _SIGMET_POINT_COORD.search(core)
        assert m is not None
        _emit_token_info(
            issues,
            code="POINT_LOCATION",
            message=("SIGMET single-point location (encode CircleByCenterPoint r=0) — research G1"),
            core=core,
            body_start=start,
            body_end=end,
            token=m.group(0).split()[0],
        )

    if _SIGMET_TOP_ABV_BLW.search(core):
        _emit_token_info(
            issues,
            code="TOP_ABV_OR_BLW",
            message="SIGMET TOP ABV/BLW level grammar — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token="TOP",
        )
    elif not _SIGMET_LEVEL_RANGE.search(core) and _SIGMET_SINGLE_LEVEL.search(core):
        m = _SIGMET_SINGLE_LEVEL.search(core)
        assert m is not None
        _emit_token_info(
            issues,
            code="SINGLE_ALTITUDE",
            message="SIGMET single altitude (same lower/upper) — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token=m.group(0),
        )

    return issues


def _sigmet_validity_hours(start: str, end: str) -> float | None:
    """Return VALID period length in hours (coarse midnight/month wrap)."""
    if len(start) != 6 or len(end) != 6 or not start.isdigit() or not end.isdigit():
        return None
    sd, sh, sm = int(start[:2]), int(start[2:4]), int(start[4:6])
    ed, eh, em = int(end[:2]), int(end[2:4]), int(end[4:6])
    if not (1 <= sd <= 31 and 1 <= ed <= 31 and sh < 24 and eh < 24 and sm < 60 and em < 60):
        return None
    start_m = sd * 24 * 60 + sh * 60 + sm
    end_m = ed * 24 * 60 + eh * 60 + em
    if end_m < start_m:
        # Day/month wrap (e.g. 312200/010200) — add one 31-day month bucket.
        end_m += 31 * 24 * 60
    return (end_m - start_m) / 60.0


def _check_sigmet_g2(
    *,
    start: int,
    end: int,
    upper: str,
    is_va: bool = False,
    is_tc: bool = False,
) -> list[Issue]:
    """F23 theme G2 — sequence / validity duration / FIR / OBS·FCST / intensity."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    seq = _SIGMET_SEQ.search(core)
    if seq is not None:
        _emit_token_info(
            issues,
            code="SIGMET_SEQUENCE",
            message="SIGMET sequence number present — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=seq.group(1),
        )
    elif _SIGMET_NO_SEQ.search(core):
        _emit_token_info(
            issues,
            code="MISSING_SEQUENCE",
            message="SIGMET missing sequence number after SIGMET — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token="SIGMET",
        )

    valid = _SIGMET_VALID_PAIR.search(core)
    if valid is not None:
        hours = _sigmet_validity_hours(valid.group(1), valid.group(2))
        if is_va:
            max_hours = _WV_MAX_VALIDITY_HOURS
            label = "6 hours (WV)"
        elif is_tc:
            max_hours = _WC_MAX_VALIDITY_HOURS
            label = "6 hours (WC)"
        else:
            max_hours = _WS_MAX_VALIDITY_HOURS
            label = "4 hours (WS)"
        if hours is not None and hours > max_hours:
            _emit_token_info(
                issues,
                code="INVALID_VALIDITY_DURATION",
                message=f"SIGMET VALID period exceeds {label} — research G2",
                core=core,
                body_start=start,
                body_end=end,
                token="VALID",
            )

    fir = _SIGMET_FIR_CTA.search(core)
    if fir is not None:
        _emit_token_info(
            issues,
            code="FIR_OR_CTA",
            message="SIGMET FIR/CTA/UIR airspace identity — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=fir.group(0).split("/")[0],
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_FIR_OR_CTA",
            message="SIGMET missing FIR/CTA/UIR airspace identity — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token="SIGMET",
        )

    obs = _SIGMET_OBS_FCST.search(core)
    if obs is not None:
        _emit_token_info(
            issues,
            code="OBS_OR_FCST",
            message="SIGMET OBS or FCST analysis — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=obs.group(0),
        )
    elif not _SIGMET_NO_VA_EXP.search(core):
        _emit_token_info(
            issues,
            code="MISSING_OBS_OR_FCST",
            message="SIGMET missing OBS or FCST — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token="SIGMET",
        )

    intensity = _SIGMET_INTENSITY.search(core)
    if intensity is not None:
        _emit_token_info(
            issues,
            code="INTENSITY_CHANGE",
            message="SIGMET intensity change INTSF/WKN/NC — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=intensity.group(0),
        )

    return issues


def _check_airmet_a1(*, start: int, end: int, upper: str) -> list[Issue]:
    """F24 theme A1 — AIRMET sequence number + FIR/CTA identity."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    seq = _AIRMET_SEQ.search(core)
    if seq is not None:
        _emit_token_info(
            issues,
            code="SIGMET_SEQUENCE",
            message="AIRMET sequence number present — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token=seq.group(1),
        )
    elif _AIRMET_NO_SEQ.search(core):
        _emit_token_info(
            issues,
            code="MISSING_SEQUENCE",
            message="AIRMET missing sequence number after AIRMET — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    fir = _SIGMET_FIR_CTA.search(core)
    if fir is not None:
        _emit_token_info(
            issues,
            code="FIR_OR_CTA",
            message="AIRMET FIR/CTA/UIR airspace identity — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token=fir.group(0).split("/")[0],
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_FIR_OR_CTA",
            message="AIRMET missing FIR/CTA/UIR airspace identity — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    return issues


def _check_airmet_a2(*, start: int, end: int, upper: str) -> list[Issue]:
    """F24 theme A2 — AIRMET phenomenon modifiers (OBS/STNR/WKN/TOP ABV)."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_STNR.search(core):
        if _SIGMET_MOV.search(core):
            _emit_token_info(
                issues,
                code="INVALID_STNR_MOVEMENT",
                message="AIRMET STNR conflicts with MOV — F24 theme A2",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )
        else:
            _emit_token_info(
                issues,
                code="STNR_MOVEMENT",
                message="AIRMET STNR stationary movement — F24 theme A2",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )

    if _SIGMET_TOP_ABV_BLW.search(core):
        _emit_token_info(
            issues,
            code="TOP_ABV_OR_BLW",
            message="AIRMET TOP ABV/BLW level grammar — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token="TOP",
        )

    obs = _SIGMET_OBS_FCST.search(core)
    if obs is not None:
        _emit_token_info(
            issues,
            code="OBS_OR_FCST",
            message="AIRMET OBS or FCST analysis — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token=obs.group(0),
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_OBS_OR_FCST",
            message="AIRMET missing OBS or FCST — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    intensity = _SIGMET_INTENSITY.search(core)
    if intensity is not None:
        _emit_token_info(
            issues,
            code="INTENSITY_CHANGE",
            message="AIRMET intensity change INTSF/WKN/NC — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token=intensity.group(0),
        )

    return issues


def _check_sigmet_v1(*, start: int, end: int, upper: str) -> list[Issue]:
    """F23 theme V1 — VA volcano identity / ash geometry / NO VA EXP / CNL FIR-moved."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_NO_VA_EXP.search(core):
        if _SIGMET_VA_CLD.search(core):
            _emit_token_info(
                issues,
                code="INVALID_NO_VA_EXP",
                message="VA SIGMET NO VA EXP must not include VA CLD body — research V1",
                core=core,
                body_start=start,
                body_end=end,
                token="NO",
            )
        else:
            _emit_token_info(
                issues,
                code="NO_VA_EXP",
                message="VA SIGMET NO VA EXP absence token — research V1",
                core=core,
                body_start=start,
                body_end=end,
                token="NO",
            )

    if not _SIGMET_VA_TOKEN.search(core):
        return issues

    # Volcano identity required for active VA (including NO VA EXP with volcano named).
    if _SIGMET_VA_VOLCANO.search(core):
        _emit_token_info(
            issues,
            code="VA_VOLCANO_IDENTITY",
            message="VA SIGMET erupting volcano identity (MT/PSN) — research V1",
            core=core,
            body_start=start,
            body_end=end,
            token="MT",
        )
    elif not _SIGMET_CNL.search(core):
        _emit_token_info(
            issues,
            code="MISSING_VA_VOLCANO",
            message="VA SIGMET missing volcano identity (MT … PSN) — research V1",
            core=core,
            body_start=start,
            body_end=end,
            token="VA",
        )

    if _SIGMET_VA_CLD.search(core) and (_SIGMET_WI.search(core) or _SIGMET_POINT_COORD.search(core)):
        _emit_token_info(
            issues,
            code="VA_ASH_GEOMETRY",
            message="VA SIGMET ash cloud geometry / forecast position — research V1",
            core=core,
            body_start=start,
            body_end=end,
            token="VA",
        )

    return issues


def _check_sigmet_tc(*, start: int, end: int, upper: str) -> list[Issue]:
    """EV-030 theme TC — cyclone identity / OF TC CENTRE geometry (#829)."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    has_identity = _SIGMET_TC_IDENTITY.search(core) is not None
    has_of_centre = _SIGMET_OF_TC_CENTRE.search(core) is not None
    has_tc_name = _SIGMET_TC_NAME.search(core) is not None
    # TC family cue: named TC, OF TC CENTRE, or bare TC token (shared with G2 is_tc).
    if not (has_identity or has_of_centre or has_tc_name or _SIGMET_TC_TOKEN.search(core)):
        return issues

    if has_identity:
        _emit_token_info(
            issues,
            code="TC_CYCLONE_IDENTITY",
            message="TC SIGMET tropical cyclone identity (TC … PSN) — #829 / TC-EV030-004",
            core=core,
            body_start=start,
            body_end=end,
            token="TC",
        )
    elif has_of_centre or has_tc_name:
        _emit_token_info(
            issues,
            code="MISSING_TC_IDENTITY",
            message="TC SIGMET missing cyclone identity (TC … PSN) — #829 / TC-EV030-004",
            core=core,
            body_start=start,
            body_end=end,
            token="TC",
        )

    if has_of_centre and _SIGMET_WI.search(core):
        _emit_token_info(
            issues,
            code="TC_CB_GEOMETRY",
            message="TC SIGMET CB geometry WI … OF TC CENTRE — #829 / TC-EV030-004",
            core=core,
            body_start=start,
            body_end=end,
            token="TC",
        )

    return issues


def _check_sigmet_airmet(tac: str, product: str, *, profile: str = "annex3") -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    core = upper[:-1] if upper.endswith("=") else upper
    issues: list[Issue] = []
    # F23 theme C1 — one IWXXM report per TAC report (shared with METAR/SPECI/TAF).
    issues.extend(_check_c1_multi_report(tac, product))

    if not _VALID_PERIOD.search(upper):
        issues.append(
            _issue(
                "MISSING_VALID",
                f"{product} missing VALID ddhhmm/ddhhmm period — A6 identity",
                start=start,
                end=end,
                location="valid",
            )
        )

    if product == "SIGMET":
        issues.extend(_check_sigmet_g1(start=start, end=end, upper=upper))
        # CNL reports intentionally omit phenomenon — skip multi-family + G2 body gates.
        if _SIGMET_CNL.search(upper[:-1] if upper.endswith("=") else upper):
            return issues
        is_va = bool(_SIGMET_VA_TOKEN.search(upper))
        is_tc = bool(_SIGMET_TC_TOKEN.search(upper))
        issues.extend(_check_sigmet_g2(start=start, end=end, upper=upper, is_va=is_va, is_tc=is_tc))
        if is_va:
            issues.extend(_check_sigmet_v1(start=start, end=end, upper=upper))
        if is_tc and not is_va:
            issues.extend(_check_sigmet_tc(start=start, end=end, upper=upper))
    elif product == "AIRMET":
        # F24 theme A1 — sequence + FIR (CNL still needs identity; skip multi-family below).
        issues.extend(_check_airmet_a1(start=start, end=end, upper=upper))
        if _SIGMET_CNL.search(upper[:-1] if upper.endswith("=") else upper):
            return issues
        # F24 theme A2 — OBS/STNR/intensity/TOP ABV (phenomenon families below).
        issues.extend(_check_airmet_a2(start=start, end=end, upper=upper))
        issues.extend(
            _check_ca_gfa_airmet(
                product=product,
                core=core,
                body_start=start,
                body_end=end,
                profile=profile,
            )
        )

    families = _SIGMET_FAMILIES if product == "SIGMET" else _AIRMET_FAMILIES
    hit = _count_families(upper, families)
    if len(hit) > 1:
        issues.append(
            _issue(
                "MULTIPLE_PHENOMENA",
                f"{product} encodes multiple phenomenon families {hit} — A6 one-phenomenon gate",
                start=start,
                end=end,
                location="phenomenon",
            )
        )

    # EV-050 — AirWx/SigWx register membership (underscore↔space normalize).
    issues.extend(_check_phenomenon_membership(upper, product=product, start=start, end=end))

    return issues
