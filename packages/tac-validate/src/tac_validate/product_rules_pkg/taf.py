"""Product rules - taf."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *


def _check_taf(tac: str, *, profile: str = "annex3") -> list[Issue]:
    """TAF checklist - A5-1 template gates + F20 T1 NIL/CNL/AMD/COR."""
    # ruff: noqa: F403, F405
    start, end, body = _body_span(tac)
    upper = body.upper()
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []
    product = "TAF"
    issues.extend(_check_c1_multi_report(tac, product))

    if _first_icao(tokens, _TAF_SKIP) is None:
        issues.append(
            _issue(
                "MISSING_CCCC",
                "TAF missing ICAO location (CCCC) - A5-1 #2",
                start=start,
                end=end,
                location="station",
            )
        )

    if not _OBS_TIME.search(core):
        issues.append(
            _issue(
                "MISSING_ISSUE_TIME",
                "TAF missing issue time ddhhmmZ - A5-1 #3",
                start=start,
                end=end,
                location="time",
            )
        )

    # T1 NIL: missing forecast ends the message (A5-1 #4) - skip validity body gates.
    if "NIL" in tokens:
        if "AMD" in tokens:
            _emit_token_info(
                issues,
                code="AMD_PRESENT",
                message=f"{product} AMD modifier present - research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="AMD",
            )
        if "COR" in tokens:
            _emit_token_info(
                issues,
                code="COR_PRESENT",
                message=f"{product} COR modifier present - research T1",
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
                message=f"{product} NIL must not include body groups - research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        else:
            _emit_token_info(
                issues,
                code="NIL_REPORT",
                message=f"{product} NIL report - research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        return issues

    if not _TAF_VALIDITY.search(core):
        issues.append(
            _issue(
                "MISSING_VALIDITY",
                "TAF missing validity period ddhh/ddhh - A5-1 #5",
                start=start,
                end=end,
                location="validity",
            )
        )

    if "AMD" in tokens:
        _emit_token_info(
            issues,
            code="AMD_PRESENT",
            message=f"{product} AMD modifier present - research T1",
            core=core,
            body_start=start,
            body_end=end,
            token="AMD",
        )
    if "COR" in tokens:
        _emit_token_info(
            issues,
            code="COR_PRESENT",
            message=f"{product} COR modifier present - research T1",
            core=core,
            body_start=start,
            body_end=end,
            token="COR",
        )

    if "CNL" in tokens:
        # CNL must terminate the forecast content (A5-1 #6 paraphrase).
        cnl_idx = tokens.index("CNL")
        trailing = [t for t in tokens[cnl_idx + 1 :] if t not in {"="}]
        if trailing:
            _emit_token_info(
                issues,
                code="INVALID_CNL_SHAPE",
                message="TAF CNL must end the message - A5-1 #6",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
        else:
            _emit_token_info(
                issues,
                code="CNL_REPORT",
                message=f"{product} CNL cancel report - research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
        return issues

    # T2 change groups - FM / BECMG / TEMPO / PROB + TL / AT (App 5 §1.4 / A5-2).
    _check_taf_change_groups(
        issues,
        tokens=tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
    )
    # T3 - TX/TN base-only; CAVOK / NSC / NSW / VV/// (Guidance exceptional).
    _check_taf_t3_elements(
        issues,
        tokens=tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
    )
    issues.extend(
        _check_ca_manair(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
            profile=profile,
        )
    )
    issues.extend(
        _check_us_faa_nws_taf(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
            profile=profile,
        )
    )

    return issues


def _check_us_faa_nws_taf(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """US_FAA_NWS TAF overlay rules for ``profile=iwxxm_us`` (#919 M13)."""
    if profile != "iwxxm_us" or product != "TAF":
        return []
    issues: list[Issue] = []
    if "BECMG" in tokens:
        issues.append(
            _issue(
                "US_TAF_BECMG_FORBIDDEN",
                f"{product} BECMG is forbidden under US_FAA_NWS - FMH-1 / FAA GEN 1.7",
                start=body_start,
                end=body_end,
                location="change_group",
            )
        )
    for i, tok in enumerate(tokens):
        if tok != "TEMPO":
            continue
        window = tokens[i + 1] if i + 1 < len(tokens) else ""
        duration_h: int | None = None
        m = re.fullmatch(r"(\d{2})(\d{2})/(\d{2})(\d{2})", window)
        if m is not None:
            start_h = int(m.group(2))
            end_h = int(m.group(4))
            duration_h = (end_h - start_h) if end_h >= start_h else (24 - start_h + end_h)
        elif _TAF_TL.fullmatch(window):
            # TL-only TEMPO without explicit window - cannot compute duration here.
            duration_h = None
        if duration_h is not None and duration_h > 4:
            issues.append(
                _issue(
                    "US_TAF_TEMPO_MAX_4H",
                    f"{product} TEMPO exceeds 4h maximum under US_FAA_NWS - FMH-1",
                    start=body_start,
                    end=body_end,
                    location="change_group",
                )
            )
        break
    return issues


def _taf_first_change_index(tokens: list[str]) -> int | None:
    """Index of first FM/BECMG/TEMPO/PROB change indicator, if any."""
    for i, tok in enumerate(tokens):
        if tok in {"BECMG", "TEMPO"} or _TAF_FM.fullmatch(tok) or _TAF_PROB.fullmatch(tok):
            return i
    return None


def _check_taf_t3_elements(
    issues: list[Issue],
    *,
    tokens: list[str],
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> None:
    """Emit T3 info/error codes for TX/TN and CAVOK/NSC/NSW/VV///."""
    change_i = _taf_first_change_index(tokens)
    tx_tn_toks = [(i, t) for i, t in enumerate(tokens) if _TAF_TX_TN.fullmatch(t)]
    if tx_tn_toks:
        on_change = any(change_i is not None and i >= change_i for i, _t in tx_tn_toks)
        first_tok = tx_tn_toks[0][1]
        if on_change:
            _emit_token_info(
                issues,
                code="INVALID_TX_TN",
                message=f"{product} TX/TN allowed on base forecast only - research T3",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=first_tok,
            )
        else:
            _emit_token_info(
                issues,
                code="TX_TN_PRESENT",
                message=f"{product} TX/TN temperature forecasts on base - research T3",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=first_tok,
            )

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
            code="VV_OMIT",
            message=f"{product} VV/// - omit verticalVisibility without nilReason - research T3",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="VV///",
        )


def _check_taf_change_groups(
    issues: list[Issue],
    *,
    tokens: list[str],
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> None:
    """Emit T2 info/error codes for TAF change indicators."""
    fm_tok = next((t for t in tokens if _TAF_FM.fullmatch(t)), None)
    if fm_tok is not None:
        _emit_token_info(
            issues,
            code="FM_PRESENT",
            message=f"{product} FM change group present - research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=fm_tok,
        )
    if "BECMG" in tokens:
        _emit_token_info(
            issues,
            code="BECMG_PRESENT",
            message=f"{product} BECMG change group present - research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="BECMG",
        )
    if "TEMPO" in tokens:
        _emit_token_info(
            issues,
            code="TEMPO_PRESENT",
            message=f"{product} TEMPO change group present - research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="TEMPO",
        )

    tl_tok = next((t for t in tokens if _TAF_TL.fullmatch(t)), None)
    if tl_tok is not None:
        _emit_token_info(
            issues,
            code="TL_PRESENT",
            message=f"{product} TL time group present - research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=tl_tok,
        )
    at_tok = next((t for t in tokens if _TAF_AT.fullmatch(t)), None)
    if at_tok is not None:
        _emit_token_info(
            issues,
            code="AT_PRESENT",
            message=f"{product} AT time group present - research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=at_tok,
        )

    for i, tok in enumerate(tokens):
        m = _TAF_PROB.fullmatch(tok)
        if m is None:
            continue
        pct = m.group(1)
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        qualifies_forbidden = nxt == "BECMG" or bool(_TAF_FM.fullmatch(nxt))
        if pct not in {"30", "40"} or qualifies_forbidden:
            _emit_token_info(
                issues,
                code="INVALID_PROB",
                message=(f"{product} invalid PROB (only 30|40; must not qualify BECMG/FM) - App 5 §1.4 / research T2"),
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
        else:
            _emit_token_info(
                issues,
                code="PROB_PRESENT",
                message=f"{product} PROB30/40 change group present - research T2",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
