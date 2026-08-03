"""TC-EV030-006 / T3.1+T3.2 — VAA/TCA decode residual pin (#820).

T3.1 snapped pre-deepen counts (VAA=13, TCA=14). T3.2 structured field decode
shrunk official peers to the counts below; keep this pin current.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tac2iwxxm.decode import decode_tac

ANNEX3 = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"

# Post–T3.2 counts (structured LABEL: fields). VAA keeps AHL bulletin residual.
_BASELINE: tuple[tuple[str, str, int], ...] = (
    ("vaa_a7_2", "VAA", 1),
    ("tca_a2_2", "TCA", 0),
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
    """Residual count pin after structured field decode (T3.2)."""
    tac = (ANNEX3 / f"{stem}.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product=product)
    texts = [r.text.strip() for r in result.residuals if r.text and r.text.strip()]
    assert len(texts) == expected_residuals, (
        f"{stem}: residual count {len(texts)} != pin {expected_residuals}; "
        "update t3.1/t3.2 reports + this pin when intentional"
    )
    assert all(t for t in texts)
