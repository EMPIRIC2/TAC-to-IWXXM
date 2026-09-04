"""Product rules - vona."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *


def _check_vona(tac: str) -> list[Issue]:
    """F32 theme V1 - VONA template gates + ONSET/DUR NIL info (#741)."""
    # ruff: noqa: F403, F405
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "VONA missing DTG: template field - A7-1",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _SVO_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_SVO",
                "VONA missing SVO: template field - F32 theme V1 / A7-1",
                start=start,
                end=end,
                location="svo",
            )
        )
    volcano_m = _VOLCANO_LINE.search(body)
    if not volcano_m:
        issues.append(
            _issue(
                "MISSING_VONA_VOLCANO",
                "VONA missing VOLCANO: template field - F32 theme V1 / A7-1",
                start=start,
                end=end,
                location="volcano",
            )
        )
    onset_m = _ONSET_LINE.search(body)
    if onset_m and onset_m.group(1).strip().rstrip("=").upper() == "NIL":
        issues.append(
            _issue(
                "VONA_ONSET_NIL",
                "VONA ONSET NIL - onsetTime omitted (F32 theme V1)",
                start=onset_m.start(1),
                end=onset_m.end(1),
                location="onset",
            )
        )
    dur_m = _DUR_LINE.search(body)
    if dur_m and dur_m.group(1).strip().rstrip("=").upper() == "NIL":
        issues.append(
            _issue(
                "VONA_DUR_NIL",
                "VONA DUR NIL - duration omitted (F32 theme V1)",
                start=dur_m.start(1),
                end=dur_m.end(1),
                location="duration",
            )
        )
    return issues
