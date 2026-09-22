"""TC-EVDOC-008: ruff pydocstyle (D) is enabled for ADR-048 trees."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ruff_toml_selects_pydocstyle_d() -> None:
    """Root ruff.toml enables the D (pydocstyle) rule group."""
    text = (ROOT / "ruff.toml").read_text(encoding="utf-8")
    assert '"D"' in text or "'D'" in text or "D," in text or 'D"' in text
    assert "pydocstyle" in text
    assert 'convention = "numpy"' in text


def test_ruff_excludes_generated_xsd() -> None:
    """Generated xsdata trees stay outside the D gate."""
    text = (ROOT / "ruff.toml").read_text(encoding="utf-8")
    assert "iwxxm_xsd" in text
