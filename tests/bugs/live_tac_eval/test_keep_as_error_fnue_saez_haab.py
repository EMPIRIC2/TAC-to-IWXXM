"""Keep-as-error guards for FNUE / SAEZ / HAAB live residuals (#1496-#1498).

Disposition: leave lint severity as **error**. Do not soften, remap profiles,
widen the observation-time detector, or invent product-rules for these shapes.

| Issue | Station | Keep-error codes |
|-------|---------|------------------|
| #1496 | FNUE all-solidus | `INVALID_WIND` (+ `MISSING_TEMP_DEWPOINT`) |
| #1497 | SAEZ `Z0Z` garble | `MISSING_OBS_TIME` |
| #1498 | HAAB omit trailing `Z` | `MISSING_OBS_TIME` + `INVALID_VISIBILITY` (+ `INVALID_WIND` when `KTKT`) |

Out of scope: global `/////KT` → info; detector widen for `Z0Z` / bare `ddhhmm`.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tests.bugs.live_tac_eval.helpers import assert_has_code, lint_annex3

# #1496 — FNUE (Luena) all-solidus AUTO / outage feed.
_FNUE_ALL_SOLIDUS = "METAR FNUE 010100Z AUTO /////KT //// ////// ///// Q////"

# #1497 — SAEZ (Ezeiza) garbled observation time token `…Z0Z`.
_SAEZ_Z0Z = "METAR SAEZ 010210Z0Z 09003KT CAVOK 16/15 Q1011 NOSIG"

# #1498 — HAAB (Addis Ababa) observation time missing trailing Z.
_HAAB_OMIT_Z_KTKT = "METAR HAAB 011400 09012KTKT CAVOK 22/01 Q1027 NOSIG"
_HAAB_OMIT_Z = "METAR HAAB 011000 13010KT CAVOK 22/01 Q1027 NOSIG"

# (case_id, issue, icao, tac, expected_error_codes)
_KEEP_AS_ERROR_CASES: list[tuple[str, str, str, str, tuple[str, ...]]] = [
    (
        "fnue_all_solidus_invalid_wind",
        "1496",
        "FNUE",
        _FNUE_ALL_SOLIDUS,
        ("INVALID_WIND", "MISSING_TEMP_DEWPOINT"),
    ),
    (
        "saez_z0z_missing_obs_time",
        "1497",
        "SAEZ",
        _SAEZ_Z0Z,
        ("MISSING_OBS_TIME",),
    ),
    (
        "haab_omit_z_ktkt",
        "1498",
        "HAAB",
        _HAAB_OMIT_Z_KTKT,
        ("MISSING_OBS_TIME", "INVALID_VISIBILITY", "INVALID_WIND"),
    ),
    (
        "haab_omit_z",
        "1498",
        "HAAB",
        _HAAB_OMIT_Z,
        ("MISSING_OBS_TIME", "INVALID_VISIBILITY"),
    ),
]


@pytest.mark.parametrize(
    ("case_id", "issue", "icao", "tac", "codes"),
    _KEEP_AS_ERROR_CASES,
    ids=[row[0] for row in _KEEP_AS_ERROR_CASES],
)
def test_fnue_saez_haab_keep_as_error(
    case_id: str,
    issue: str,
    icao: str,
    tac: str,
    codes: tuple[str, ...],
) -> None:
    """Regional keep-error samples must remain severity error under annex3."""
    del case_id, issue  # parametrize id / ticket trace only
    report = lint_annex3(tac, product="METAR", icao=icao)
    for code in codes:
        assert_has_code(report, code, severity="error")
