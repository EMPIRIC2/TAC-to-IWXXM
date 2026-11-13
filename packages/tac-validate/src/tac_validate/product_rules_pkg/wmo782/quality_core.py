"""Identity, visibility, and core WMO-782 METAR/SPECI quality checks."""

from __future__ import annotations

# pyright: reportPrivateUsage=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import (
    _LAYER_CLOUD_TOKEN,
    _METAR_SPECI_SKIP,
    _OBS_TIME,
    _RVR,
    _VIS_METERS,
    _VIS_OK,
    _WIND,
    _WIND_DIR_VAR,
    _WX_SIGNIFICANT,
    _first_icao_index,
    _issue,
    _token_index,
    _token_span_in_core,
)

_SOLIDUS_MANDATORY = re.compile(
    r"^(?:"
    r"/{2,5}\d{0,3}(?:KT|MPS)?"
    r"|\d{3}/{2}(?:KT|MPS)"
    r"|////(?:SM)?"
    r"|R\d{2}[LCR]?/{4,5}"
    r"|(?:FEW|SCT|BKN|OVC|VV)/{3}"
    r"|M?\d{2}/{2,3}"
    r"|[QA]/{4}"
    r")$"
)
_WIND_PARSE = re.compile(r"^(?:(?P<dir>VRB|\d{3}))(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<unit>KT|MPS)$")
_DV_VIS = re.compile(r"^(\d{4})(N|NE|E|SE|S|SW|W|NW)$")
_VIS_SOLIDUS = re.compile(r"^////(?:SM)?$")


def _vis_meters_on_reporting_scale(value: int) -> bool:
    """Return True when a metre visibility follows WMO-782 reporting steps."""
    if value >= 9999:
        return value == 9999
    if value < 800:
        return value % 50 == 0
    if value < 5000:
        return value % 100 == 0
    if value < 10000:
        return value % 1000 == 0
    return False


def _check_wmo782_first_groups_and_modifiers(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """Identification first-groups shape and COR/NIL/AUTO placement matrix."""
    issues: list[Issue] = []
    if not tokens:
        return issues

    # Strip optional leading product keyword for index math.
    idx0 = 0
    if tokens[0] in {"METAR", "SPECI"}:
        idx0 = 1
    head = tokens[idx0:]
    if not head:
        issues.append(
            _issue(
                "FIRST_GROUPS_FORMAT",
                f"{product} identification groups are incomplete",
                start=body_start,
                end=body_end,
                location="identity",
            )
        )
        return issues

    has_nil = "NIL" in tokens
    has_auto = "AUTO" in tokens
    has_cor = "COR" in tokens

    if has_nil and has_auto:
        span = _token_span_in_core(core, "NIL", body_start) or _token_span_in_core(core, "AUTO", body_start)
        start, end = (body_start, body_end) if span is None else span
        issues.append(
            _issue(
                "NIL_AUTO_CONFLICT",
                f"{product} includes both NIL and AUTO",
                start=start,
                end=end,
                location="identity",
            )
        )

    # COR: WMO slot is after the code name; US practice also places COR after YYGGggZ.
    if has_cor:
        cor_i = tokens.index("COR")
        time_i = _token_index(tokens, _OBS_TIME)
        after_code = cor_i == (1 if tokens[0] in {"METAR", "SPECI"} else 0)
        after_time = time_i is not None and cor_i == time_i + 1
        if not (after_code or after_time):
            span = _token_span_in_core(core, "COR", body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "COR_MISPLACED",
                    f"{product} places COR outside the accepted slot after the code name or after the date/time group",
                    start=start,
                    end=end,
                    location="identity",
                )
            )

    # AUTO must follow YYGGggZ (or appear after COR/CCCC/time in accepted shapes).
    if has_auto and not has_nil:
        auto_i = tokens.index("AUTO")
        time_i = _token_index(tokens, _OBS_TIME)
        if time_i is None or auto_i != time_i + 1:
            # Also accept AUTO immediately after product+COR+CCCC+time only.
            span = _token_span_in_core(core, "AUTO", body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "AUTO_MISPLACED",
                    f"{product} places AUTO outside the accepted slot after the date/time group",
                    start=start,
                    end=end,
                    location="identity",
                )
            )

    # NIL must stand alone after identification (no wind/vis/body); placement after time.
    if has_nil:
        nil_i = tokens.index("NIL")
        time_i = _token_index(tokens, _OBS_TIME)
        cccc_i = _first_icao_index(tokens, _METAR_SPECI_SKIP)
        body_after = [t for t in tokens[nil_i + 1 :] if t not in {"=", ""} and not t.startswith("RMK")]
        misplaced = False
        if (
            time_i is not None
            and nil_i != time_i + 1
            and not (cccc_i is not None and nil_i == cccc_i + 1 and time_i is None)
        ):
            # Accept NIL right after time, or (rare) as the body marker after CCCC when time omitted.
            misplaced = True
        if body_after and any(
            _WIND.fullmatch(t) or _VIS_OK.fullmatch(t) or _VIS_METERS.fullmatch(t) or t == "CAVOK" for t in body_after
        ):
            misplaced = True
        if misplaced:
            span = _token_span_in_core(core, "NIL", body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "NIL_MISPLACED",
                    f"{product} places NIL outside the accepted identification slot",
                    start=start,
                    end=end,
                    location="identity",
                )
            )

    # First-groups shape: need CCCC and YYGGggZ in order after optional COR.
    cccc_i = _first_icao_index(tokens, _METAR_SPECI_SKIP)
    time_i = _token_index(tokens, _OBS_TIME)
    shape_bad = cccc_i is None or time_i is None or cccc_i > time_i
    if not shape_bad and tokens[0] not in {"METAR", "SPECI"}:
        shape_bad = True
    # CCCC should be 4-char ICAO-like; reject obvious non-alpha station tokens already filtered.
    if not shape_bad and cccc_i is not None:
        # After product and optional COR, CCCC should be next identity group.
        expect_i = 1
        if len(tokens) > 1 and tokens[1] == "COR":
            expect_i = 2
        if cccc_i != expect_i:
            shape_bad = True
    if shape_bad:
        issues.append(
            _issue(
                "FIRST_GROUPS_FORMAT",
                f"{product} identification groups do not match an accepted METAR/SPECI "
                "± COR/AUTO/NIL and CCCC YYGGggZ shape",
                start=body_start,
                end=body_end,
                location="identity",
            )
        )
    return issues


def _check_wmo782_visibility_quality(
    obs_tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    is_auto: bool,
) -> list[Issue]:
    """AUTO ////, reporting-scale steps, and directional minimum Dv format."""
    issues: list[Issue] = []
    if "CAVOK" in obs_tokens:
        return issues

    for tok in obs_tokens:
        if is_auto and _VIS_SOLIDUS.fullmatch(tok):
            span = _token_span_in_core(core, tok, body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "AUTO_VISIBILITY_NOT_OBSERVABLE",
                    f"{product} AUTO report encodes visibility as {tok}",
                    start=start,
                    end=end,
                    location="visibility",
                )
            )
        if _VIS_METERS.fullmatch(tok):
            value = int(tok)
            if not _vis_meters_on_reporting_scale(value):
                span = _token_span_in_core(core, tok, body_start)
                start, end = (body_start, body_end) if span is None else span
                issues.append(
                    _issue(
                        "VISIBILITY_SCALE_STEP",
                        f"{product} visibility value {tok!r} does not follow the reporting scale",
                        start=start,
                        end=end,
                        location="visibility",
                    )
                )
        dv = _DV_VIS.fullmatch(tok)
        if dv is not None:
            dval = int(dv.group(1))
            if not _vis_meters_on_reporting_scale(dval) and dval != 9999:
                span = _token_span_in_core(core, tok, body_start)
                start, end = (body_start, body_end) if span is None else span
                issues.append(
                    _issue(
                        "DIRECTIONAL_VISIBILITY_FORMAT",
                        f"{product} directional minimum visibility {tok!r} should use the "
                        "reporting scale with four digits plus a direction",
                        start=start,
                        end=end,
                        location="visibility",
                    )
                )
        # Almost-Dv tokens: wrong shape (for example 1000NN, 100SW).
        if (
            re.fullmatch(r"\d{3,5}[A-Z]{1,3}", tok)
            and not _DV_VIS.fullmatch(tok)
            and not tok.endswith(("KT", "MPS", "SM"))
            and not _RVR.match(tok)
            and not _WIND.fullmatch(tok)
        ):
            span = _token_span_in_core(core, tok, body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "DIRECTIONAL_VISIBILITY_FORMAT",
                    f"{product} directional minimum visibility {tok!r} should be four "
                    "digits plus a direction (for example 1400SW)",
                    start=start,
                    end=end,
                    location="visibility",
                )
            )
    return issues


def _check_wmo782_metar_speci_quality(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """Emit WMO-No. 782 METAR/SPECI combination checks (solidus, CAVOK, VRB, range).

    Parameters
    ----------
    tokens : list[str]
        Uppercased report tokens (no trailing ``=``).
    product : str
        ``METAR`` or ``SPECI``.
    core : str
        Uppercased body text used for spans.
    body_start : int
        Absolute start offset of the body in the TAC string.
    body_end : int
        Absolute end offset of the body in the TAC string.

    Returns
    -------
    list[Issue]
        Zero or more registry-backed issues.
    """
    issues: list[Issue] = []
    is_auto = "AUTO" in tokens
    obs_tokens = tokens
    if "RMK" in tokens:
        obs_tokens = tokens[: tokens.index("RMK")]
    if "BECMG" in obs_tokens or "TEMPO" in obs_tokens or "NOSIG" in obs_tokens:
        cut = min(
            (obs_tokens.index(t) for t in ("BECMG", "TEMPO", "NOSIG") if t in obs_tokens),
            default=len(obs_tokens),
        )
        obs_tokens = obs_tokens[:cut]

    issues.extend(
        _check_wmo782_first_groups_and_modifiers(
            tokens,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )
    issues.extend(
        _check_wmo782_visibility_quality(
            obs_tokens,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
            is_auto=is_auto,
        )
    )

    if not is_auto:
        for tok in obs_tokens:
            if _SOLIDUS_MANDATORY.fullmatch(tok) or (tok.endswith(("KT", "MPS")) and "/" in tok):
                span = _token_span_in_core(core, tok, body_start)
                start, end = (body_start, body_end) if span is None else span
                issues.append(
                    _issue(
                        "MISSING_MANDATORY_DIGIT_AS_SOLIDUS",
                        f"{product} uses solidus in {tok!r} for a missing or incorrect mandatory digit",
                        start=start,
                        end=end,
                        location="body",
                    )
                )
                break

    if "CAVOK" in obs_tokens:
        has_wx = any(_WX_SIGNIFICANT.fullmatch(t) for t in obs_tokens if t not in {"CAVOK", "NSW", "NSC", "NCD"})
        has_layer = any(_LAYER_CLOUD_TOKEN.fullmatch(t) for t in obs_tokens)
        has_cb_tcu = any(t.endswith(("CB", "TCU")) for t in obs_tokens)
        # Visibility groups that contradict CAVOK (≥10 km / CAVOK exclusivity).
        has_low_vis = False
        for tok in obs_tokens:
            if tok in {"CAVOK", "9999"} or tok.endswith("SM"):
                continue
            if re.fullmatch(r"\d{4}", tok) and int(tok) < 9999:
                has_low_vis = True
                break
        if has_wx or has_layer or has_cb_tcu or has_low_vis:
            span = _token_span_in_core(core, "CAVOK", body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "CAVOK_CONDITIONS_NOT_MET",
                    f"{product} CAVOK is present with weather, cloud of operational significance, "
                    "or visibility below 10 km",
                    start=start,
                    end=end,
                    location="cavok",
                )
            )

    from tac_validate.product_rules_pkg.wmo782.check import check_wmo782_extended

    issues.extend(
        check_wmo782_extended(
            tokens,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )

    has_dir_var = any(_WIND_DIR_VAR.fullmatch(t) for t in obs_tokens)
    for tok in obs_tokens:
        parsed = _WIND_PARSE.fullmatch(tok)
        if parsed is None:
            continue
        direction = parsed.group("dir")
        speed = int(parsed.group("spd"))
        gust = parsed.group("gust")
        unit = parsed.group("unit")
        if direction == "VRB" and has_dir_var:
            span = _token_span_in_core(core, tok, body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "WIND_VRB_MISUSE",
                    f"{product} wind {tok!r} uses VRB together with a directed variation group",
                    start=start,
                    end=end,
                    location="wind",
                )
            )
        # Physical range: hurricane-force mean in METAR; large gust spread.
        mean_kt = speed if unit == "KT" else speed * 2  # ~ m/s → kt for threshold compare
        if product == "METAR" and mean_kt >= 64:
            span = _token_span_in_core(core, tok, body_start)
            start, end = (body_start, body_end) if span is None else span
            issues.append(
                _issue(
                    "WIND_PHYSICAL_RANGE",
                    f"{product} mean wind {tok!r} is hurricane-force; confirm encode or prefer SPECI criteria",
                    start=start,
                    end=end,
                    location="wind",
                )
            )
        if gust is not None:
            gust_n = int(gust)
            spread = gust_n - speed
            spread_kt = spread if unit == "KT" else spread * 2
            if spread_kt >= 40:
                span = _token_span_in_core(core, tok, body_start)
                start, end = (body_start, body_end) if span is None else span
                issues.append(
                    _issue(
                        "WIND_PHYSICAL_RANGE",
                        f"{product} gust spread in {tok!r} is unusually large relative to the mean",
                        start=start,
                        end=end,
                        location="wind",
                    )
                )
    return issues


__all__ = [
    "_check_wmo782_first_groups_and_modifiers",
    "_check_wmo782_metar_speci_quality",
    "_check_wmo782_visibility_quality",
]
