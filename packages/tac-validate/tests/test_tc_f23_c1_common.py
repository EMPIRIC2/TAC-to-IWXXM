"""F23 / C1 — common-rule fixture seeds (TC-F23-004 / matrix C1).

HARD theme C1 from sigmet-research-catalog.md (#733/#739 common table).
T4.3 seeds TAC fixtures where lint applies (reportStatus / nilReasons /
one-report / COR ban). CRS attrs, translationFailedTAC, and COLLECT packing
remain convert-only — encode + assertions land with T4.4 (F20 C1 pattern).
"""

from __future__ import annotations

from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"

_C1_ACCEPT = (
    "accept/sigmet_c1_normal.tac",
    "accept/sigmet_c1_cnl.tac",
    "accept/sigmet_c1_stnr.tac",
    "accept/sigmet_c1_multi_report.tac",
    "accept/sigmet_c1_va_normal.tac",
    "accept/sigmet_c1_va_no_va_exp.tac",
    "accept/sigmet_c1_va_cnl_fir_moved.tac",
)

_C1_NEGATIVE = ("negative/sigmet/c1_cor_not_allowed.tac",)

# Convert-only (no TAC lint surface) — documented for T4.4 matrix deferral.
_C1_CONVERT_ONLY = (
    "2-D CRS attrs (srsName / srsDimension / axisLabels)",
    "translationFailedTAC",
    "COLLECT packing / code-list URIs",
)


def test_c1_sigmet_fixture_seeds_present() -> None:
    for rel in _C1_ACCEPT + _C1_NEGATIVE:
        path = FIXTURES / rel
        assert path.is_file(), f"missing C1 fixture: {path}"
        assert path.read_text(encoding="utf-8").strip(), f"empty C1 fixture: {path}"


def test_c1_convert_only_deferral_documented() -> None:
    assert len(_C1_CONVERT_ONLY) >= 3
