"""Product rules - metar_speci."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

from tac_validate import membership
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *


def _check_metar_speci(tac: str, product: str, *, profile: str = "annex3") -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    # Drop trailing '=' for token scans.
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []
    issues.extend(_check_c1_multi_report(tac, product))

    cccc = _first_icao(tokens, _METAR_SPECI_SKIP)
    if cccc is None:
        issues.append(
            _issue(
                "MISSING_CCCC",
                f"{product} missing ICAO location (CCCC) - A3-2 #2",
                start=start,
                end=end,
                location="station",
            )
        )

    if not _OBS_TIME.search(core):
        issues.append(
            _issue(
                "MISSING_OBS_TIME",
                f"{product} missing observation time ddhhmmZ - A3-2 #3",
                start=start,
                end=end,
                location="time",
            )
        )

    # R8 NIL: short-circuit body checklist when NIL is the report content.
    if "NIL" in tokens:
        if "AUTO" in tokens:
            _emit_token_info(
                issues,
                code="AUTO_PRESENT",
                message=f"{product} AUTO modifier present - research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="AUTO",
            )
        if "COR" in tokens:
            _emit_token_info(
                issues,
                code="COR_PRESENT",
                message=f"{product} COR modifier present - research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="COR",
            )
        trailing = tokens[tokens.index("NIL") + 1 :]
        if trailing:
            _emit_token_info(
                issues,
                code="INVALID_NIL",
                message=f"{product} NIL must not include body groups - research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        else:
            _emit_token_info(
                issues,
                code="NIL_REPORT",
                message=f"{product} NIL report - research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        return issues

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

    order_issue = _check_metar_speci_field_order(tokens, product=product, start=start, end=end)
    if order_issue is not None:
        issues.append(order_issue)

    # Visibility lives before RMK - do not treat PK WND dddss/tt digits as vis (R2/R5).
    # Strip WMO AHL heading lines so YYGGgg (e.g. 121200) is not INVALID_VISIBILITY (EV-040).
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

    for _i, wx_tok in _weather_candidate_tokens(tokens):
        span = _token_span_in_core(core, wx_tok, start)
        if span is None:
            wx_start, wx_end = start, end
        else:
            wx_start, wx_end = span
        # Recent weather (RE*) - AerodromeRecentWeather membership (EV-050).
        if _RECENT_WX.fullmatch(wx_tok):
            if membership.is_member("recent_weather", wx_tok):
                continue
            issues.append(
                _membership_issue(
                    product=product,
                    token=wx_tok,
                    family="recent_weather",
                    start=wx_start,
                    end=wx_end,
                    location="weather",
                )
            )
            continue
        if _is_valid_weather_token(wx_tok):
            if _weather_in_register(wx_tok):
                continue
            issues.append(
                _membership_issue(
                    product=product,
                    token=wx_tok,
                    family="present_or_forecast_weather",
                    start=wx_start,
                    end=wx_end,
                    location="weather",
                )
            )
            continue
        issues.append(
            _issue(
                "INVALID_WEATHER",
                f"{product} invalid present weather token {wx_tok!r} - A3-2 #8 / research R3",
                start=wx_start,
                end=wx_end,
                location="weather",
            )
        )

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

    for _i, cloud_tok in _cloud_candidate_tokens(tokens):
        span = _token_span_in_core(core, cloud_tok, start)
        if span is None:
            cloud_start, cloud_end = start, end
        else:
            cloud_start, cloud_end = span
        if not _is_valid_cloud_token(cloud_tok):
            issues.append(
                _issue(
                    "INVALID_CLOUD_TOKEN",
                    f"{product} invalid cloud/VV token {cloud_tok!r} - A3-2 #9 / research R4",
                    start=cloud_start,
                    end=cloud_end,
                    location="cloud",
                )
            )
            continue
        parts = _LAYER_CLOUD_PARTS.fullmatch(cloud_tok)
        if parts is not None:
            amount, ctype = parts.group(1), parts.group(2)
            if not membership.is_member("cloud_amount", amount):
                issues.append(
                    _membership_issue(
                        product=product,
                        token=amount,
                        family="cloud_amount",
                        start=cloud_start,
                        end=cloud_end,
                        location="cloud",
                    )
                )
            if ctype is not None and not membership.is_member("cloud_type", ctype):
                issues.append(
                    _membership_issue(
                        product=product,
                        token=ctype,
                        family="cloud_type",
                        start=cloud_start,
                        end=cloud_end,
                        location="cloud",
                    )
                )
        if cloud_tok.endswith(("CB", "TCU")):
            issues.append(
                _issue(
                    "CLOUD_CB_OR_TCU",
                    f"{product} cloud group {cloud_tok!r} includes convective type - research R4",
                    start=cloud_start,
                    end=cloud_end,
                    location="cloud",
                )
            )

    issues.extend(
        _check_us_remarks(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
            profile=profile,
        )
    )
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
        _check_r8_pack(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
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
