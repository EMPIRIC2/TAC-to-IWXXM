"""Product rules - metar_speci."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *
from tac_validate.theme_checks import (
    lint_profile,
    r1_identity_order,
    r3_weather,
    r4_cloud,
    r5_remarks,
    r8_modifiers,
    r8_nil_gate,
)


def _check_metar_speci(tac: str, product: str, *, profile: str = "annex3") -> list[Issue]:
    """Internal helper ``_check_metar_speci``."""
    start, end, body = _body_span(tac)
    upper = body.upper()
    # Drop trailing '=' for token scans.
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []
    issues.extend(_check_c1_multi_report(tac, product))

    from tac_validate.detectors import detector_mode, run_r2_visibility_detectors, run_theme_pack

    mode = detector_mode()
    use_detectors = mode != "legacy"
    profile_token = lint_profile.set(profile)
    try:
        # R8 NIL: short-circuit body checklist when NIL is the report content.
        if "NIL" in tokens:
            if use_detectors:
                issues.extend(run_theme_pack("metar-speci-r8-modifiers", tac, product))
            else:
                nil_issues = r8_nil_gate(tac, product) or []
                issues.extend(nil_issues)
            return issues

        if use_detectors:
            issues.extend(run_theme_pack("metar-speci-r1-identity-order", tac, product))
        else:
            issues.extend(r1_identity_order(tac, product))

        wind_tokens = [t for t in tokens if t == "CALM" or t.endswith(("KT", "MPS"))]
        has_good_wind = any(_WIND.fullmatch(t) for t in wind_tokens)
        if not has_good_wind and not wind_tokens:
            issues.append(
                _issue(
                    "MISSING_WIND",
                    f"{product} missing surface wind group - A3-2 #5",
                    start=start,
                    end=end,
                    location="wind",
                )
            )

        # ADR-046 M2/M3: R2 via detector pack by default; legacy keeps inline path for compares.
        if use_detectors:
            issues.extend(run_r2_visibility_detectors(tac, product))
        else:
            rmk_at = core.find("RMK")
            vis_core = core[:rmk_at] if rmk_at >= 0 else core
            vis_core = "\n".join(line for line in vis_core.splitlines() if not _AHL_HEADING_LINE.match(line.strip()))
            bad_vis = list(_VIS_BAD.finditer(vis_core))
            if bad_vis:
                issues.extend(
                    _issue(
                        "INVALID_VISIBILITY",
                        f"{product} invalid visibility token {match.group(1)!r} - research R2",
                        start=start + match.start(1),
                        end=start + match.end(1),
                        location="visibility",
                    )
                    for match in bad_vis
                )
            elif not _VIS_OK.search(vis_core):
                issues.append(
                    _issue(
                        "MISSING_VISIBILITY",
                        f"{product} missing visibility or CAVOK - A3-2 #6",
                        start=start,
                        end=end,
                        location="visibility",
                    )
                )

        if use_detectors:
            issues.extend(run_theme_pack("metar-speci-r3-weather", tac, product))
        else:
            issues.extend(r3_weather(tac, product))

        if not _TEMP.search(core):
            issues.append(
                _issue(
                    "MISSING_TEMP_DEWPOINT",
                    f"{product} missing temperature/dewpoint tt/td - A3-2 #10",
                    start=start,
                    end=end,
                    location="temperature",
                )
            )

        if not _QNH.search(core) and not _QNH_NOT_OBS.search(core):
            issues.append(
                _issue(
                    "MISSING_QNH",
                    f"{product} missing QNH/altimeter (Qnnnn/Annnn) - A3-2 #11",
                    start=start,
                    end=end,
                    location="pressure",
                )
            )

        if use_detectors:
            issues.extend(run_theme_pack("metar-speci-r4-cloud", tac, product))
            issues.extend(run_theme_pack("metar-speci-r5-remarks", tac, product))
            issues.extend(run_theme_pack("metar-speci-r8-modifiers", tac, product))
        else:
            issues.extend(r4_cloud(tac, product))
            issues.extend(r5_remarks(tac, product))
            issues.extend(r8_modifiers(tac, product))

        issues.extend(
            _check_ca_manobs(
                tokens,
                product=product,
                core=core,
                body_start=start,
                body_end=end,
                profile=profile,
            )
        )
        issues.extend(
            _check_s1_exceptional(
                tokens,
                product=product,
                core=core,
                body_start=start,
                body_end=end,
            )
        )
        return issues
    finally:
        lint_profile.reset(profile_token)


def _check_s1_exceptional(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """S1 exceptional METAR/SPECI tokens (Guidance + #734) - info diagnostics."""
    # ruff: noqa: F403, F405
    issues: list[Issue] = []
    if "CAVOK" in tokens:
        _emit_token_info(
            issues,
            code="CAVOK_PRESENT",
            message=f"{product} CAVOK present - research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="CAVOK",
        )
    if "NSC" in tokens:
        _emit_token_info(
            issues,
            code="NSC_PRESENT",
            message=f"{product} NSC present - research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NSC",
        )
        _emit_nsc_layer_exclusivity(
            issues,
            product=product,
            tokens=tokens,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    if "NCD" in tokens:
        _emit_token_info(
            issues,
            code="NCD_PRESENT",
            message=f"{product} NCD present - research S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NCD",
        )
    if "NSW" in tokens:
        _emit_token_info(
            issues,
            code="NSW_PRESENT",
            message=f"{product} NSW present - research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NSW",
        )
    if "VV///" in tokens:
        _emit_token_info(
            issues,
            code="VV_NOT_OBSERVABLE",
            message=f"{product} VV/// - verticalVisibility nil notObservable - research S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="VV///",
        )
    if "//" in tokens:
        _emit_token_info(
            issues,
            code="WX_NOT_OBSERVABLE",
            message=f"{product} present weather // - nil notObservable - research S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="//",
        )
    for tok in tokens:
        if _WIND_DIR_VAR.fullmatch(tok):
            _emit_token_info(
                issues,
                code="WIND_DIR_VARIATION",
                message=f"{product} wind direction variation {tok!r} - research S1",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            break
    return issues
