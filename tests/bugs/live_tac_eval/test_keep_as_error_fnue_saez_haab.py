"""Keep-as-error guards for FNUE / SAEZ / HAAB live residuals (#1496-#1498).

Disposition: leave lint severity as **error**. Do not soften, remap profiles,
widen the observation-time detector, or invent product-rules for these shapes.

| Issue | Station | Keep-error codes |
|-------|---------|------------------|
| #1496 | FNUE all-solidus | `INVALID_WIND` (+ `MISSING_TEMP_DEWPOINT`) |
| #1497 | SAEZ `Z0Z` garble | `MISSING_OBS_TIME` |
| #1498 | HAAB omit trailing `Z` | `MISSING_OBS_TIME` + `INVALID_VISIBILITY` (+ `INVALID_WIND` when `KTKT`) |

Out of scope: global `/////KT` → info; detector widen for `Z0Z` / bare `ddhhmm`.

Combinatorial matrix (evolve-auto):
- Guard success: residual TAC keeps listed codes at severity error.
- Guard failure / no false keep: clean station TAC must not raise those codes.
- Validation fail: empty / non-METAR / wrong-product rejected with errors.
- Validation pass: well-formed station METAR has no error-severity issues.
- Mutation: N/A (lint read/query only; no create/update/delete surface).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tests.bugs.live_tac_eval.helpers import (
    assert_absent_codes,
    assert_has_code,
    assert_no_error_severity,
    issue_codes,
    lint_annex3,
)

# #1496 — FNUE (Luena) all-solidus AUTO / outage feed.
_FNUE_ALL_SOLIDUS = "METAR FNUE 010100Z AUTO /////KT //// ////// ///// Q////"

# #1497 — SAEZ (Ezeiza) garbled observation time token `…Z0Z`.
_SAEZ_Z0Z = "METAR SAEZ 010210Z0Z 09003KT CAVOK 16/15 Q1011 NOSIG"

# #1498 — HAAB (Addis Ababa) observation time missing trailing Z.
_HAAB_OMIT_Z_KTKT = "METAR HAAB 011400 09012KTKT CAVOK 22/01 Q1027 NOSIG"
_HAAB_OMIT_Z = "METAR HAAB 011000 13010KT CAVOK 22/01 Q1027 NOSIG"

# Well-formed station METARs (validation pass / no false keep).
_FNUE_CLEAN = "METAR FNUE 010100Z 09010KT CAVOK 22/15 Q1013 NOSIG"
_SAEZ_CLEAN = "METAR SAEZ 010210Z 09003KT CAVOK 16/15 Q1011 NOSIG"
_HAAB_CLEAN = "METAR HAAB 011400Z 13010KT CAVOK 22/01 Q1027 NOSIG"

# Codes the keep-error tickets pin (must not appear on clean TAC).
_FNUE_KEEP = ("INVALID_WIND", "MISSING_TEMP_DEWPOINT")
_SAEZ_KEEP = ("MISSING_OBS_TIME",)
_HAAB_KEEP_KTKT = ("MISSING_OBS_TIME", "INVALID_VISIBILITY", "INVALID_WIND")
_HAAB_KEEP = ("MISSING_OBS_TIME", "INVALID_VISIBILITY")

# (case_id, issue, icao, tac, expected_error_codes)
_KEEP_AS_ERROR_CASES: list[tuple[str, str, str, str, tuple[str, ...]]] = [
    (
        "fnue_all_solidus_invalid_wind",
        "1496",
        "FNUE",
        _FNUE_ALL_SOLIDUS,
        _FNUE_KEEP,
    ),
    (
        "saez_z0z_missing_obs_time",
        "1497",
        "SAEZ",
        _SAEZ_Z0Z,
        _SAEZ_KEEP,
    ),
    (
        "haab_omit_z_ktkt",
        "1498",
        "HAAB",
        _HAAB_OMIT_Z_KTKT,
        _HAAB_KEEP_KTKT,
    ),
    (
        "haab_omit_z",
        "1498",
        "HAAB",
        _HAAB_OMIT_Z,
        _HAAB_KEEP,
    ),
]

# Clean station x keep-code set that must stay absent (no false keep).
_NO_FALSE_KEEP_CASES: list[tuple[str, str, str, tuple[str, ...]]] = [
    ("fnue_clean_no_solidus_codes", "FNUE", _FNUE_CLEAN, _FNUE_KEEP),
    ("saez_clean_no_z0z_codes", "SAEZ", _SAEZ_CLEAN, _SAEZ_KEEP),
    ("haab_clean_no_omit_z_codes", "HAAB", _HAAB_CLEAN, _HAAB_KEEP_KTKT),
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
    """Guard success: regional keep-error samples stay severity error under annex3."""
    del case_id, issue  # parametrize id / ticket trace only
    report = lint_annex3(tac, product="METAR", icao=icao)
    for code in codes:
        assert_has_code(report, code, severity="error")


@pytest.mark.parametrize(
    ("case_id", "issue", "icao", "tac", "codes"),
    _KEEP_AS_ERROR_CASES,
    ids=[f"validation_fail_{row[0]}" for row in _KEEP_AS_ERROR_CASES],
)
def test_keep_error_samples_fail_validation(
    case_id: str,
    issue: str,
    icao: str,
    tac: str,
    codes: tuple[str, ...],
) -> None:
    """Validation fail: residual TAC yields at least one error-severity issue."""
    del case_id, issue, codes
    report = lint_annex3(tac, product="METAR", icao=icao)
    errors = [i for i in report.issues if i.severity == "error"]
    assert errors, (
        f"expected error-severity issues, got {[i.code for i in report.issues]}"
    )


@pytest.mark.parametrize(
    ("case_id", "icao", "tac", "forbidden"),
    _NO_FALSE_KEEP_CASES,
    ids=[row[0] for row in _NO_FALSE_KEEP_CASES],
)
def test_clean_station_metar_no_false_keep(
    case_id: str,
    icao: str,
    tac: str,
    forbidden: tuple[str, ...],
) -> None:
    """No false keep: well-formed station METAR must not raise ticket keep-codes."""
    del case_id
    report = lint_annex3(tac, product="METAR", icao=icao)
    assert_absent_codes(report, forbidden)
    assert_no_error_severity(report)


@pytest.mark.parametrize(
    ("case_id", "icao", "tac"),
    [
        ("fnue_clean_validation_pass", "FNUE", _FNUE_CLEAN),
        ("saez_clean_validation_pass", "SAEZ", _SAEZ_CLEAN),
        ("haab_clean_validation_pass", "HAAB", _HAAB_CLEAN),
    ],
)
def test_clean_station_metar_validation_pass(case_id: str, icao: str, tac: str) -> None:
    """Validation pass: clean FNUE/SAEZ/HAAB METAR has no error-severity lint."""
    del case_id
    report = lint_annex3(tac, product="METAR", icao=icao)
    assert_no_error_severity(report)


def test_wrong_station_override_still_keeps_content_codes() -> None:
    """Wrong-station ICAO override must not drop content-derived keep-error codes.

    Passing icao=SAEZ against the FNUE solidus body still yields INVALID_WIND
    from the TAC tokens (guard must not falsely clear on ICAO mismatch).
    """
    report = lint_annex3(_FNUE_ALL_SOLIDUS, product="METAR", icao="SAEZ")
    assert_has_code(report, "INVALID_WIND", severity="error")
    present = issue_codes(report)
    assert "INVALID_WIND" in present


def test_saez_clean_not_missing_obs_time() -> None:
    """Failure mode: proper SAEZ obs-time token must not raise MISSING_OBS_TIME."""
    report = lint_annex3(_SAEZ_CLEAN, product="METAR", icao="SAEZ")
    assert_absent_codes(report, ("MISSING_OBS_TIME",))


def test_haab_with_trailing_z_not_omit_z_codes() -> None:
    """Failure mode: HAAB with trailing Z must not raise omit-Z keep codes."""
    report = lint_annex3(_HAAB_CLEAN, product="METAR", icao="HAAB")
    assert_absent_codes(report, _HAAB_KEEP_KTKT)


def test_empty_tac_validation_fail() -> None:
    """Validation fail / missing fixture: empty TAC is rejected with errors."""
    report = lint_annex3("", product="METAR", icao="FNUE")
    errors = [i for i in report.issues if i.severity == "error"]
    assert errors, "empty TAC must not validate clean"


def test_non_metar_product_on_metar_body_stays_scoped() -> None:
    """Failure mode: linting residual METAR body as TAF must not claim METAR keep set.

    Product mismatch is a rejected / out-of-scope pairing for these guards —
    assert the FNUE solidus keep codes are not all present as a METAR keep hit.
    """
    report = lint_annex3(_FNUE_ALL_SOLIDUS, product="TAF", icao="FNUE")
    present = issue_codes(report)
    # Either errors exist (rejected) or the METAR keep pair is incomplete.
    metar_keep_hit = all(code in present for code in _FNUE_KEEP)
    errors = [i for i in report.issues if i.severity == "error"]
    assert errors or not metar_keep_hit, (
        "TAF product on FNUE solidus METAR must not pass as a METAR keep-error hit"
    )


def test_fnue_solidus_not_only_saez_keep_code() -> None:
    """Cross-ticket: FNUE solidus must keep INVALID_WIND, not SAEZ-only MISSING_OBS_TIME."""
    report = lint_annex3(_FNUE_ALL_SOLIDUS, product="METAR", icao="FNUE")
    assert_has_code(report, "INVALID_WIND", severity="error")
    # SAEZ-only signature would be MISSING_OBS_TIME without INVALID_WIND — blocked above.
