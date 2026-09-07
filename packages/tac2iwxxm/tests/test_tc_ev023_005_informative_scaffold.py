"""TC-EV023-005 scaffold (T0.3) - informative Amd79 marker + vendor path gate.

Full TAC→2025-2→XSD+SCH cases land in T5.1 and use
``@pytest.mark.xfail(strict=False)`` so soft failures do not hard-fail PR CI (E23-T4=2).
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_AMD79 = _REPO / "vendor" / "schemas" / "iwxxm-translation" / "Amd79-80-2023"

pytestmark = pytest.mark.iwxxm_translation_informative


@pytest.mark.parametrize(
    "rel",
    [
        "metar",
        "taf",
        "volcanic-ash-advisory",
        "tropical-cyclone-advisory",
    ],
)
def test_tc_ev023_005_amd79_product_trees_present(rel: str) -> None:
    """Vendor tip has METAR/SPECI, TAF, VAA, TCA trees (no SIGMET/AIRMET)."""
    path = _AMD79 / rel
    assert path.is_dir(), f"missing Amd79 tree: {path}"
    tacs = list(path.glob("*.tac"))
    assert tacs, f"no .tac fixtures under {path}"


def test_tc_ev023_005_nsc_seed_present() -> None:
    """P0/P1 seed cited by theme map - EFHK SPECI NSC."""
    seed = _AMD79 / "metar" / "EFHK-290020Z.tac"
    assert seed.is_file()
    text = seed.read_text(encoding="utf-8")
    assert "NSC" in text
