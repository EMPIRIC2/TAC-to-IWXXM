"""METAR/SPECI R-theme check bodies shared by legacy dispatch and detector hatches.

ADR-046 / #1216 M3: thin-wrap behind detector pack ids (D-VPL-G3). Profile for R5
is supplied via ``lint_profile`` contextvar (hatches only receive tac + product).
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import contextvars

from tac_validate import membership
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import (
    _LAYER_CLOUD_PARTS,
    _METAR_SPECI_SKIP,
    _OBS_TIME,
    _RECENT_WX,
    _body_span,
    _check_metar_speci_field_order,
    _check_r8_pack,
    _check_us_remarks,
    _cloud_candidate_tokens,
    _emit_token_info,
    _first_icao,
    _is_valid_cloud_token,
    _is_valid_weather_token,
    _issue,
    _membership_issue,
    _token_span_in_core,
    _weather_candidate_tokens,
    _weather_in_register,
)

lint_profile: contextvars.ContextVar[str] = contextvars.ContextVar("lint_profile", default="annex3")

R1_CODES = frozenset({"MISSING_CCCC", "MISSING_OBS_TIME", "ODD_FIELD_ORDER"})
R3_CODES = frozenset({"INVALID_WEATHER", "UNKNOWN_WMO_MEMBERSHIP"})
R4_CODES = frozenset({"INVALID_CLOUD_TOKEN", "CLOUD_CB_OR_TCU", "UNKNOWN_WMO_MEMBERSHIP"})
R5_CODES = frozenset({"INVALID_REMARK", "REMARK_US_EXTENSION"})
R8_CODES = frozenset(
    {
        "AUTO_PRESENT",
        "COR_PRESENT",
        "INVALID_NIL",
        "NIL_REPORT",
        "NOSIG_PRESENT",
        "TEMPO_PRESENT",
        "RVR_PRESENT",
        "INVALID_RVR",
        "INVALID_WIND",
        "WIND_VRB_OR_GUST",
    }
)


def _tokens(tac: str) -> tuple[int, int, str, list[str]]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    return start, end, core, tokens


def r1_identity_order(tac_text: str, product: str) -> list[Issue]:
    """R1: CCCC, observation time, field order."""
    start, end, core, tokens = _tokens(tac_text)
    issues: list[Issue] = []
    if _first_icao(tokens, _METAR_SPECI_SKIP) is None:
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
    order_issue = _check_metar_speci_field_order(tokens, product=product, start=start, end=end)
    if order_issue is not None:
        issues.append(order_issue)
    return issues


def r3_weather(tac_text: str, product: str) -> list[Issue]:
    """R3: present / recent weather token validity + membership."""
    start, end, core, tokens = _tokens(tac_text)
    issues: list[Issue] = []
    for _i, wx_tok in _weather_candidate_tokens(tokens):
        span = _token_span_in_core(core, wx_tok, start)
        if span is None:
            wx_start, wx_end = start, end
        else:
            wx_start, wx_end = span
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
    return issues


def r4_cloud(tac_text: str, product: str) -> list[Issue]:
    """R4: cloud / VV tokens + CB/TCU info."""
    start, end, core, tokens = _tokens(tac_text)
    issues: list[Issue] = []
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
    return issues


def r5_remarks(tac_text: str, product: str) -> list[Issue]:
    """R5: US REMARKS malformed + iwxxm_us extension awareness."""
    start, end, core, tokens = _tokens(tac_text)
    return _check_us_remarks(
        tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
        profile=lint_profile.get(),
    )


def r8_nil_gate(tac_text: str, product: str) -> list[Issue] | None:
    """If NIL is report content, return R8 NIL issues; else ``None`` (continue body)."""
    start, end, core, tokens = _tokens(tac_text)
    if "NIL" not in tokens:
        return None
    issues: list[Issue] = []
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


def r8_modifiers(tac_text: str, product: str) -> list[Issue]:
    """R8 non-NIL: AUTO/COR/NOSIG/TEMPO/RVR/wind diagnostics."""
    start, end, core, tokens = _tokens(tac_text)
    if "NIL" in tokens:
        return []
    return _check_r8_pack(
        tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
    )


def hatch_r1(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for R1 pack."""
    return r1_identity_order(tac_text, product)


def hatch_r1_order(tac_text: str, product: str) -> list[Issue]:
    """Declarative R1 residual: field-order only (CCCC / time via YAML)."""
    start, end, _core, tokens = _tokens(tac_text)
    order_issue = _check_metar_speci_field_order(tokens, product=product, start=start, end=end)
    return [order_issue] if order_issue is not None else []


def hatch_r3(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for R3 pack."""
    return r3_weather(tac_text, product)


def hatch_r4(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for R4 pack."""
    return r4_cloud(tac_text, product)


def hatch_r4_membership(tac_text: str, product: str) -> list[Issue]:
    """Declarative R4 residual: WMO membership only (shape/CB via YAML)."""
    start, end, core, tokens = _tokens(tac_text)
    issues: list[Issue] = []
    for _i, cloud_tok in _cloud_candidate_tokens(tokens):
        if not _is_valid_cloud_token(cloud_tok):
            continue
        span = _token_span_in_core(core, cloud_tok, start)
        if span is None:
            cloud_start, cloud_end = start, end
        else:
            cloud_start, cloud_end = span
        parts = _LAYER_CLOUD_PARTS.fullmatch(cloud_tok)
        if parts is None:
            continue
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
    return issues


def hatch_r5(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for R5 pack."""
    return r5_remarks(tac_text, product)


def hatch_r5_pk_and_extension(tac_text: str, product: str) -> list[Issue]:
    """Declarative R5 residual: PK WND + iwxxm_us extension (SLP/P/T shape via YAML)."""
    start, end, core, tokens = _tokens(tac_text)
    if "RMK" not in tokens:
        return []
    from tac_validate.product_rules_pkg._common import (
        _RMK_AO,
        _RMK_P_OK,
        _RMK_PK_VAL,
        _RMK_SLP_OK,
        _RMK_T_OK,
        _append_remark_issue,
    )

    rmk_i = tokens.index("RMK")
    remark = tokens[rmk_i + 1 :]
    issues: list[Issue] = []
    saw_us = False
    i = 0
    while i < len(remark):
        tok = remark[i]
        if tok in _RMK_AO:
            saw_us = True
            i += 1
            continue
        if _RMK_SLP_OK.fullmatch(tok):
            saw_us = True
            i += 1
            continue
        if tok.startswith("SLP") and tok[3:].isdigit():
            # Malformed SLP handled by declarative finditer.
            i += 1
            continue
        if _RMK_P_OK.fullmatch(tok):
            saw_us = True
            i += 1
            continue
        if len(tok) > 1 and tok[0] == "P" and tok[1:].isdigit():
            i += 1
            continue
        if _RMK_T_OK.fullmatch(tok):
            saw_us = True
            i += 1
            continue
        if len(tok) > 1 and tok[0] == "T" and tok[1:].isdigit():
            i += 1
            continue
        if tok == "PK":
            has_wnd = i + 1 < len(remark) and remark[i + 1] == "WND"
            has_val = has_wnd and i + 2 < len(remark) and _RMK_PK_VAL.fullmatch(remark[i + 2])
            if has_val:
                saw_us = True
                i += 3
                continue
            span_tok = "WND" if has_wnd else "PK"
            _append_remark_issue(
                issues,
                code="INVALID_REMARK",
                message=f"{product} malformed remark PK WND (need dddss/tt)",
                core=core,
                body_start=start,
                body_end=end,
                token=span_tok,
            )
            if has_wnd:
                i += 2
            else:
                i += 1
            continue
        i += 1

    if saw_us and lint_profile.get() == "iwxxm_us":
        _append_remark_issue(
            issues,
            code="REMARK_US_EXTENSION",
            message=(f"{product} US remarks present (AO1/AO2/SLP/P/T/PK WND) - iwxxm_us profile awareness"),
            core=core,
            body_start=start,
            body_end=end,
            token="RMK",
        )
    return issues


def hatch_r8(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for R8 pack (NIL gate + modifiers)."""
    nil = r8_nil_gate(tac_text, product)
    if nil is not None:
        return nil
    return r8_modifiers(tac_text, product)


def hatch_taf(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for TAF core checklist (A5-1 + F20 gates)."""
    del product  # pack products: [TAF]; profile via lint_profile contextvar
    from tac_validate.product_rules_pkg.taf import _check_taf

    return _check_taf(tac_text, profile=lint_profile.get())


def hatch_sigmet(tac_text: str, product: str) -> list[Issue]:
    """Detector hatch for SIGMET A6 / F23 checklist."""
    from tac_validate.product_rules_pkg.sigmet_airmet import _check_sigmet_airmet

    return _check_sigmet_airmet(tac_text, product, profile=lint_profile.get())


__all__ = [
    "R1_CODES",
    "R3_CODES",
    "R4_CODES",
    "R5_CODES",
    "R8_CODES",
    "hatch_r1",
    "hatch_r1_order",
    "hatch_r3",
    "hatch_r4",
    "hatch_r4_membership",
    "hatch_r5",
    "hatch_r5_pk_and_extension",
    "hatch_r8",
    "hatch_sigmet",
    "hatch_taf",
    "lint_profile",
    "r1_identity_order",
    "r3_weather",
    "r4_cloud",
    "r5_remarks",
    "r8_modifiers",
    "r8_nil_gate",
]
