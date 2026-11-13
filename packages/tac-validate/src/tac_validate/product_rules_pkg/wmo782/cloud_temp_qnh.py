"""Cloud, temperature, and QNH combination checks (WMO-No. 782)."""

from __future__ import annotations

# pyright: reportPrivateUsage=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from tac_validate.models import Issue
from tac_validate.product_rules_pkg.wmo782._emit import (
    CLOUD_BAD_SUFFIX,
    CLOUD_LAYER,
    QNH,
    TEMP_PAIR,
    emit,
    parse_temp_c,
)


def check_cloud_temp_qnh(
    obs: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    is_auto: bool,
) -> list[Issue]:
    """Emit cloud order/count/type, VV exclusivity, dew-point, and QNH issues."""
    issues: list[Issue] = []
    layers: list[tuple[str, int, str | None]] = []

    for tok in obs:
        m = CLOUD_LAYER.fullmatch(tok)
        if m:
            layers.append((tok, int(m.group(1)), m.group(2)))
        bad = CLOUD_BAD_SUFFIX.fullmatch(tok)
        if bad and bad.group(1) not in {"CB", "TCU"}:
            emit(
                issues,
                "CLOUD_TYPE_SUFFIX_ONLY_CB_TCU",
                f"{product} Cloud type suffix outside CB TCU or AUTO ///",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="cloud",
            )
        if tok == "NCD" and not is_auto:
            emit(
                issues,
                "NCD_REQUIRES_AUTO",
                f"{product} NCD without AUTO",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="cloud",
            )

    heights = [h for _, h, _ in layers]
    if heights != sorted(heights) and layers:
        emit(
            issues,
            "CLOUD_HEIGHT_NOT_ASCENDING",
            f"{product} cloud layer heights are not in ascending order",
            core=core,
            tok=layers[0][0],
            body_start=body_start,
            body_end=body_end,
            location="cloud",
        )
    has_conv = any(suf in {"CB", "TCU"} for _, _, suf in layers)
    if len(layers) > 3 and not (len(layers) == 4 and has_conv):
        emit(
            issues,
            "CLOUD_LAYER_COUNT_EXCEEDED",
            f"{product} reports more than three cloud groups without a CB/TCU fourth-layer exemption",
            core=core,
            tok=layers[3][0],
            body_start=body_start,
            body_end=body_end,
            location="cloud",
        )
    by_h: dict[int, set[str]] = {}
    for _, h, suf in layers:
        if suf:
            by_h.setdefault(h, set()).add(suf)
    if any("CB" in s and "TCU" in s for s in by_h.values()) and layers:
        emit(
            issues,
            "CLOUD_COMMON_BASE_CB_TCU",
            f"{product} should merge CB and TCU that share a common base into one cloud group",
            core=core,
            tok=layers[0][0],
            body_start=body_start,
            body_end=body_end,
            location="cloud",
        )

    vv = next((t for t in obs if t.startswith("VV")), None)
    if vv and (layers or any(t in {"NSC", "NCD", "CAVOK"} for t in obs)):
        emit(
            issues,
            "VV_EXCLUDES_CLOUD_LAYERS",
            f"{product} VV group mixed with cloud layers NSC NCD or CAVOK",
            core=core,
            tok=vv,
            body_start=body_start,
            body_end=body_end,
            location="cloud",
        )

    temp_tok = next((t for t in obs if TEMP_PAIR.fullmatch(t)), None)
    if temp_tok:
        left, right = temp_tok.split("/", 1)
        air_c = parse_temp_c(left)
        dew_c = parse_temp_c(right)
        if air_c is not None and dew_c is not None and dew_c > air_c:
            emit(
                issues,
                "TEMP_DEWPOINT_INVERSION",
                f"{product} dew-point temperature is higher than air temperature",
                core=core,
                tok=temp_tok,
                body_start=body_start,
                body_end=body_end,
                location="temperature",
            )

    for tok in obs:
        q = QNH.fullmatch(tok)
        if not q:
            continue
        if q.group("digits") == "////":
            emit(
                issues,
                "QNH_MISSING_AS_SOLIDUS",
                f"{product} encodes missing QNH as {tok}",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="pressure",
            )
        else:
            digits = int(q.group("digits"))
            pre = q.group("pre")
            if (pre == "Q" and digits > 2000) or (pre == "A" and digits < 2000):
                emit(
                    issues,
                    "QNH_PREFIX_UNIT_MISMATCH",
                    f"{product} Q with inHg-like digits or A with hPa-like digits",
                    core=core,
                    tok=tok,
                    body_start=body_start,
                    body_end=body_end,
                    location="pressure",
                )
    return issues
