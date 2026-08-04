"""TC-EV032-003 — #835 catalog promote A6-2-TC → wmoPass (S040 / EV-032 T1.4)."""

from __future__ import annotations

from pathlib import Path

CATALOG = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/examplesCatalog.ts"
FIXTURE_GAPS = Path(__file__).resolve().parents[3] / "apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md"


def test_tc_ev032_003_catalog_wmo_pass() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    start = text.index("id: 'sigmet_a6_2_tc'")
    end = text.index("},", start)
    block = text[start:end]
    assert "wmoPass: true" in block
    assert "wmoReference: true" not in block
    assert "wmoSeed: 'sigmet-A6-2-TC'" in block


def test_tc_ev032_003_fixture_gaps_wmo_pass() -> None:
    text = FIXTURE_GAPS.read_text(encoding="utf-8")
    assert "sigmet-A6-2-TC" in text
    assert "wmoPass" in text
    assert "#835" in text
