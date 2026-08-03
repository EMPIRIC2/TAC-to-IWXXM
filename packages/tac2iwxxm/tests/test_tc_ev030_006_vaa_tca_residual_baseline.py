"""TC-EV030-006 / T3.1 — VAA/TCA decode residual baseline (#820).

Pins residual counts for official peers before T3.2 structured decode.
``allow_any`` remains in ``wmo_decode_residual_allowlist`` until T3.3 shrink.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tac2iwxxm.decode import decode_tac

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

# Exact counts from S037 T3.1 snapshot (2026-08-03) — update when T3.2 shrinks.
_BASELINE: tuple[tuple[str, str, int], ...] = (
    ("vaa_a7_2", "VAA", 13),
    ("tca_a2_2", "TCA", 14),
)


@pytest.mark.parametrize(
    ("stem", "product", "expected_residuals"),
    _BASELINE,
    ids=[s[0] for s in _BASELINE],
)
def test_tc_ev030_006_baseline_residual_count(
    stem: str,
    product: str,
    expected_residuals: int,
) -> None:
    """Baseline inventory — residual count must match T3.1 snapshot until T3.2."""
    tac = (ANNEX3 / f"{stem}.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product=product)
    texts = [r.text.strip() for r in result.residuals if r.text and r.text.strip()]
    assert len(texts) == expected_residuals, (
        f"{stem}: residual count {len(texts)} != baseline {expected_residuals}; "
        "update t3.1-vaa-tca-residual-baseline.md + this pin when intentional"
    )
    assert all(t for t in texts)
