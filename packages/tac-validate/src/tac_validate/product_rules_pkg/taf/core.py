"""Product rules - taf."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *
from tac_validate.station_scoped_policy import accepts_end_tx_tn
from tac_validate.taf_amd import amd_modifier_present
from tac_validate.taf_prob import ProbGroupKind, classify_probability_group


def _check_taf(tac: str, *, profile: str = "annex3") -> list[Issue]:
    """
    Internal helper ``_check_taf``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    # ruff: noqa: F403, F405
    from tac_validate.product_rules_pkg.taf.change_groups import _check_taf_change_groups
    from tac_validate.product_rules_pkg.taf.national_t3 import (
        _check_taf_t3_elements,
        _check_us_faa_nws_taf,
    )

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
        if amd_modifier_present(tokens):
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

    if amd_modifier_present(tokens):
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
    # T3 - TX/TN base-only (annex3); us_military accepts end TX/TN.
    _check_taf_t3_elements(
        issues,
        tokens=tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
        profile=profile,
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
        _check_in_imd_taf(
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

    spaced_cavok = any(tokens[i : i + 5] == ["C", "A", "V", "O", "K"] for i in range(max(0, len(tokens) - 4)))
    issues.extend(
        _issue(
            "MALFORMED_SOURCE_TOKEN",
            f"{product} looks like a source typo or garbled group {tok!r}",
            start=start,
            end=end,
            location="body",
        )
        for tok in tokens
        if tok in {"-VCTSRA", "SC045", "BKN0206", "ECMG"}
        or re.fullmatch(r"\d{4}/\d{5}", tok)
        or re.fullmatch(r"(?:FEW|SCT|BKN|OVC)\d{4,}", tok)
    )
    if spaced_cavok:
        issues.append(
            _issue(
                "MALFORMED_SOURCE_TOKEN",
                f"{product} looks like a source typo or garbled group 'C A V O K'",
                start=start,
                end=end,
                location="body",
            )
        )

    return issues


__all__ = [
    "Issue",
    "ProbGroupKind",
    "_check_taf",
    "accepts_end_tx_tn",
    "amd_modifier_present",
    "classify_probability_group",
]
