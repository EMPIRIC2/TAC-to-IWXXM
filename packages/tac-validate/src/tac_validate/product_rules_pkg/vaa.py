# ruff: noqa: F403, F405
"""Product rules — vaa."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *


def _check_vaa(tac: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "VAA missing DTG: template field — A2-1",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _VAAC_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_VAAC",
                "VAA missing VAAC: template field — A2-1",
                start=start,
                end=end,
                location="vaac",
            )
        )
    # F26 theme V1 — exceptional volcano / remarks / forecast / next-advisory cues (#736).
    volcano_m = _VOLCANO_LINE.search(body)
    if not volcano_m:
        issues.append(
            _issue(
                "MISSING_VOLCANO",
                "VAA missing VOLCANO: template field — F26 theme V1 / A2-1",
                start=start,
                end=end,
                location="volcano",
            )
        )
    else:
        volcano_val = volcano_m.group(1).strip().upper()
        v_start, v_end = volcano_m.start(1), volcano_m.end(1)
        if not volcano_val:
            issues.append(
                _issue(
                    "MISSING_VOLCANO",
                    "VAA missing VOLCANO: template field — F26 theme V1 / A2-1",
                    start=volcano_m.start(),
                    end=volcano_m.end(),
                    location="volcano",
                )
            )
        elif volcano_val.split()[0] == "UNKNOWN":
            issues.append(
                _issue(
                    "VAA_VOLCANO_UNKNOWN",
                    "VAA VOLCANO UNKNOWN — exceptional name allowed (F26 theme V1)",
                    start=v_start,
                    end=v_end,
                    location="volcano",
                )
            )
        elif volcano_val.split()[0] == "UNNAMED":
            issues.append(
                _issue(
                    "VAA_VOLCANO_UNNAMED",
                    "VAA VOLCANO UNNAMED — exceptional name allowed (F26 theme V1)",
                    start=v_start,
                    end=v_end,
                    location="volcano",
                )
            )
    rmk_m = _RMK_LINE.search(body)
    if rmk_m:
        rmk_val = rmk_m.group(1).strip().rstrip("=").upper()
        if rmk_val == "NIL":
            issues.append(
                _issue(
                    "VAA_RMK_NIL",
                    "VAA RMK NIL — remarks inapplicable (F26 theme V1)",
                    start=rmk_m.start(1),
                    end=rmk_m.end(1),
                    location="remarks",
                )
            )
    no_va = _NO_VA_EXP.search(body)
    if no_va is not None:
        issues.append(
            _issue(
                "VAA_FCST_NO_VA_EXP",
                "VAA forecast NO VA EXP — status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)",
                start=no_va.start(),
                end=no_va.end(),
                location="forecast",
            )
        )
    nxt_m = _NXT_ADVISORY_LINE.search(body)
    if nxt_m and "NO FURTHER" in nxt_m.group(1).upper():
        issues.append(
            _issue(
                "VAA_NO_FURTHER_ADVISORIES",
                "VAA NXT ADVISORY NO FURTHER ADVISORIES — next time inapplicable (F26 theme V1)",
                start=nxt_m.start(1),
                end=nxt_m.end(1),
                location="next_advisory",
            )
        )
    return issues
